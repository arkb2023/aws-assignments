#!/bin/bash

# Assumption: Environment variables are already set externally
# PREFIX="m8"
# SQS_STACK_NAME="${PREFIX}-sqs-fifo-stack"
# SQS_FIFO_QUEUE="${PREFIX}-fifo-queue.fifo"
# SQS_MESSAGE_GROUP="test-group"

# Retrieve the Queue URL from CloudFormation outputs
QUEUE_URL=$(aws cloudformation describe-stacks \
  --stack-name "$SQS_STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='QueueURL'].OutputValue" \
  --output text)

echo "Queue URL retrieved: $QUEUE_URL"
echo "Sending 10 messages to FIFO queue with group ID: $SQS_MESSAGE_GROUP"

# Loop to send 10 messages
for i in {1..10}; do
  MESSAGE_BODY="Test message $i"
  aws sqs send-message \
    --queue-url "$QUEUE_URL" \
    --message-body "$MESSAGE_BODY" \
    --message-group-id "$SQS_MESSAGE_GROUP"

  echo "Sent: $MESSAGE_BODY"
done

echo "All messages sent."