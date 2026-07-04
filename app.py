import os
from datetime import date

from flask import Flask, jsonify, render_template, request

from config.database import db

# Models
from models.user import User
from models.reminder import Reminder
from models.chat_history import ChatHistory
from models.activity import Activity

# Blueprints
from routes.chatbot import chatbot_bp
from routes.auth import auth_bp


# ==========================================================
# APP
# ==========================================================

app = Flask(
    __name__,
    instance_relative_config=True
)

os.makedirs(
    app.instance_path,
    exist_ok=True
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" +
    os.path.join(
        app.instance_path,
        "database.db"
    )
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key"
)

db.init_app(app)


# ==========================================================
# REGISTER BLUEPRINTS
# ==========================================================

app.register_blueprint(auth_bp)
app.register_blueprint(chatbot_bp)


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    user = User.query.first()

    reminder = None
    chat_count = 0
    activities = []
    days_remaining = 0

    if user:

        reminder = Reminder.query.filter_by(
            user_id=user.id
        ).first()

        chat_count = ChatHistory.query.filter_by(
            user_id=user.id
        ).count()

        activities = (
            Activity.query
            .filter_by(user_id=user.id)
            .order_by(Activity.created_at.desc())
            .limit(5)
            .all()
        )

        if reminder:

            days_remaining = (
                reminder.next_injection_date -
                date.today()
            ).days

    return render_template(
        "dashboard.html",
        user=user,
        reminder=reminder,
        chat_count=chat_count,
        activities=activities,
        days_remaining=days_remaining
    )


# ==========================================================
# CHAT
# ==========================================================

@app.route("/chat")
def chat():

    return render_template(
        "chat.html"
    )


# ==========================================================
# RESOURCES
# ==========================================================

@app.route("/resources")
def resources():

    return render_template(
        "resources.html"
    )


# ==========================================================
# PROFILE
# ==========================================================

@app.route("/profile")
def profile():

    user = User.query.first()

    reminder = None

    if user:

        reminder = Reminder.query.filter_by(
            user_id=user.id
        ).first()

    return render_template(
        "profile.html",
        user=user,
        reminder=reminder
    )


# ==========================================================
# UPDATE PROFILE
# ==========================================================

@app.route(
    "/update-profile",
    methods=["POST"]
)
def update_profile():

    user = User.query.first()

    if not user:

        return jsonify(
            {
                "success": False,
                "message": "User not found"
            }
        )

    user.full_name = request.form.get(
        "full_name"
    )

    user.phone = request.form.get(
        "phone"
    )

    user.location = request.form.get(
        "location"
    )

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Profile updated successfully."
        }
    )


# ==========================================================
# DATABASE
# ==========================================================

with app.app_context():

    db.create_all()


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )