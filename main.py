from flask import Flask, request, jsonify
import boto3
import json

app = Flask(__name__)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Переменная для хранения загаданного слова
secret_word = None

@app.route("/start_game", methods=["POST"])
def start_game():
    global secret_word
    
    # Генерируем слово с помощью Claude v2
    body = json.dumps({
        "prompt": "Human: Think of one random word for the game '21 questions'. Answer with ONLY the word.\n\nAssistant:",
        "max_tokens_to_sample": 10,
        "temperature": 1.0,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n", "\n\nHuman:"]
    })

    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = response['body'].read().decode()
    parsed = json.loads(result)
    
    secret_word = parsed["completion"].strip()

    return jsonify({"message": "Game started!", "secret_word_length": len(secret_word)})

@app.route("/ask", methods=["POST"])
def ask_question():
    global secret_word

    if not secret_word:
        return jsonify(answer="The game has not started yet. Please start a new game first."), 400

    data = request.get_json()
    question = data.get("question", "").strip().lower()

    reveal_triggers = ["reveal the word", "what is the word", "tell me the word", "open the word", "show the word"]
    if any(trigger in question for trigger in reveal_triggers):
        return jsonify(answer=f"The word I thought of is '{secret_word}'.")

    body = json.dumps({
        "prompt": f"""Human: We're playing '21 questions'. The secret word is '{secret_word}'. 
User asked: \"{question}\" Answer with 'yes', 'no', or 'unclear'.\n\nAssistant:""",
        "max_tokens_to_sample": 5,
        "temperature": 0.0,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n", "\n\nHuman:"]
    })

    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = response['body'].read().decode()
    parsed = json.loads(result)

    return jsonify(answer=parsed["completion"].strip())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)