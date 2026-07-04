from config.database import db
from sqlalchemy.sql import func


class Reminder(db.Model):

    __tablename__ = "reminders"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    last_injection_date = db.Column(
        db.Date
    )

    next_injection_date = db.Column(
        db.Date,
        nullable=False
    )

    reminder_sent = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )