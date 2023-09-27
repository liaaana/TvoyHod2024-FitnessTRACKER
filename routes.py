import json
from flask import Response, render_template, request, redirect, url_for, flash
from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask import stream_with_context, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, Response

from exersices import gen_push_up, gen_curl, gen_squat
from forms.login_form import LoginForm
from forms.register_form import RegistrationForm
from app import app, db, login_manager
from models.user import User


def load_translations(language):
    translations = {}
    try:
        with open(f'translations/{language}.json', 'r', encoding='utf-8') as file:
            translations = json.load(file)
    except FileNotFoundError:
        pass
    return translations



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/rating")
@login_required
def rating():
    users = (
        User.query.order_by(User.push_ups_counter + User.squats_counter + User.crunches_counter).all()
    )

    users = users[::-1]

    return render_template("rating.html", users=users)


@app.route("/exercises")
@login_required
def exercises():
    return render_template("exercises.html")


@app.route("/curl_preview")
@login_required
def curl_preview():
    """Video streaming squat page."""
    return render_template("curl_preview.html")

@app.route("/curl")
@login_required
def curl():
    """Video streaming squat page."""
    return render_template("curl.html")


@app.route("/curl_feed")
@login_required
def curl_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return app.response_class(stream_with_context(gen_curl()), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/push_up_preview")
@login_required
def push_up_preview():
    return render_template("push_up_preview.html")


@app.route("/push_up")
@login_required
def push_up():
    """Video streaming squat page."""
    return render_template("push_up.html")


@app.route("/push_up_feed")
@login_required
def push_up_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return app.response_class(stream_with_context(gen_push_up()), mimetype="multipart/x-mixed-replace; boundary=frame")



@app.route("/squat_preview")
@login_required
def squat_preview():
    return render_template("squat_preview.html")


@app.route("/squat")
@login_required
def squat():
    """Video streaming squat page."""
    return render_template("squat.html")


@app.route("/squat_feed")
@login_required
def squat_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return app.response_class(stream_with_context(gen_squat()), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method="sha256")
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("profile"))
        else:
            flash("Invalid email or password", "danger")
    return render_template("login.html", form=form)


@app.route('/profile')
@login_required
def profile():
    user_language = current_user.language 
    translations = load_translations(user_language)
    return render_template('profile.html', user=current_user, translations=translations)

@app.route("/change_username", methods=["POST"])
@login_required
def change_username():
    new_name = request.form.get("new_name")
    if new_name:
        current_user.name = new_name
        db.session.commit()
    return redirect("/profile")


@app.route("/change_language", methods=["POST"])
@login_required
def change_language():
    new_language = request.form.get("new_language")
    if new_language:
        current_user.language = new_language
        db.session.commit()
    return redirect("/profile")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
