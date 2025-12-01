"""
Main Webhook Server untuk Kitab Imam Mazhab RAG AI
Flask server untuk menerima webhook dari WAHA dan memproses pesan
"""

import os
import sys
import logging
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime

from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.rag_engine import get_rag_engine
from core.agent import get_agent, KitabMazhabAgent
from integrations.waha_client import (
    get_waha_client,
    get_conversation_manager,
    WAHAWebhookParser,
    WAHAClient,
    ConversationManager
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global instances
agent: Optional[KitabMazhabAgent] = None
waha: Optional[WAHAClient] = None
conversation_mgr: Optional[ConversationManager] = None


def initialize_services():
    """Initialize all services"""
    global agent, waha, conversation_mgr
    
    logger.info("Initializing services...")
    
    # Initialize RAG engine and load knowledge base
    logger.info("Loading RAG engine...")
    rag = get_rag_engine()
    
    kb_path = Path(__file__).parent / "data" / "knowledge_base" / "kitab_mazhab.json"
    if kb_path.exists():
        doc_count = rag.load_knowledge_base(str(kb_path))
        logger.info(f"Loaded {doc_count} documents into RAG")
    else:
        logger.warning(f"Knowledge base not found at {kb_path}")
    
    # Initialize agent
    logger.info("Initializing AI agent...")
    agent = get_agent()
    
    # Initialize WAHA client
    logger.info("Initializing WAHA client...")
    try:
        waha = get_waha_client()
        logger.info("WAHA client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize WAHA client: {e}")
        waha = None
    
    # Initialize conversation manager
    conversation_mgr = get_conversation_manager()
    
    logger.info("All services initialized!")


def format_response_for_whatsapp(text: str, max_length: int = 4000) -> str:
    """Format response for WhatsApp, handling length limits"""
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length - 100] + "\n\n... _(pesan terpotong karena terlalu panjang)_"
    
    return text


def process_user_message(phone_number: str, message: str) -> str:
    """Process user message and generate response"""
    global agent, conversation_mgr
    
    # Handle special commands
    message_lower = message.lower().strip()
    
    # Greeting commands
    if message_lower in ["assalamualaikum", "salam", "halo", "hai", "hi", "hello", "start", "/start"]:
        return agent.get_greeting()
    
    # Help command
    if message_lower in ["help", "bantuan", "/help", "menu", "/menu", "?"]:
        return agent.get_help()
    
    # Reset conversation
    if message_lower in ["reset", "/reset", "ulang", "mulai ulang"]:
        conversation_mgr.clear_history(phone_number)
        return "✅ Percakapan telah direset.\n\nSilakan ajukan pertanyaan baru tentang kitab imam mazhab."
    
    # Process with agent
    history = conversation_mgr.get_history(phone_number)
    
    # Add user message to history
    conversation_mgr.add_message(phone_number, "user", message)
    
    try:
        # Get response from agent
        response = agent.process_message(message, history)
        
        # Add assistant response to history
        conversation_mgr.add_message(phone_number, "assistant", response.answer)
        
        # Format for WhatsApp
        formatted_response = format_response_for_whatsapp(response.answer)
        
        return formatted_response
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return "Maaf, terjadi kesalahan dalam memproses pertanyaan Anda. Silakan coba lagi. 🙏"


# Flask Routes

@app.route("/", methods=["GET"])
def home():
    """Home endpoint"""
    return jsonify({
        "status": "running",
        "service": "Kitab Imam Mazhab RAG AI",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health",
            "test": "/test"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    global agent, waha
    
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "agent": agent is not None,
            "waha": waha is not None,
            "rag": get_rag_engine().collection.count() > 0
        }
    }
    
    # Check WAHA connection
    if waha:
        try:
            sessions = waha.get_sessions()
            status["waha_sessions"] = len(sessions)
        except:
            status["waha_sessions"] = "error"
    
    return jsonify(status)


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Main webhook endpoint for WAHA
    Receives incoming messages and sends responses
    """
    global agent, waha, conversation_mgr
    
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({"status": "error", "message": "No payload"}), 400
        
        logger.info(f"Received webhook: {payload.get('event', 'unknown')}")
        
        # Parse the message
        message = WAHAWebhookParser.parse_message(payload)
        
        if not message:
            # Not a message event or from self
            return jsonify({"status": "ok", "message": "Ignored"})
        
        logger.info(f"Processing message from {message.from_number}: {message.body[:50]}...")
        
        # Skip if message is empty
        if not message.body.strip():
            return jsonify({"status": "ok", "message": "Empty message"})
        
        # Skip group messages (optional - remove if you want group support)
        if message.is_group:
            logger.info("Skipping group message")
            return jsonify({"status": "ok", "message": "Group message skipped"})
        
        # Process message
        phone_number = message.from_number
        user_message = message.body
        
        # Send typing indicator
        if waha:
            try:
                waha.set_typing(phone_number, True)
            except:
                pass
        
        # Generate response
        response_text = process_user_message(phone_number, user_message)
        
        # Stop typing
        if waha:
            try:
                waha.set_typing(phone_number, False)
            except:
                pass
        
        # Send response
        if waha:
            try:
                waha.send_text(phone_number, response_text, reply_to=message.id)
                logger.info(f"Response sent to {phone_number}")
            except Exception as e:
                logger.error(f"Failed to send response: {e}")
        
        return jsonify({
            "status": "ok",
            "message_processed": True,
            "from": phone_number
        })
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/test", methods=["POST"])
def test_message():
    """
    Test endpoint untuk menguji AI tanpa WAHA
    
    Body: {"message": "pertanyaan anda", "phone": "optional_phone"}
    """
    try:
        data = request.get_json()
        message = data.get("message", "")
        phone = data.get("phone", "test_user")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        response = process_user_message(phone, message)
        
        return jsonify({
            "status": "ok",
            "input": message,
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/send", methods=["POST"])
def send_message():
    """
    Endpoint untuk mengirim pesan via WAHA
    
    Body: {"to": "phone_number", "message": "text"}
    """
    global waha
    
    if not waha:
        return jsonify({"error": "WAHA not initialized"}), 500
    
    try:
        data = request.get_json()
        to = data.get("to", "")
        message = data.get("message", "")
        
        if not to or not message:
            return jsonify({"error": "Both 'to' and 'message' are required"}), 400
        
        result = waha.send_text(to, message)
        
        return jsonify({
            "status": "ok",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/sessions", methods=["GET"])
def get_sessions():
    """Get WAHA sessions"""
    global waha
    
    if not waha:
        return jsonify({"error": "WAHA not initialized"}), 500
    
    try:
        sessions = waha.get_sessions()
        return jsonify({
            "status": "ok",
            "sessions": [
                {
                    "name": s.name,
                    "status": s.status,
                    "phone": s.phone_number
                }
                for s in sessions
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stats", methods=["GET"])
def get_stats():
    """Get system statistics"""
    global conversation_mgr
    
    rag = get_rag_engine()
    
    return jsonify({
        "status": "ok",
        "stats": {
            "rag_documents": rag.collection.count(),
            "active_conversations": len(conversation_mgr.conversations) if conversation_mgr else 0,
            "timestamp": datetime.now().isoformat()
        }
    })


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run the Flask server"""
    initialize_services()
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    port = int(os.getenv("WEBHOOK_PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    run_server(host=host, port=port, debug=debug)
