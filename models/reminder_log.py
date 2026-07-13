from config.database import db
from sqlalchemy.sql import func


class ReminderLog(db.Model):

    __tablename__ = "reminder_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================
    # USER
    # =====================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "reminder_logs",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    # =====================================
    # REMINDER
    # =====================================

    reminder_id = db.Column(
        db.Integer,
        db.ForeignKey("reminders.id"),
        nullable=False
    )

    reminder = db.relationship(
        "Reminder",
        backref=db.backref(
            "logs",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    # =====================================
    # DELIVERY CHANNEL
    # =====================================

    channel = db.Column(
        db.String(30),
        nullable=False
    )
    # email
    # whatsapp
    # sms

    # =====================================
    # REMINDER TYPE
    # =====================================

    reminder_type = db.Column(
        db.String(50),
        nullable=False
    )
    # 7 Days Before
    # 3 Days Before
    # Tomorrow
    # Today
    # Missed Dose

    # =====================================
    # STATUS
    # =====================================

    status = db.Column(
        db.String(30),
        default="Pending"
    )
    # Pending
    # Sent
    # Failed

    # =====================================
    # MESSAGE
    # =====================================

    message = db.Column(
        db.Text,
        nullable=True
    )

    error_message = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # TIMESTAMPS
    # =====================================

    sent_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )

    # =====================================
    # REPRESENTATION
    # =====================================

    def __repr__(self):
        return (
            f"<ReminderLog "
            f"User={self.user_id} "
            f"Channel={self.channel} "
            f"Status={self.status}>"
        )