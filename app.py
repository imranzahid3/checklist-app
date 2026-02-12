from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bsnl-sector62-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------
# MODELS
# -------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(50), nullable=False)
    deadline = db.Column(db.String(100), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)

# -------------------
# INITIAL SETUP
# -------------------

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="BBM Sector-62").first():
        user1 = User(username="BBM Sector-62", password="bbm123")
        user2 = User(username="JE Sector-62", password="je123")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

# -------------------
# ROUTES
# -------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user'] = user.username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Credentials"

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        priority = request.form['priority']
        deadline = request.form['deadline']
        remarks = request.form['remarks']

        new_task = Task(
            name=name,
            description=description,
            priority=priority,
            deadline=deadline,
            remarks=remarks
        )
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('dashboard'))

    pending_tasks = Task.query.filter_by(completed=False).all()
    completed_tasks = Task.query.filter_by(completed=True).all()

    return render_template(
        'dashboard.html',
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )


@app.route('/complete/<int:id>')
def complete_task(id):
    task = Task.query.get(id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run(debug=True)

