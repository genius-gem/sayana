from config.database import db
from sqlalchemy.sql import func


class InjectionHistory(db.Model):

    __tablename__ = "injection_history"

    # ======================================================
    # PRIMARY KEY
    # ======================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ======================================================
    # USER
    # ======================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # ======================================================
    # INJECTION DETAILS
    # ======================================================

    injection_number = db.Column(
        db.Integer,
        nullable=False
    )

    injection_date = db.Column(
        db.Date,
        nullable=False
    )

    next_injection_date = db.Column(
        db.Date,
        nullable=False
    )

    injection_site = db.Column(
        db.String(100),
        nullable=False
    )

    administered_by = db.Column(
        db.String(150),
        default="Self"
    )

    status = db.Column(
        db.String(30),
        default="Completed"
    )
    # Completed
    # Missed
    # Upcoming

    notes = db.Column(
        db.Text,
        default=""
    )

    # ======================================================
    # TIMESTAMPS
    # ======================================================

    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    
    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self):

        return (
            f"<InjectionHistory "
            f"User={self.user_id} "
            f"Injection={self.injection_number}>"
        )