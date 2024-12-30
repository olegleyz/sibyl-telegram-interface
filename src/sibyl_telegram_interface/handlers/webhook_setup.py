"""Lambda handler for setting up the Telegram webhook."""

import json
from typing import Dict, Any
import cfnresponse

from ..telegram.bot import TelegramBot
from ..utils.ssm import get_bot_token

def lambda_handler(event: Dict[str, Any], context: Any) -> None:
    """Handle webhook setup as a CloudFormation custom resource."""
    try:
        if event['RequestType'] in ['Create', 'Update']:
            # Get the function URL from the event
            function_url = event['ResourceProperties']['FunctionUrl']
            
            try:
                # Get bot token and initialize bot
                bot_token = get_bot_token()
                bot = TelegramBot(bot_token)
                
                # Set up webhook
                response = bot.set_webhook(function_url)
                
                if not response.get('ok'):
                    error_message = response.get('description', 'Unknown error')
                    if 'invalid token' in str(response).lower():
                        error_message = (
                            "ERROR: The bot token stored in SSM Parameter Store is invalid. "
                            "Please update it with a valid token."
                        )
                    raise ValueError(error_message)
                
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {
                    'WebhookUrl': function_url,
                    'SetupResponse': response
                })
                
            except ValueError as e:
                print(str(e))
                cfnresponse.send(event, context, cfnresponse.FAILED, {
                    'Error': str(e)
                })
                
        elif event['RequestType'] == 'Delete':
            # Clean up webhook if needed
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            
    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        cfnresponse.send(event, context, cfnresponse.FAILED, {
            'Error': error_message
        })
