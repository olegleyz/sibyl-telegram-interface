"""Telegram data models."""

from typing import Dict, Any
from pydantic import BaseModel, Field
from ..config import settings

class TelegramMessage(BaseModel):
    """Model for validating Telegram messages."""
    
    message: Dict[str, Any] = Field(..., description="Telegram message object")
    user_id: int = Field(..., description="Telegram user ID")
    chat_id: int = Field(..., description="Telegram chat ID")

    @property
    def text_content(self) -> str:
        """Get the text content of the message."""
        return self.message.get('text', '')

    def validate_message_length(self, max_length: int = settings.MAX_MESSAGE_LENGTH) -> bool:
        """Validate the message length."""
        return len(self.text_content) <= max_length
