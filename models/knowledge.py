from config.database import db
from sqlalchemy.sql import func


class Knowledge(db.Model):

    __tablename__ = "knowledge"

    # ======================================================
    # PRIMARY KEY
    # ======================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ======================================================
    # ARTICLE TITLE
    # ======================================================

    title = db.Column(
        db.String(255),
        nullable=False
    )

    # ======================================================
    # CATEGORY
    # ======================================================

    category = db.Column(
        db.String(100),
        nullable=False
    )

    # ======================================================
    # CONTENT
    # ======================================================

    content = db.Column(
        db.Text,
        nullable=False
    )

    # ======================================================
    # OPTIONAL KEYWORDS
    # ======================================================

    keywords = db.Column(
        db.String(500),
        nullable=True
    )

    # ======================================================
    # STATUS
    # ======================================================

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    # ======================================================
    # CREATED DATE
    # ======================================================

    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )

    # ======================================================
    # UPDATED DATE
    # ======================================================

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
            f"<Knowledge {self.title}>"
        )

    # ======================================================
    # TO DICTIONARY
    # ======================================================

    def to_dict(self):

        return {

            "id": self.id,

            "title": self.title,

            "category": self.category,

            "content": self.content,

            "keywords": self.keywords,

            "is_active": self.is_active
        }