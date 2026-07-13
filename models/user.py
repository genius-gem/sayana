from config.database import db
from sqlalchemy.sql import func


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        default=""
    )

    location = db.Column(
        db.String(150),
        default=""
    )

    whatsapp_enabled = db.Column(
        db.Boolean,
        default=True
    )

    email_enabled = db.Column(
        db.Boolean,
        default=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )

    is_active = db.Column(
    db.Boolean,
    default=True
    )

    # ----------------------------------
    # Relationships
    # ----------------------------------

    reminders = db.relationship(
        "Reminder",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    activities = db.relationship(
        "Activity",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    chat_history = db.relationship(
        "ChatHistory",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    injection_history = db.relationship(
        "InjectionHistory",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"