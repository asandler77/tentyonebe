# main.py
from flask import Flask, request, jsonify
import boto3
import json
import re
import string

app = Flask(__name__)

# Клиент Bedrock (убедитесь, что настроены AWS креды и IAM-права на bedrock:InvokeModel)
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# ---- Состояние игры (в пределах одного процесса) ----
secret_word = None
question_count = 0
MAX_QUESTIONS = 21


# ---------- Утилиты ----------
def normalize(text: str) -> str:
    """низкий регистр + убрать пунктуацию + схлопнуть пробелы"""
    t = (text or "").lower().strip()
    t = t.translate(str.maketrans("", "", string.punctuation))
    t = re.sub(r"\s+", " ", t)
    return t


def is_correct_guess(user_text: str, secret: str) -> bool:
    """
    True если пользователь явно угадал слово.
    Поддержка форм: "dog", "is it dog", "is the word dog", "is it a/an dog".
    """
    t = normalize(user_text)
    s = normalize(secret)
    if not t or not s:
        return False

    # точное совпадение (пользователь просто ввёл слово)
    if t == s:
        return True

    # распространённые формы вопроса-угадывания
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


def build_referee_prompt(secret: str, question: str) -> str:
    """Усиленный промпт для строгого рефери."""
    return f"""Human: You are a strict referee in the game "21 questions".
The secret word is '{secret}'.
The user asked: "{question}"

Answer ONLY with one word:
- "yes" if the secret word IS or BELONGS TO that category (synonyms and hypernyms count),
- "no" if it clearly is not,
- "unclear" if you cannot decide.

Assistant:"""


# ---------- Эндпоинты ----------
@app.route("/start_game", methods=["POST"])
def start_game():
    global secret_word, question_count

    # запрос к Claude для генерации слова
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

    result = response["body"].read().decode()
    parsed = json.loads(result)

    secret_word = (parsed.get("completion") or "").strip()
    question_count = 0  # сброс счётчика

    return jsonify({"message": "Game started!", "secret_word_length": len(secret_word)})


@app.route("/ask", methods=["POST"])
def ask_question():
    global secret_word, question_count

    if not secret_word:
        return jsonify(answer="The game has not started yet. Please start a new game first."), 400

    data = request.get_json() or {}
    question = (data.get("question") or "").strip()

    # 1) Reveal — не считаем как вопрос, завершает игру
    if is_reveal(question):
        ans = f"The word I thought of is '{secret_word}'."
        # завершаем игру
        secret_word = None
        question_count = 0
        return jsonify(answer=ans)

    # 2) Увеличиваем счётчик за любой обычный вопрос
    question_count += 1

    # 3) Проверка на угадывание
    if is_correct_guess(question, secret_word):
        ans = "You won!"
        secret_word = None
        question_count = 0
        return jsonify(answer=ans)

    # 4) Если достигли лимит — проигрыш
    if question_count >= MAX_QUESTIONS:
        ans = "You lose!"
        secret_word = None
        question_count = 0
        return jsonify(answer=ans)

    # 5) Иначе спрашиваем у Claude (строгий рефери)
    prompt = build_referee_prompt(secret_word, question)

    body = json.dumps({
        "prompt": prompt,
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

    result = response["body"].read().decode()
    parsed = json.loads(result)
    answer = (parsed.get("completion") or "").strip()

    # Нормализуем ответ до yes/no/unclear на всякий случай
    norm = normalize(answer)
    if norm.startswith("yes"):
        answer = "yes"
    elif norm.startswith("no"):
        answer = "no"
    elif norm.startswith("unclear"):
        answer = "unclear"

    return jsonify(answer=answer)


# Запуск (для локальной отладки)
if __name__ == "__main__":
    # Не включайте debug=True на проде
    app.run(host="0.0.0.0", port=5000, debug=False)
