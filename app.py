from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'checklist-secret-2026-xyz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ------------------ MODELS ------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300))
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    completed_by = db.Column(db.String(50))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------ ROUTES ------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.password == request.form["password"]:
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        new_task = Task(description=request.form["task"])
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("dashboard"))

    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("dashboard.html", tasks=tasks)


@app.route("/complete/<int:task_id>")
@login_required
def complete(task_id):
    task = Task.query.get(task_id)
    task.status = "Done"
    task.completed_at = datetime.utcnow()
    task.completed_by = current_user.username
    db.session.commit()
    return redirect(url_for("dashboard"))


# ------------------ INIT ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Create default users if not exists
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", password="admin123")
            je = User(username="je", password="je123")
            db.session.add(admin)
            db.session.add(je)
            db.session.commit()

    app.run()

