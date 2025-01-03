"""Process Telegram messages from SQS queue."""

import json
from typing import Dict, Any
import boto3
from botocore.config import Config

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parameters import get_parameter

from ..telegram.bot import TelegramBot
from ..telegram.models import TelegramMessage
from ..config.settings import BOT_TOKEN_PARAM_PATH

# Configure boto3 with performance optimizations
boto_config = Config(
    connect_timeout=2,
    read_timeout=2,
    parameter_validation=False,  # Skip parameter validation for speed
    retries={'max_attempts': 2}  # Reduce retry attempts
)

# Initialize clients outside handler for connection reuse
ssm_client = boto3.client('ssm', config=boto_config)
logger = Logger()

# Cache for bot token
_BOT_TOKEN = None

def get_cached_bot_token() -> str:
    """Get bot token with caching."""
    global _BOT_TOKEN
    if _BOT_TOKEN is None:
        _BOT_TOKEN = get_parameter(BOT_TOKEN_PARAM_PATH, decrypt=True)
    return _BOT_TOKEN

@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Process messages from SQS queue."""
    try:
        # Get bot token once and reuse
        bot_token = get_cached_bot_token()
        bot = TelegramBot(bot_token)
        
        # Process all messages in batch
        for record in event['Records']:
            process_message(bot, json.loads(record['body']))
            
        return {'statusCode': 200}
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {'statusCode': 500}

def process_message(bot: TelegramBot, message_data: Dict[str, Any]) -> None:
    """Process a single message from the queue."""
    try:
        # Reconstruct message without validation for speed
        message = message_data['message']
        chat_id = message['chat_id']
        
        # Quick response
        bot.send_message(chat_id, "Message processed")
        
    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}")
        # Re-raise to trigger SQS retry
        raise
