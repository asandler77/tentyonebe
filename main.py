from flask import Flask, request, jsonify
import boto3
import json
import re
import string

app = Flask(__name__)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Game state
secret_word = None
question_count = 0
MAX_QUESTIONS = 21


def normalize(text: str) -> str:
    """lowercase + strip punctuation + collapse spaces"""
    text = text.lower().strip()
    # remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    # collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text


def is_correct_guess(user_text: str, secret: str) -> bool:
    """Return True if the user text is a direct guess of the secret word."""
    t = normalize(user_text)
    s = normalize(secret)

    # exact word only
    if t == s:
        return True

    # common guess phrasings
    patterns = [
        rf"^is it {re.escape(s)}$",
        rf"^is this {re.escape(s)}$",
        rf"^is the word {re.escape(s)}$",
        rf"^is it a {re.escape(s)}$",
        rf"^is it an {re.escape(s)}$",
    ]
    return any(re.match(p, t) for p in patterns)


@app.route("/start_game", methods=["POST"])
def start_game():
    global secret_word, question_count

    # Generate a random word with Claude v2
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

    # reset question counter
    question_count = 0

    return jsonify({"message": "Game started!", "secret_word_length": len(secret_word)})


@app.route("/ask", methods=["POST"])
def ask_question():
    global secret_word, question_count

    if not secret_word:
        return jsonify(answer="The game has not started yet. Please start a new game first."), 400

    data = request.get_json() or {}
    question = (data.get("question") or "").strip()

    # Reveal requests (do not count against the 21 questions)
    reveal_triggers = ["reveal the word", "what is the word", "tell me the word", "open the word", "show the word"]
    if any(rt in question.lower() for rt in reveal_triggers):
        ans = f"The word I thought of is '{secret_word}'."
        # End game on reveal
        secret_word = None
        question_count = 0
        return jsonify(answer=ans)

    # Increase question count for any non-reveal ask
    question_count += 1

    # Check for a direct correct guess
    if is_correct_guess(question, secret_word):
        ans = "You won!"
        # End game on win
        secret_word = None
        question_count = 0
        return jsonify(answer=ans)

    # If limit reached and not guessed: lose
    if question_count >= MAX_QUESTIONS:
        ans = "You lose!"
        # Optionally reveal the word here if you like:
        # ans = f"You lose! The word was '{secret_word}'."
        # End game on loss
        secret_word = None
        question_count = 0
        return jsonify(answer=ans)

    # Otherwise ask Claude for yes/no/unclear
    body = json.dumps({
        "prompt": f"""Human: We're playing '21 questions'. The secret word is '{secret_word}'.
User asked: "{question}" Answer with 'yes', 'no', or 'unclear'.

Assistant:""",
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
    app.run(host="0.0.0.0", port=5000, debug=False)
