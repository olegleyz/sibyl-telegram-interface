"""Main Lambda handler for processing Telegram webhook requests."""

import json
from typing import Dict, Any
from aws_lambda_powertools import Logger
from pydantic import ValidationError

from ..telegram.bot import TelegramBot
from ..telegram.models import TelegramMessage
from ..utils.ssm import get_bot_token

logger = Logger()

@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle incoming Telegram webhook requests."""
    try:
        # Extract request IP and validate
        request_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp')
        bot = TelegramBot(get_bot_token())
        
        if not request_ip or not bot.validate_telegram_ip(request_ip):
            logger.warning(f"Invalid request IP: {request_ip}")
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Forbidden'})
            }

        # Parse and validate the incoming message
        body = json.loads(event.get('body', '{}'))
        message = TelegramMessage(
            message=body.get('message', {}),
            user_id=body.get('message', {}).get('from', {}).get('id'),
            chat_id=body.get('message', {}).get('chat', {}).get('id')
        )

        if not message.validate_message_length():
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Message too long'})
            }

        # TODO: Call backend API using generated client
        # Process the message and get response from backend
        response_text = "Message received and processed"

        # Send response back to Telegram
        telegram_response = bot.send_message(message.chat_id, response_text)

        return {
            'statusCode': 200,
            'body': json.dumps(telegram_response)
        }

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid message format'})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
