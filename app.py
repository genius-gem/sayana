import os
from datetime import date, datetime, timedelta

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session
)

from werkzeug.security import generate_password_hash

from config.database import db
from config.mail import mail

# Models
from models.user import User
from models.reminder import Reminder
from models.reminder_log import ReminderLog
from models.chat_history import ChatHistory
from models.activity import Activity
from models.knowledge import Knowledge
from models.injection_history import InjectionHistory

# Blueprints
# Blueprints
from routes.auth import auth_bp
from routes.chatbot import chatbot_bp
from routes.admin import admin_bp

from scheduler.scheduler import SchedulerService




# ==========================================================
# APP CONFIGURATION
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


# ==========================================
# MAIL CONFIGURATION
# ==========================================

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")

app.config["MAIL_PORT"] = int(
    os.getenv("MAIL_PORT", 587)
)

app.config["MAIL_USE_TLS"] = (
    os.getenv("MAIL_USE_TLS") == "True"
)

app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")

app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "MAIL_DEFAULT_SENDER"
)

mail.init_app(app)


# ==========================================================
# REGISTER BLUEPRINTS
# ==========================================================

app.register_blueprint(auth_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(admin_bp)


# ==========================================================
# CURRENT USER
# ==========================================================

def get_current_user():

    user_id = session.get("user_id")

    if user_id is None:
        return None

    return db.session.get(User, user_id)


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():

    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    return redirect(url_for("auth.login"))


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    user = get_current_user()

    if user is None:
        return redirect(url_for("auth.login"))

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

    days_remaining = 0

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

    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    return render_template(
        "chat.html"
    )


# ==========================================================
# RESOURCES
# ==========================================================

@app.route("/resources")
def resources():

    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    return render_template(
        "resources.html"
    )


# ==========================================================
# PROFILE
# ==========================================================

@app.route("/profile")
def profile():

    user = get_current_user()

    if user is None:
        return redirect(url_for("auth.login"))

    reminder = Reminder.query.filter_by(
        user_id=user.id
    ).first()

    days_remaining = 0

    if reminder:

        days_remaining = (
            reminder.next_injection_date -
            date.today()
        ).days

    return render_template(
        "profile.html",
        user=user,
        reminder=reminder,
        days_remaining=days_remaining
    )

# ==========================================================
# UPDATE PROFILE
# ==========================================================

@app.route(
    "/update-profile",
    methods=["POST"]
)
def update_profile():

    user = get_current_user()

    if user is None:

        return jsonify({
            "success": False,
            "message": "Please login first."
        })

    user.full_name = request.form.get(
        "full_name",
        user.full_name
    )

    user.phone = request.form.get(
        "phone",
        user.phone
    )

    user.location = request.form.get(
        "location",
        user.location
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Profile updated successfully."
    })


# ==========================================================
# UPDATE REMINDER
# ==========================================================

@app.route(
    "/update-reminder",
    methods=["POST"]
)
def update_reminder():

    user = get_current_user()

    if user is None:
        return redirect(url_for("auth.login"))

    last_date = request.form.get(
        "last_injection_date"
    )

    if not last_date:
        return redirect(url_for("profile"))

    last_injection = datetime.strptime(
        last_date,
        "%Y-%m-%d"
    ).date()

    next_injection = (
        last_injection +
        timedelta(weeks=13)
    )

    reminder = Reminder.query.filter_by(
        user_id=user.id
    ).first()

    if reminder is None:

        reminder = Reminder(

            user_id=user.id,

            last_injection_date=last_injection,

            next_injection_date=next_injection,

            whatsapp_enabled=(
                request.form.get(
                    "whatsapp_enabled"
                ) == "on"
            ),

            email_enabled=(
                request.form.get(
                    "email_enabled"
                ) == "on"
            )
        )

        db.session.add(reminder)

    else:

        reminder.last_injection_date = (
            last_injection
        )

        reminder.next_injection_date = (
            next_injection
        )

        reminder.whatsapp_enabled = (
            request.form.get(
                "whatsapp_enabled"
            ) == "on"
        )

        reminder.email_enabled = (
            request.form.get(
                "email_enabled"
            ) == "on"
        )

        reminder.reminder_sent = False

    db.session.commit()

    activity = Activity(

        user_id=user.id,

        activity="Updated reminder schedule"

    )

    db.session.add(activity)
    db.session.commit()

    return redirect(
        url_for("profile")
    )


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(
        email="admin@sayanapress.com"
    ).first()

    if admin is None:

        admin = User(

            full_name="System Administrator",

            email="admin@sayanapress.com",

            password=generate_password_hash(
                "Admin@123"
            ),

            phone="+2348000000000",

            location="Nigeria",

            whatsapp_enabled=True,

            email_enabled=True,

            is_admin=True
        )

        db.session.add(admin)
        db.session.commit()

        print("=" * 60)
        print("DEFAULT ADMINISTRATOR CREATED")
        print("Email    : admin@sayanapress.com")
        print("Password : Admin@123")
        print("=" * 60)

    else:
        print("Administrator already exists.")



# ==========================================
# START BACKGROUND SCHEDULER
# ==========================================

if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:

    scheduler = SchedulerService()

    scheduler.start()


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )