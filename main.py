from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question", "").lower()
    print(f"[API] Получен вопрос: {question}")
    if "это животное?" in question:
        return jsonify(answer="Верно")
    else:
        return jsonify(answer="Неверно")

if __name__ == "__main__":
    app.run(debug=True)
