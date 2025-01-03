"""Process Telegram messages from SQS queue."""

import json
from typing import Dict, Any

from aws_lambda_powertools import Logger

from ..telegram.bot import TelegramBot
from ..telegram.models import TelegramMessage
from ..utils.ssm import get_bot_token

logger = Logger()

@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Process messages from SQS queue."""
    try:
        for record in event['Records']:
            process_message(json.loads(record['body']))
        return {'statusCode': 200}
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {'statusCode': 500}

def process_message(message_data: Dict[str, Any]) -> None:
    """Process a single message from the queue."""
    try:
        # Initialize bot and reconstruct message
        bot = TelegramBot(get_bot_token())
        message = TelegramMessage(**message_data['message'])

        # Here you can perform time-consuming operations:
        # - Call external APIs
        # - Process complex computations
        # - Handle media
        # - Interact with databases
        response_text = "Your message has been processed"

        # Send response back to Telegram
        # If this fails, the message will stay in the queue and be retried
        bot.send_message(message.chat_id, response_text)
        
    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}")
        # Re-raise to trigger SQS retry
        raise
