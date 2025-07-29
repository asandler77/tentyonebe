from flask import Flask, request, jsonify
import boto3
import json

app = Flask(__name__)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question", "")

    body = json.dumps({
        "prompt": f"Human: {question}\n\nAssistant:",
        "max_tokens_to_sample": 300,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"]
    })

    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = response['body'].read().decode()
    parsed = json.loads(result)
    return jsonify(answer=parsed["completion"])

if __name__ == "__main__":
    app.run(debug=True)
