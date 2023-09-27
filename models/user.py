from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    push_ups_counter = db.Column(db.Integer, default=0)
    squats_counter = db.Column(db.Integer, default=0)
    crunches_counter = db.Column(db.Integer, default=0)
    language = db.Column(db.String(5), nullable=False, default="ru")
