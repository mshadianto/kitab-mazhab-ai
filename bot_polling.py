"""
Kitab Imam Mazhab RAG AI - Polling Mode
Tidak memerlukan webhook/ngrok - polling langsung ke WAHA API
"""

import os
import sys
import time
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Set
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.rag_engine import get_rag_engine
from core.agent import get_agent, KitabMazhabAgent
from integrations.waha_client import (
    get_waha_client,
    get_conversation_manager,
    WAHAClient,
    ConversationManager
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WAHAPollingBot:
    """
    Bot yang menggunakan polling untuk mengambil pesan dari WAHA
    Tidak memerlukan webhook/ngrok
    """
    
    def __init__(
        self,
        poll_interval: int = 3,  # seconds
        session: str = None
    ):
        self.poll_interval = poll_interval
        self.session = session or os.getenv("WAHA_SESSION", "WBSBPKH230")
        self.api_url = os.getenv("WAHA_API_URL", "").rstrip('/')
        self.api_key = os.getenv("WAHA_API_KEY", "")
        
        # Track processed messages
        self.processed_messages: Set[str] = set()
        self.last_check_time = datetime.now() - timedelta(minutes=5)
        
        # Initialize components
        self.agent: Optional[KitabMazhabAgent] = None
        self.waha: Optional[WAHAClient] = None
        self.conversation_mgr: Optional[ConversationManager] = None
        
        # Headers for API
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["X-Api-Key"] = self.api_key
    
    def initialize(self):
        """Initialize all components"""
        logger.info("=" * 50)
        logger.info("🕌 KITAB IMAM MAZHAB RAG AI - POLLING MODE")
        logger.info("=" * 50)
        
        # Initialize RAG
        logger.info("📚 Loading RAG engine...")
        rag = get_rag_engine()
        kb_path = Path(__file__).parent / "data" / "knowledge_base" / "kitab_mazhab.json"
        if kb_path.exists():
            doc_count = rag.load_knowledge_base(str(kb_path))
            logger.info(f"✅ Loaded {doc_count} documents into RAG")
        
        # Initialize Agent
        logger.info("🤖 Initializing AI agent...")
        self.agent = get_agent()
        logger.info("✅ Agent ready (Llama 3.3 70B)")
        
        # Initialize WAHA
        logger.info("📱 Initializing WAHA client...")
        self.waha = get_waha_client()
        logger.info(f"✅ WAHA connected to {self.api_url}")
        
        # Initialize conversation manager
        self.conversation_mgr = get_conversation_manager()
        
        logger.info("=" * 50)
        logger.info("✅ All services initialized!")
        logger.info(f"📡 Polling session: {self.session}")
        logger.info(f"⏱️  Poll interval: {self.poll_interval} seconds")
        logger.info("=" * 50)
    
    def get_chats(self):
        """Get list of chats"""
        try:
            url = f"{self.api_url}/api/{self.session}/chats"
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting chats: {e}")
            return []
    
    def get_messages(self, chat_id: str, limit: int = 10):
        """Get messages from a specific chat"""
        try:
            url = f"{self.api_url}/api/{self.session}/chats/{chat_id}/messages"
            params = {"limit": limit, "downloadMedia": False}
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    def send_message(self, to: str, text: str):
        """Send message via WAHA"""
        try:
            chat_id = to if "@" in to else f"{to}@c.us"
            url = f"{self.api_url}/api/sendText"
            data = {
                "chatId": chat_id,
                "text": text,
                "session": self.session
            }
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            return response.status_code == 200 or response.status_code == 201
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def send_seen(self, chat_id: str, message_id: str):
        """Mark message as seen"""
        try:
            url = f"{self.api_url}/api/sendSeen"
            data = {
                "chatId": chat_id,
                "messageId": message_id,
                "session": self.session
            }
            requests.post(url, headers=self.headers, json=data, timeout=10)
        except:
            pass
    
    def set_typing(self, chat_id: str, typing: bool = True):
        """Set typing indicator"""
        try:
            endpoint = "startTyping" if typing else "stopTyping"
            url = f"{self.api_url}/api/{endpoint}"
            data = {"chatId": chat_id, "session": self.session}
            requests.post(url, headers=self.headers, json=data, timeout=10)
        except:
            pass
    
    def process_message(self, phone_number: str, message: str) -> str:
        """Process user message and generate response"""
        message_lower = message.lower().strip()
        
        # Handle special commands
        if message_lower in ["assalamualaikum", "salam", "halo", "hai", "hi", "hello", "start", "/start"]:
            return self.agent.get_greeting()
        
        if message_lower in ["help", "bantuan", "/help", "menu", "/menu", "?"]:
            return self.agent.get_help()
        
        if message_lower in ["reset", "/reset", "ulang", "mulai ulang"]:
            self.conversation_mgr.clear_history(phone_number)
            return "✅ Percakapan telah direset.\n\nSilakan ajukan pertanyaan baru tentang kitab imam mazhab."
        
        # Process with agent
        history = self.conversation_mgr.get_history(phone_number)
        self.conversation_mgr.add_message(phone_number, "user", message)
        
        try:
            response = self.agent.process_message(message, history)
            self.conversation_mgr.add_message(phone_number, "assistant", response.answer)
            
            # Truncate if too long
            answer = response.answer
            if len(answer) > 4000:
                answer = answer[:3900] + "\n\n... _(pesan terpotong)_"
            
            return answer
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Maaf, terjadi kesalahan dalam memproses pertanyaan Anda. Silakan coba lagi. 🙏"
    
    def poll_messages(self):
        """Poll for new messages"""
        try:
            # Get all chats
            chats = self.get_chats()
            
            for chat in chats:
                chat_id = chat.get("id", "")
                
                # Skip groups (optional)
                if "@g.us" in chat_id:
                    continue
                
                # Get recent messages
                messages = self.get_messages(chat_id, limit=5)
                
                for msg in messages:
                    msg_id = msg.get("id", "")
                    
                    # Skip if already processed
                    if msg_id in self.processed_messages:
                        continue
                    
                    # Skip if from self
                    if msg.get("fromMe", False):
                        self.processed_messages.add(msg_id)
                        continue
                    
                    # Skip if too old (more than 5 minutes)
                    timestamp = msg.get("timestamp", 0)
                    if timestamp:
                        msg_time = datetime.fromtimestamp(timestamp)
                        if msg_time < self.last_check_time:
                            self.processed_messages.add(msg_id)
                            continue
                    
                    # Get message body
                    body = msg.get("body", "") or msg.get("text", "")
                    if not body.strip():
                        self.processed_messages.add(msg_id)
                        continue
                    
                    # Extract phone number
                    from_id = msg.get("from", chat_id)
                    phone = from_id.replace("@c.us", "").replace("@g.us", "")
                    
                    logger.info(f"📩 New message from {phone}: {body[:50]}...")
                    
                    # Mark as processed
                    self.processed_messages.add(msg_id)
                    
                    # Set typing indicator
                    self.set_typing(chat_id, True)
                    
                    # Process and respond
                    response = self.process_message(phone, body)
                    
                    # Stop typing
                    self.set_typing(chat_id, False)
                    
                    # Send response
                    if self.send_message(phone, response):
                        logger.info(f"✅ Response sent to {phone}")
                    else:
                        logger.error(f"❌ Failed to send response to {phone}")
                    
                    # Mark as seen
                    self.send_seen(chat_id, msg_id)
            
            # Cleanup old processed messages (keep last 1000)
            if len(self.processed_messages) > 1000:
                self.processed_messages = set(list(self.processed_messages)[-500:])
                
        except Exception as e:
            logger.error(f"Error polling messages: {e}")
    
    def run(self):
        """Main polling loop"""
        self.initialize()
        
        logger.info("")
        logger.info("🚀 Bot started! Listening for messages...")
        logger.info("   Press Ctrl+C to stop")
        logger.info("")
        
        try:
            while True:
                self.poll_messages()
                self.last_check_time = datetime.now() - timedelta(seconds=30)
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            logger.info("")
            logger.info("👋 Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise


def main():
    """Main entry point"""
    # Get configuration
    poll_interval = int(os.getenv("POLL_INTERVAL", "3"))
    session = os.getenv("WAHA_SESSION", "WBSBPKH230")
    
    # Create and run bot
    bot = WAHAPollingBot(poll_interval=poll_interval, session=session)
    bot.run()


if __name__ == "__main__":
    main()