"""Telegram bot implementation."""

import ipaddress
import requests
from typing import Dict, Any
from ..config import settings

class TelegramBot:
    """Telegram bot class for handling message sending and webhook configuration."""
    
    def __init__(self, bot_token: str):
        """Initialize the bot with the given token."""
        self.bot_token = bot_token
        self.api_base_url = f"{settings.TELEGRAM_API_BASE}/bot{bot_token}"
        
        # Telegram IP ranges (should be updated periodically)
        self.telegram_ip_ranges = [
            '149.154.160.0/20',
            '91.108.4.0/22',
        ]
        self.telegram_ports = ("443", "80", "88", "8443")

    def validate_telegram_ip(self, ip_address: str) -> bool:
        """Validate if the IP address belongs to Telegram."""
        try:
            request_ip = ipaddress.ip_address(ip_address)
            return any(
                request_ip in ipaddress.ip_network(range_)
                for range_ in self.telegram_ip_ranges
            )
        except ValueError:
            return False

    def validate_telegram_port(self, port: str) -> bool:
        """Validate if the port belongs to Telegram."""
        return port in self.telegram_ports
        
    def send_message(self, chat_id: int, text: str) -> Dict[str, Any]:
        """Send a message to a chat."""
        url = f"{self.api_base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        return response.json()

    def set_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Set the webhook URL for the bot."""
        url = f"{self.api_base_url}/setWebhook"
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message"]
        }
        response = requests.post(url, json=payload)
        return response.json()
