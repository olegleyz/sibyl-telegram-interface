"""Service for handling Sibyl Core user operations."""

from typing import Optional, Dict, Any
from .sibyl_core import SibylCoreService


class UserService:
    """Service for managing Sibyl Core users."""

    def __init__(self, api_key: str):
        """Initialize the user service.
        
        Args:
            api_key: Sibyl Core API key
        """
        self.client = SibylCoreService()

    def create_user(self, telegram_id: int, name: str) -> Dict[str, Any]:
        """Create a new user.
        
        Args:
            telegram_id: Telegram user ID
            name: User's name
            
        Returns:
            Dict containing the created user information
        """
        return self.client.create_user(
            telegram_id=telegram_id,
            name=name
        )

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Sibyl Core user ID.
        
        Args:
            user_id: Sibyl Core user ID
            
        Returns:
            Dict containing user information if found, None otherwise
        """
        return self.client.get_user_by_id(user_id=user_id)

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by Telegram user ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            Dict containing user information if found, None otherwise
        """
        return self.client.get_user_by_telegram_id(telegram_id=telegram_id)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: Sibyl Core user ID
            
        Returns:
            True if user was deleted successfully, False otherwise
        """
        return self.client.delete_user(user_id=user_id)
