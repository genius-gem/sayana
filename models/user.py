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
        db.String(20)
    )

    location = db.Column(
        db.String(150)
    )

    whatsapp_enabled = db.Column(
        db.Boolean,
        default=True
    )

    sms_enabled = db.Column(
        db.Boolean,
        default=True
    )

    email_enabled = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )