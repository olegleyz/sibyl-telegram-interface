"""Lambda handler for setting up the Telegram webhook."""

import json
import logging
from typing import Dict, Any

from ..telegram.bot import TelegramBot
from ..utils.ssm import get_bot_token
from ..utils import cfnresponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> None:
    """Handle webhook setup as a CloudFormation custom resource."""
    
    # Validate event structure early
    if not isinstance(event, dict):
        logger.error(f"Invalid event type: {type(event)}")
        return
        
    request_type = event.get('RequestType')
    if not request_type:
        logger.error("No RequestType in event")
        return
        
    logger.info(f"Processing {request_type} request")
    
    try:
        if request_type in ['Create', 'Update']:
            # Get the function URL from the event
            properties = event.get('ResourceProperties', {})
            function_url = properties.get('FunctionUrl')
            
            if not function_url:
                error_message = "FunctionUrl not provided in ResourceProperties"
                logger.error(error_message)
                cfnresponse.send(event, context, cfnresponse.FAILED, {
                    'Error': error_message
                })
                return
            
            try:
                # Get bot token and initialize bot
                bot_token = get_bot_token()
                bot = TelegramBot(bot_token)
                
                # Set up webhook
                response = bot.set_webhook(function_url)
                logger.info(f"Webhook setup response: {response}")
                
                if not response.get('ok'):
                    error_message = response.get('description', 'Unknown error')
                    if 'invalid token' in str(response).lower():
                        error_message = (
                            "ERROR: The bot token stored in SSM Parameter Store is invalid. "
                            "Please update it with a valid token."
                        )
                    logger.error(error_message)
                    cfnresponse.send(event, context, cfnresponse.FAILED, {
                        'Error': error_message
                    })
                    return
                
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {
                    'WebhookUrl': function_url,
                    'SetupResponse': response
                })
                
            except ValueError as e:
                error_message = str(e)
                logger.error(f"Value Error: {error_message}")
                cfnresponse.send(event, context, cfnresponse.FAILED, {
                    'Error': error_message
                })
                
        elif request_type == 'Delete':
            # Always respond with success for Delete operations
            logger.info("Processing Delete request")
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"Unexpected error: {error_message}")
        cfnresponse.send(event, context, cfnresponse.FAILED, {
            'Error': error_message
        })
