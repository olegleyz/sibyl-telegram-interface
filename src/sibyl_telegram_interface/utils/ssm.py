"""AWS SSM Parameter Store utilities."""

import boto3
from botocore.exceptions import ClientError
from ..config import settings

def get_bot_token() -> str:
    """
    Get the bot token from SSM Parameter Store.
    
    Raises:
        ValueError: If the parameter is not found or invalid
    """
    try:
        ssm = boto3.client('ssm')
        response = ssm.get_parameter(
            Name=settings.BOT_TOKEN_PARAM_PATH,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            raise ValueError(
                f"The required parameter '{settings.BOT_TOKEN_PARAM_PATH}' was not found in SSM Parameter Store. "
                "Please add it using:\n"
                f"aws ssm put-parameter --name '{settings.BOT_TOKEN_PARAM_PATH}' --value 'YOUR_BOT_TOKEN' --type 'SecureString'"
            )
        raise
