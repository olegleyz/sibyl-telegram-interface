"""Handle incoming Telegram webhook requests."""

import json
from typing import Dict, Any

from aws_lambda_powertools import Logger
import boto3
import os

from ..telegram.bot import TelegramBot
from ..telegram.models import TelegramMessage
from ..utils.ssm import get_bot_token

logger = Logger()
sqs = boto3.client('sqs')

@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle incoming Telegram webhook requests."""
    try:
        # Extract request IP and validate
        request_ip = event.get("headers", {}).get("x-forwarded-for")
        request_port = event.get("headers", {}).get("x-forwarded-port")
        bot = TelegramBot(get_bot_token())
        
        if not request_ip or not bot.validate_telegram_ip(request_ip):
            logger.warning(f"Invalid request IP: {request_ip}")
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Forbidden'})
            }

        if not request_port or not bot.validate_telegram_port(request_port):
            logger.warning(f"Invalid request port: {request_port}")
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
            logger.warning(f"Message too long: {len(message)} characters")
            bot.send_message(message.chat_id, "Error: your message is too long.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Message too long'})
            }

        # Instead of processing here, send to SQS for async processing
        tg_process_queue_name = os.environ.get('SQS_QUEUE_URL')
        sqs.send_message(
            QueueUrl=tg_process_queue_name,
            MessageBody=json.dumps({
                'message': message.dict()
            })
        )

        # Immediately return success to Telegram
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'Message queued for processing'})
        }

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
