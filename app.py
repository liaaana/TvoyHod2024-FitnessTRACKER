from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "Sbjbdkcdkv762BSvfedJDV3"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

if __name__ == "__main__":
    from models.user import User
    from routes import *
    with app.app_context():
        db.create_all()
    app.run()

