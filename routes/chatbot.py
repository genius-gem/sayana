from flask import (
    Blueprint,
    request,
    jsonify,
    session
)

from config.database import db

from models.chat_history import ChatHistory

from services.chatbot import get_response


chatbot_bp = Blueprint(
    "chatbot",
    __name__
)


# ==========================================================
# CHATBOT API
# ==========================================================

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

        # ==========================================
        # SAVE CHAT HISTORY
        # ==========================================

        user_id = session.get("user_id")

        if user_id:

            chat = ChatHistory(

                user_id=user_id,

                question=question,

                answer=answer

            )

            db.session.add(chat)

            db.session.commit()

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print(e)

        return jsonify({
            "answer": (
                "Sorry, something went wrong while "
                "processing your request."
            )
        }), 500