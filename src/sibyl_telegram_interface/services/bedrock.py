import boto3
import logging
import os

from aws_lambda_powertools import Logger


logger = Logger()
logger.setLevel(logging.INFO)


class Bedrock:
    def __init__(self, region="us-east-1"):
        self.client = boto3.client('bedrock-agent-runtime', region_name=region)

    def invoke_agent(self, user_id, prompt):    
        # Retrieve the necessary parameters from environment variables
        agent_id = os.environ['AGENT_ID']
        agent_alias_id = os.environ['AGENT_ALIAS_ID']
        logger.info(f"user_id: {user_id}")
        logger.info(f"prompt: {prompt}")

        # Invoke the Bedrock Agent
        response = self.client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=str(user_id),
            inputText=prompt,
            # enableTrace=True,  # Set enableTrace to True or False as needed
            sessionState={
                "sessionAttributes": {
                    "user_id": user_id
                },
            }
        ) 

        # Process the response
        completion = ''
        for event in response.get('completion', []):
            chunk = event['chunk']
            completion += chunk['bytes'].decode()

        return completion
