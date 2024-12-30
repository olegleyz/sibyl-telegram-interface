"""Configuration settings for the application."""

import os

# SSM Parameter paths
BOT_TOKEN_PARAM_PATH = "/sibyl/telegram/bot-token"

# Telegram settings
TELEGRAM_API_BASE = "https://api.telegram.org"
MAX_MESSAGE_LENGTH = 4096

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
