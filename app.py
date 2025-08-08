from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'flowers'  # You can change this to a stronger secret key

# Change this to your admin name
ADMIN_USERNAME = "matilda"

# This is the file that stores all requests
REQUESTS_FILE = 'requests.json'


def load_requests():
    if os.path.exists(REQUESTS_FILE):
        with open(REQUESTS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_requests(requests):
    with open(REQUESTS_FILE, 'w') as f:
        json.dump(requests, f, indent=4)


# Load requests at app start
requests_db = load_requests()


@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    user = session["username"]

    if request.method == "POST":
        note = request.form.get("note")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        requests_db.append({
            "name": user,
            "note": note,
            "time": timestamp,
            "status": "open"
        })
        save_requests(requests_db)
        return redirect(url_for("index"))

    user_requests = [r for r in requests_db if r["name"] == user]
    return render_template("index.html", user=user, requests=user_requests, is_admin=(user == ADMIN_USERNAME))


@app.route("/admin")
def admin():
    if "username" not in session:
        return redirect(url_for("login"))

    user = session["username"]
    if user != ADMIN_USERNAME:
        return "Access denied", 403

    return render_template("admin.html", requests=requests_db, user=user)


@app.route("/done/<int:request_id>")
def mark_done(request_id):
    user = session.get("username")
    if user != ADMIN_USERNAME:
        return "Access denied", 403

    if 0 <= request_id < len(requests_db):
        requests_db[request_id]["status"] = "done"
        save_requests(requests_db)
    return redirect(url_for("admin"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash("Please enter a username")
            return redirect(url_for('login'))

        session['username'] = username
        flash(f"Logged in as {username}")
        if username == ADMIN_USERNAME:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(port=5003)
