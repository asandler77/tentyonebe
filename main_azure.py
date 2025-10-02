# main_azure.py
from flask import Flask, request, jsonify
from openai import AzureOpenAI
import json
import re
import string
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview"
)

# Model to use (configure for your deployed model)
AZURE_MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4")

# ---- Game state (within single process) ----
secret_word = None
question_count = 0
MAX_QUESTIONS = 21


# ---------- Utilities ----------
def normalize(text: str) -> str:
    """lowercase + remove punctuation + collapse spaces"""
    t = (text or "").lower().strip()
    t = t.translate(str.maketrans("", "", string.punctuation))
    t = re.sub(r"\s+", " ", t)
    return t


def is_correct_guess(user_text: str, secret: str) -> bool:
    """
    True if user explicitly guessed the word.
    Supports formats: "dog", "is it dog", "is the word dog", "is it a/an dog".
    """
    t = normalize(user_text)
    s = normalize(secret)
    if not t or not s:
        return False

    # exact match (user simply entered the word)
    if t == s:
        return True

    # common guessing question formats
    patterns = [
        rf"^is it {re.escape(s)}$",
        rf"^is this {re.escape(s)}$",
        rf"^is the word {re.escape(s)}$",
        rf"^is it a {re.escape(s)}$",
        rf"^is it an {re.escape(s)}$",
    ]
    return any(re.match(p, t) for p in patterns)


def is_reveal(question: str) -> bool:
    q = (question or "").lower()
    reveal_triggers = [
        "reveal the word", "what is the word", "tell me the word",
        "open the word", "show the word", "reveal word", "reveal"
    ]
    return any(tr in q for tr in reveal_triggers)


def generate_secret_word() -> str:
    """Generates a random word using Azure OpenAI"""
    try:
        response = client.chat.completions.create(
            model=AZURE_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a word generator for the game '21 questions'. Generate one random word that is suitable for this game."
                },
                {
                    "role": "user", 
                    "content": "Think of one random word for the game '21 questions'. Answer with ONLY the word, nothing else."
                }
            ],
            max_tokens=10,
            temperature=1.0
        )
        
        word = response.choices[0].message.content.strip()
        return word
    except Exception as e:
        print(f"Error generating word: {e}")
        return "cat"  # fallback word


def get_referee_answer(secret: str, question: str) -> str:
    """Gets referee answer from Azure OpenAI"""
    try:
        response = client.chat.completions.create(
            model=AZURE_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a strict referee in the game "21 questions".
The secret word is '{secret}'.
Answer ONLY with one word:
- "yes" if the secret word IS or BELONGS TO that category (synonyms and hypernyms count),
- "no" if it clearly is not,
- "unclear" if you cannot decide."""
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=5,
            temperature=0.0
        )
        
        answer = response.choices[0].message.content.strip().lower()
        
        # Normalize answer to yes/no/unclear
        if answer.startswith("yes"):
            return "yes"
        elif answer.startswith("no"):
            return "no"
        elif answer.startswith("unclear"):
            return "unclear"
        else:
            return "unclear"  # fallback
            
    except Exception as e:
        print(f"Error getting referee answer: {e}")
        return "unclear"  # fallback


# ---------- Endpoints ----------
@app.route("/start_game", methods=["POST"])
def start_game():
    global secret_word, question_count

    # Generate new word
    secret_word = generate_secret_word()
    question_count = 0  # reset counter

    print(f"New game started! Secret word: {secret_word}")
    
    return jsonify({
        "message": "Game started!", 
        "secret_word_length": len(secret_word)
    })


@app.route("/ask", methods=["POST"])
def ask_question():
    global secret_word, question_count

    if not secret_word:
        return jsonify(answer="The game has not started yet. Please start a new game first."), 400

    data = request.get_json() or {}
    question = (data.get("question") or "").strip()

    # 1) Reveal - don't count as question, ends game
    if is_reveal(question):
        ans = f"The word I thought of is '{secret_word}'."
        # end game
        secret_word = None
        question_count = 0
        return jsonify(answer=ans)

    # 2) Increment counter for any regular question
    question_count += 1

    # 3) Check for correct guess
    if is_correct_guess(question, secret_word):
        ans = "You won!"
        secret_word = None
        question_count = 0
        return jsonify(answer=ans)

    # 4) If reached limit - lose
    if question_count >= MAX_QUESTIONS:
        ans = "You lose!"
        secret_word = None
        question_count = 0
        return jsonify(answer=ans)

    # 5) Otherwise ask Azure OpenAI (strict referee)
    answer = get_referee_answer(secret_word, question)
    
    return jsonify(answer=answer)


@app.route("/health", methods=["GET"])
def health_check():
    """Application health check"""
    return jsonify({
        "status": "healthy",
        "service": "21 Questions Game - Azure OpenAI",
        "model": AZURE_MODEL_NAME
    })


# Run (for local debugging)
if __name__ == "__main__":
    # Check for required environment variables
    required_env_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"ERROR: Missing environment variables: {', '.join(missing_vars)}")
        print("Create .env file with required variables")
        exit(1)
    
    print(f"Starting application with model: {AZURE_MODEL_NAME}")
    print(f"Azure OpenAI Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    
    # Don't enable debug=True in production
    app.run(host="0.0.0.0", port=5000, debug=False)
