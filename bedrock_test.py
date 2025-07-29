import boto3

import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')


body = {
    "prompt": "Human: Привет! Как дела?\n\nAssistant:",
    "max_tokens_to_sample": 100
}

response = bedrock.invoke_model(
    modelId='anthropic.claude-v2',
    body=json.dumps(body),
    contentType='application/json',
    accept='application/json'
)

print(response['body'].read().decode())
