# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import uuid
import os
import boto3
import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed trace

# Environment and DynamoDB setup
CONTAINER_PORT = os.getenv('DYNAMODB_CONTAINER_PORT', '8000')
DYNAMODB_ENDPOINT_URL = os.getenv('DYNAMODB_ENDPOINT_URL', f'http://localhost:{CONTAINER_PORT}')
CONTAINER_NAME = os.getenv('CONTAINER_NAME', 'pytest-dynamodb-local')
USERS_TABLE = os.getenv('USERS_TABLE', None)
REGION = os.getenv('AWS_DEFAULT_REGION', None)

logger.info(f"Initializing DynamoDB resource with endpoint {DYNAMODB_ENDPOINT_URL} and region {REGION}")
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT_URL,
    region_name=REGION
)
ddbTable = dynamodb.Table(USERS_TABLE)


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    route_key = f"{event.get('httpMethod')} {event.get('resource')}"
    logger.debug(f"Determined route_key: {route_key}")

    # Default response
    response_body = {'Message': 'Unsupported route'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }

    try:
        if route_key == 'GET /users':
            logger.info("Handling GET /users: Scanning all users")
            ddb_response = ddbTable.scan(Select='ALL_ATTRIBUTES')
            response_body = ddb_response.get('Items', [])
            logger.debug(f"Scan result: {response_body}")
            status_code = 200

        elif route_key == 'GET /users/{userid}':
            userid = event.get('pathParameters', {}).get('userid')
            logger.info(f"Handling GET /users/{{userid}} for userid={userid}")
            ddb_response = ddbTable.get_item(Key={'userid': userid})
            response_body = ddb_response.get('Item', {})
            logger.debug(f"GetItem result: {response_body}")
            status_code = 200

        elif route_key == 'DELETE /users/{userid}':
            userid = event.get('pathParameters', {}).get('userid')
            logger.info(f"Handling DELETE /users/{{userid}} for userid={userid}")
            ddbTable.delete_item(Key={'userid': userid})
            response_body = {}
            status_code = 200
            logger.debug(f"Deleted user with userid={userid}")

        elif route_key == 'POST /users':
            logger.info("Handling POST /users: Creating user")
            request_json = json.loads(event['body'])
            request_json['timestamp'] = datetime.now().isoformat()
            if 'userid' not in request_json:
                request_json['userid'] = str(uuid.uuid1())
                logger.debug(f"Generated new userid: {request_json['userid']}")
            ddbTable.put_item(Item=request_json)
            response_body = request_json
            status_code = 200
            logger.debug(f"Created user item: {response_body}")

        elif route_key == 'PUT /users/{userid}':
            userid = event.get('pathParameters', {}).get('userid')
            logger.info(f"Handling PUT /users/{{userid}} for userid={userid}")
            request_json = json.loads(event['body'])
            request_json['timestamp'] = datetime.now().isoformat()
            request_json['userid'] = userid
            ddbTable.put_item(Item=request_json)
            response_body = request_json
            status_code = 200
            logger.debug(f"Updated user item: {response_body}")

        else:
            logger.warning(f"Unsupported route_key encountered: {route_key}")

    except Exception as err:
        status_code = 400
        response_body = {'Error': str(err)}
        logger.error(f"Exception processing request: {err}", exc_info=True)

    logger.info(f"Response status: {status_code}")
    logger.debug(f"Response body: {response_body}")

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
