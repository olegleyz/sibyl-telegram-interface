# Sibyl Telegram Interface

AWS Lambda function that handles Telegram bot messages and interfaces with the backend service.

## Prerequisites

1. Create a Telegram bot and get the bot token from [@BotFather](https://t.me/botfather)

2. Deploy the sibyl-core CloudFormation stack first
   - This stack exports the API endpoint that this service depends on
   - The stack name should follow the pattern `sibyl-core-{env}` where env is either `dev` or `prod`

3. Store the bot token in AWS Parameter Store:
```bash
aws ssm put-parameter \
    --name "/sibyl/telegram/bot-token" \
    --value "YOUR_BOT_TOKEN" \
    --type "SecureString" \
    --description "Telegram Bot Token for Sibyl"
```

This step is required before deploying the stack. If you deploy without setting up the parameter, the deployment will fail with a clear error message telling you how to fix it.

## Setup

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure AWS Parameter Store:
- Store the Telegram bot token securely in AWS Parameter Store at `/sibyl/telegram/bot-token`
- Ensure the Lambda function has appropriate IAM permissions to access the parameter

## AWS Parameter Store Setup

Store the Telegram bot token in AWS Parameter Store:

Using AWS CLI:
```bash
aws ssm put-parameter \
    --name "/sibyl/telegram/bot-token" \
    --value "YOUR_BOT_TOKEN" \
    --type "SecureString" \
    --description "Telegram Bot Token for Sibyl"
```

Or using AWS Console:
1. Go to AWS Systems Manager
2. Navigate to Parameter Store
3. Click "Create parameter"
4. Set:
   - Name: `/sibyl/telegram/bot-token`
   - Type: SecureString
   - Value: Your Telegram bot token
5. Click "Create parameter"

3. Deploy to AWS Lambda:
- Create a new Lambda function
- Set Python 3.12 as the runtime
- Set `lambda_handler.lambda_handler` as the handler
- Configure environment variables if needed
- The function URL will be automatically configured by SAM

## Deployment with AWS SAM

1. Install AWS SAM CLI following the [official instructions](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

2. Build the SAM application:
```bash
sam build
```

3. Deploy the application:
```bash
# First-time deployment
sam deploy --guided

# Subsequent deployments
sam deploy
```

## Setting up the Telegram Webhook

The webhook is automatically configured during the first deployment using a Custom Resource in CloudFormation. You don't need to run any additional commands.

To verify the webhook setup:
```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

If you need to manually set up the webhook, you can use the provided script:
```bash
./setup_webhook.py --stack-name <your-stack-name>
```

## Security Features

- IP validation for Telegram webhook requests
- Message length validation
- Secure token storage using AWS Parameter Store
- Request validation using Pydantic models
- Comprehensive error handling and logging

## Development

To add the backend API client:
1. Generate the Python client from your OpenAPI specification
2. Add the generated client to the project
3. Update the `lambda_handler` function to use the client for backend communication

## Testing

TODO: Add test cases for:
- IP validation
- Message validation
- Backend API integration
- Telegram API integration
