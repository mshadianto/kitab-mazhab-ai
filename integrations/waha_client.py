"""
WAHA (WhatsApp HTTP API) Integration
Handler untuk menerima dan mengirim pesan WhatsApp
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WAHAMessage:
    """Struktur pesan WAHA"""
    id: str
    from_number: str
    to_number: str
    body: str
    timestamp: datetime
    is_group: bool = False
    group_id: Optional[str] = None
    quoted_message: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    raw_data: Dict = field(default_factory=dict)


@dataclass
class WAHASession:
    """Session information"""
    name: str
    status: str
    phone_number: Optional[str] = None


class WAHAClient:
    """
    Client untuk berinteraksi dengan WAHA API
    """
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        session: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.api_url = (api_url or os.getenv("WAHA_API_URL", "")).rstrip('/')
        self.session = session or os.getenv("WAHA_SESSION", "default")
        self.api_key = api_key or os.getenv("WAHA_API_KEY", "")
        
        if not self.api_url:
            raise ValueError("WAHA_API_URL is required")
        
        self.headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            self.headers["X-Api-Key"] = self.api_key
        
        logger.info(f"WAHAClient initialized for {self.api_url} with session {self.session}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to WAHA API"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json() if response.text else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"WAHA API error: {e}")
            raise
    
    # Session Management
    def get_sessions(self) -> List[WAHASession]:
        """Get all sessions"""
        result = self._make_request("GET", "/api/sessions")
        return [
            WAHASession(
                name=s.get("name", ""),
                status=s.get("status", "UNKNOWN"),
                phone_number=s.get("me", {}).get("id", "").split("@")[0] if s.get("me") else None
            )
            for s in result
        ]
    
    def get_session_status(self) -> Dict:
        """Get current session status"""
        return self._make_request("GET", f"/api/sessions/{self.session}")
    
    def start_session(self) -> Dict:
        """Start a session"""
        return self._make_request("POST", f"/api/sessions/{self.session}/start")
    
    def stop_session(self) -> Dict:
        """Stop a session"""
        return self._make_request("POST", f"/api/sessions/{self.session}/stop")
    
    # Messaging
    def send_text(
        self,
        to: str,
        text: str,
        reply_to: Optional[str] = None
    ) -> Dict:
        """
        Send text message
        
        Args:
            to: Phone number with country code (e.g., 6281234567890)
            text: Message text
            reply_to: Message ID to reply to (optional)
        """
        # Ensure proper format
        chat_id = to if "@" in to else f"{to}@c.us"
        
        data = {
            "chatId": chat_id,
            "text": text,
            "session": self.session
        }
        
        if reply_to:
            data["reply_to"] = reply_to
        
        return self._make_request("POST", "/api/sendText", data=data)
    
    def send_text_with_formatting(
        self,
        to: str,
        text: str,
        reply_to: Optional[str] = None
    ) -> Dict:
        """Send text with WhatsApp formatting"""
        # WhatsApp supports: *bold*, _italic_, ~strikethrough~, ```code```
        chat_id = to if "@" in to else f"{to}@c.us"
        
        data = {
            "chatId": chat_id,
            "text": text,
            "session": self.session
        }
        
        if reply_to:
            data["reply_to"] = reply_to
        
        return self._make_request("POST", "/api/sendText", data=data)
    
    def send_image(
        self,
        to: str,
        image_url: str,
        caption: Optional[str] = None
    ) -> Dict:
        """Send image message"""
        chat_id = to if "@" in to else f"{to}@c.us"
        
        data = {
            "chatId": chat_id,
            "file": {
                "url": image_url
            },
            "caption": caption or "",
            "session": self.session
        }
        
        return self._make_request("POST", "/api/sendImage", data=data)
    
    def send_document(
        self,
        to: str,
        document_url: str,
        filename: str,
        caption: Optional[str] = None
    ) -> Dict:
        """Send document"""
        chat_id = to if "@" in to else f"{to}@c.us"
        
        data = {
            "chatId": chat_id,
            "file": {
                "url": document_url,
                "filename": filename
            },
            "caption": caption or "",
            "session": self.session
        }
        
        return self._make_request("POST", "/api/sendFile", data=data)
    
    def send_buttons(
        self,
        to: str,
        text: str,
        buttons: List[Dict[str, str]],
        footer: Optional[str] = None
    ) -> Dict:
        """
        Send message with buttons (if supported)
        
        Args:
            buttons: List of {"id": "btn_id", "text": "Button Text"}
        """
        chat_id = to if "@" in to else f"{to}@c.us"
        
        data = {
            "chatId": chat_id,
            "text": text,
            "buttons": buttons,
            "footer": footer or "",
            "session": self.session
        }
        
        return self._make_request("POST", "/api/sendButtons", data=data)
    
    def send_list(
        self,
        to: str,
        text: str,
        button_text: str,
        sections: List[Dict],
        title: Optional[str] = None,
        footer: Optional[str] = None
    ) -> Dict:
        """
        Send list message
        
        Args:
            sections: [{"title": "Section", "rows": [{"id": "1", "title": "Option", "description": "Desc"}]}]
        """
        chat_id = to if "@" in to else f"{to}@c.us"
        
        data = {
            "chatId": chat_id,
            "text": text,
            "title": title or "",
            "buttonText": button_text,
            "sections": sections,
            "footer": footer or "",
            "session": self.session
        }
        
        return self._make_request("POST", "/api/sendList", data=data)
    
    def send_reaction(self, to: str, message_id: str, emoji: str) -> Dict:
        """Send reaction to a message"""
        chat_id = to if "@" in to else f"{to}@c.us"
        
        data = {
            "chatId": chat_id,
            "messageId": message_id,
            "reaction": emoji,
            "session": self.session
        }
        
        return self._make_request("POST", "/api/reaction", data=data)
    
    def mark_as_read(self, chat_id: str, message_ids: List[str]) -> Dict:
        """Mark messages as read"""
        data = {
            "chatId": chat_id,
            "messageIds": message_ids,
            "session": self.session
        }
        
        return self._make_request("POST", "/api/markAsRead", data=data)
    
    def set_typing(self, to: str, typing: bool = True) -> Dict:
        """Set typing indicator"""
        chat_id = to if "@" in to else f"{to}@c.us"
        
        endpoint = "/api/startTyping" if typing else "/api/stopTyping"
        data = {
            "chatId": chat_id,
            "session": self.session
        }
        
        return self._make_request("POST", endpoint, data=data)
    
    # Webhook Configuration
    def set_webhook(self, webhook_url: str, events: Optional[List[str]] = None) -> Dict:
        """Configure webhook for receiving messages"""
        default_events = [
            "message",
            "message.reaction",
            "session.status"
        ]
        
        data = {
            "url": webhook_url,
            "events": events or default_events,
            "session": self.session
        }
        
        return self._make_request("PUT", f"/api/sessions/{self.session}/webhooks", data=data)
    
    def get_webhooks(self) -> Dict:
        """Get configured webhooks"""
        return self._make_request("GET", f"/api/sessions/{self.session}/webhooks")


class WAHAWebhookParser:
    """Parser untuk webhook events dari WAHA"""
    
    @staticmethod
    def parse_message(payload: Dict) -> Optional[WAHAMessage]:
        """Parse incoming message webhook"""
        try:
            event = payload.get("event", "")
            
            if event != "message":
                return None
            
            data = payload.get("payload", {})
            
            # Skip status messages
            if data.get("fromMe", False):
                return None
            
            msg_id = data.get("id", "")
            from_number = data.get("from", "").replace("@c.us", "").replace("@g.us", "")
            to_number = data.get("to", "").replace("@c.us", "").replace("@g.us", "")
            
            # Check if group
            is_group = "@g.us" in data.get("from", "")
            group_id = data.get("from", "") if is_group else None
            
            # Get message body
            body = ""
            if "body" in data:
                body = data["body"]
            elif "text" in data:
                body = data["text"]
            elif data.get("type") == "chat":
                body = data.get("body", "")
            
            # Parse timestamp
            timestamp = datetime.fromtimestamp(
                data.get("timestamp", 0)
            ) if data.get("timestamp") else datetime.now()
            
            # Check for quoted message
            quoted = None
            if data.get("quotedMsg"):
                quoted = data["quotedMsg"].get("body", "")
            
            # Check for media
            media_url = None
            media_type = None
            if data.get("hasMedia"):
                media_type = data.get("type", "")
                # Media URL might need to be fetched separately
            
            return WAHAMessage(
                id=msg_id,
                from_number=from_number,
                to_number=to_number,
                body=body.strip(),
                timestamp=timestamp,
                is_group=is_group,
                group_id=group_id,
                quoted_message=quoted,
                media_url=media_url,
                media_type=media_type,
                raw_data=data
            )
            
        except Exception as e:
            logger.error(f"Error parsing webhook: {e}")
            return None
    
    @staticmethod
    def is_valid_webhook(payload: Dict, secret: Optional[str] = None) -> bool:
        """Validate webhook signature if secret is configured"""
        if not secret:
            return True
        
        # WAHA might use different validation methods
        # Implement based on your WAHA configuration
        return True


class ConversationManager:
    """Manage conversation state and history"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict]] = {}
        self.user_states: Dict[str, Dict] = {}
    
    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a user"""
        return self.conversations.get(user_id, [])
    
    def add_message(self, user_id: str, role: str, content: str):
        """Add message to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            "role": role,
            "content": content
        })
        
        # Trim history
        if len(self.conversations[user_id]) > self.max_history * 2:
            self.conversations[user_id] = self.conversations[user_id][-self.max_history * 2:]
    
    def clear_history(self, user_id: str):
        """Clear conversation history"""
        if user_id in self.conversations:
            del self.conversations[user_id]
    
    def get_state(self, user_id: str) -> Dict:
        """Get user state"""
        return self.user_states.get(user_id, {})
    
    def set_state(self, user_id: str, state: Dict):
        """Set user state"""
        self.user_states[user_id] = state
    
    def update_state(self, user_id: str, **kwargs):
        """Update user state"""
        if user_id not in self.user_states:
            self.user_states[user_id] = {}
        self.user_states[user_id].update(kwargs)


# Singleton instances
_waha_client: Optional[WAHAClient] = None
_conversation_manager: Optional[ConversationManager] = None


def get_waha_client() -> WAHAClient:
    """Get or create WAHA client singleton"""
    global _waha_client
    if _waha_client is None:
        _waha_client = WAHAClient()
    return _waha_client


def get_conversation_manager() -> ConversationManager:
    """Get or create conversation manager singleton"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager


if __name__ == "__main__":
    # Test WAHA client
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    try:
        client = WAHAClient()
        
        # Test get sessions
        sessions = client.get_sessions()
        print("Sessions:")
        for s in sessions:
            print(f"  - {s.name}: {s.status} ({s.phone_number})")
        
        # Test session status
        status = client.get_session_status()
        print(f"\nSession status: {status}")
        
    except Exception as e:
        print(f"Error: {e}")
