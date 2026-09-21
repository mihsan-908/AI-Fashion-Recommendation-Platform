from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )


class SavedOutfit(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    outfit_name = db.Column(
        db.String(200),
        nullable=False
    )

    top = db.Column(
        db.String(500)
    )

    bottom = db.Column(
        db.String(500)
    )

    shoes = db.Column(
        db.String(500)
    )

    accessories = db.Column(
        db.String(500)
    )

    style_tip = db.Column(
        db.Text
    )

    # Stores the generated fashion image URL/path
    generated_image_url = db.Column(
        db.String(500)
    )