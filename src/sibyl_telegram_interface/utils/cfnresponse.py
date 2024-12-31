"""
AWS CloudFormation Custom Resource Response Helper.
Based on: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
"""

import json
import logging
import urllib3
from typing import Dict, Any, Optional

SUCCESS = "SUCCESS"
FAILED = "FAILED"

http = urllib3.PoolManager(retries=urllib3.Retry(3))
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send(
    event: Dict[str, Any],
    context: Any,
    response_status: str,
    response_data: Dict[str, Any],
    physical_resource_id: Optional[str] = None,
    no_echo: bool = False,
    reason: Optional[str] = None
) -> None:
    """Send a response to CloudFormation regarding the success or failure of a custom resource deployment."""
    
    if 'ResponseURL' not in event:
        logger.error("No ResponseURL found in the event")
        return
    
    response_url = event['ResponseURL']
    logger.info(f"CFN response URL: {response_url}")

    response_body = {
        'Status': response_status,
        'Reason': reason or f"See the details in CloudWatch Log Stream: {context.log_stream_name}",
        'PhysicalResourceId': physical_resource_id or context.log_stream_name,
        'StackId': event.get('StackId', ''),
        'RequestId': event.get('RequestId', ''),
        'LogicalResourceId': event.get('LogicalResourceId', ''),
        'NoEcho': no_echo,
        'Data': response_data or {}
    }

    json_response_body = json.dumps(response_body)
    logger.info("Response body: %s", json_response_body)

    headers = {
        'content-type': '',
        'content-length': str(len(json_response_body))
    }

    try:
        response = http.request(
            'PUT',
            response_url,
            body=json_response_body.encode('utf-8'),
            headers=headers,
            timeout=urllib3.Timeout(connect=5.0, read=10.0)
        )
        logger.info(f"CloudFormation response status code: {response.status}")
        
        if response.status >= 400:
            logger.error(f"CloudFormation response error: {response.data.decode('utf-8')}")
    except Exception as e:
        logger.error(f"Failed to send response to CloudFormation: {str(e)}")
        # Don't re-raise the exception - we want the Lambda to exit gracefully
        # even if we couldn't send the response
