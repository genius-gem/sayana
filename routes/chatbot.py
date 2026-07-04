from flask import (
    Blueprint,
    request,
    jsonify
)

from services.chatbot import get_response


chatbot_bp = Blueprint(
    "chatbot",
    __name__
)


@chatbot_bp.route(
    "/ask",
    methods=["POST"]
)
def ask():

    data = request.get_json()

    if not data:

        return jsonify({
            "answer": "No request received."
        }), 400

    question = data.get(
        "question",
        ""
    ).strip()

    if not question:

        return jsonify({
            "answer": "Please enter a question."
        }), 400

    try:

        answer = get_response(question)

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print(e)

        return jsonify({
            "answer": "Sorry, something went wrong while processing your request."
        }), 500