"""Sibyl Core API service wrapper."""

from typing import Optional, Dict, Any
import os
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from sibyl_core_sdk import Configuration, ApiClient
from sibyl_core_sdk.api.default_api import DefaultApi
from sibyl_core_sdk.models import UsersPostRequest
from ..config import settings


class SibylCoreService:
    """Service wrapper for Sibyl Core APIs."""

    def __init__(self):
        """Initialize Sibyl Core service."""
        configuration = Configuration()
        configuration.host = os.getenv("API_ENDPOINT")
        
        # Initialize AWS credentials
        self.region = os.getenv("AWS_REGION", "us-east-1")
        aws_session = boto3.Session()
        credentials = aws_session.get_credentials()
        self.credentials = credentials.get_frozen_credentials()
        
        # Create API client with custom auth
        api_client = ApiClient(configuration=configuration)
        api_client.authentications = {
            'AWS_IAM': lambda x: self._sign_request(x)
        }
        self.api = DefaultApi(api_client=api_client)

    def _sign_request(self, request: AWSRequest) -> None:
        """Sign request with SigV4.
        
        Args:
            request: Request to sign
        """
        SigV4Auth(
            self.credentials, 
            "execute-api",  # AWS service name for API Gateway
            self.region
        ).add_auth(request)

    def create_user(self, telegram_id: int, name: str) -> Dict[str, Any]:
        """Create a new user.
        
        Args:
            telegram_id: Telegram user ID
            name: User's name
            
        Returns:
            Dict containing the created user information
        """
        request = UsersPostRequest(
            telegram_id=telegram_id,
            name=name
        )
        return self.api.users_post(users_post_request=request)

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by UUID.
        
        Args:
            user_id: User UUID
            
        Returns:
            Dict containing user information if found, None otherwise
        """
        try:
            return self.api.users_id_get(id=user_id)
        except Exception:  # Replace with specific exception from SDK
            return None

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            Dict containing user information if found, None otherwise
        """
        try:
            return self.api.users_telegram_telegram_id_get(telegram_id=str(telegram_id))
        except Exception:  # Replace with specific exception from SDK
            return None

    def update_user(self, user_id: str, telegram_id: int, name: str) -> Optional[Dict[str, Any]]:
        """Update user information.
        
        Args:
            user_id: User UUID
            telegram_id: Telegram user ID
            name: User's name
            
        Returns:
            Dict containing updated user information if successful, None otherwise
        """
        request = UsersPostRequest(
            telegram_id=telegram_id,
            name=name
        )
        try:
            return self.api.users_id_put(id=user_id, users_post_request=request)
        except Exception:  # Replace with specific exception from SDK
            return None

    def delete_user(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            True if user was deleted successfully, False otherwise
        """
        try:
            self.api.users_id_delete(id=user_id)
            return True
        except Exception:  # Replace with specific exception from SDK
            return False