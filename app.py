import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mindease_secret_key_2026"


def get_db_connection():
    conn = sqlite3.connect("mood.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS moods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        mood TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT,
        session_type TEXT,
        preferred_date TEXT,
        notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wellness_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


def is_logged_in():
    return "user_id" in session


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not email or not password or not confirm_password:
            flash("Please fill in all fields.")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            flash("An account with this email already exists.")
            return render_template("register.html")

        cursor.execute("""
            INSERT INTO users (full_name, email, password)
            VALUES (?, ?, ?)
        """, (full_name, email, hashed_password))

        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, full_name, email, password FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["user_email"] = user["email"]
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM moods")
    total_entries = cursor.fetchone()["count"]

    cursor.execute("SELECT mood FROM moods ORDER BY id DESC LIMIT 1")
    latest_row = cursor.fetchone()
    latest_mood = latest_row["mood"] if latest_row else "No entries yet"

    cursor.execute("SELECT COUNT(*) AS count FROM moods WHERE mood = 'Happy'")
    positive_count = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM moods
        WHERE mood IN ('Sad', 'Stressed', 'Anxious')
    """)
    negative_count = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT mood, COUNT(*) AS count
        FROM moods
        GROUP BY mood
    """)
    mood_counts_raw = cursor.fetchall()

    mood_counts = {
        "Happy": 0,
        "Sad": 0,
        "Stressed": 0,
        "Anxious": 0,
        "Neutral": 0
    }

    for row in mood_counts_raw:
        mood = row["mood"]
        count = row["count"]
        if mood in mood_counts:
            mood_counts[mood] = count

    cursor.execute("SELECT mood FROM moods ORDER BY id DESC LIMIT 5")
    recent_rows = cursor.fetchall()
    recent_moods = [row["mood"] for row in recent_rows]

    negative_recent = sum(1 for mood in recent_moods if mood in ["Sad", "Stressed", "Anxious"])
    show_alert = negative_recent >= 3

    conn.close()

    return render_template(
        "dashboard.html",
        total_entries=total_entries,
        latest_mood=latest_mood,
        positive_count=positive_count,
        negative_count=negative_count,
        mood_counts=mood_counts,
        show_alert=show_alert,
        negative_recent=negative_recent,
        user_name=session.get("user_name", "User")
    )


@app.route("/mood", methods=["GET", "POST"])
def mood():
    if not is_logged_in():
        return redirect(url_for("login"))

    result = None
    advice = None

    if request.method == "POST":
        text = request.form.get("mood_text", "").strip().lower()

        if text:
            mood_keywords = {
                "Happy": ["happy", "great", "amazing", "good", "excited", "joy", "fantastic"],
                "Sad": ["sad", "down", "upset", "hurt", "depressed", "crying", "lonely"],
                "Stressed": ["stress", "stressed", "pressure", "overwhelmed", "burnout", "tired"],
                "Anxious": ["anxious", "worried", "nervous", "panic", "afraid", "uneasy"]
            }

            mood_scores = {
                "Happy": 0,
                "Sad": 0,
                "Stressed": 0,
                "Anxious": 0
            }

            for mood_name, keywords in mood_keywords.items():
                for word in keywords:
                    if word in text:
                        mood_scores[mood_name] += 1

            max_score = max(mood_scores.values())

            if max_score == 0:
                result = "Neutral"
                advice = "Maintain a balanced routine and check in with yourself regularly."
            else:
                result = max(mood_scores, key=mood_scores.get)

                if result == "Happy":
                    advice = "Keep doing what supports your wellbeing and share positivity with others."
                elif result == "Sad":
                    advice = "Consider talking to someone you trust, resting, and doing a calming activity."
                elif result == "Stressed":
                    advice = "Try deep breathing, take short breaks, and break large tasks into smaller steps."
                elif result == "Anxious":
                    advice = "Use grounding techniques, breathe slowly, and focus on one thing at a time."

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO moods (text, mood) VALUES (?, ?)",
                (text, result)
            )
            conn.commit()
            conn.close()

    return render_template("mood.html", result=result, advice=advice)


@app.route("/history")
def history():
    if not is_logged_in():
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT text, mood FROM moods ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()

    return render_template("history.html", data=data)


@app.route("/support")
def support():
    if not is_logged_in():
        return redirect(url_for("login"))

    return render_template("support.html")


@app.route("/book", methods=["GET", "POST"])
def book():
    if not is_logged_in():
        return redirect(url_for("login"))

    success = False

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        session_type = request.form.get("session_type", "").strip()
        preferred_date = request.form.get("preferred_date", "").strip()
        notes = request.form.get("notes", "").strip()

        if full_name and email and session_type and preferred_date:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookings (full_name, email, session_type, preferred_date, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (full_name, email, session_type, preferred_date, notes))
            conn.commit()
            conn.close()

            success = True

    return render_template("book.html", success=success)


@app.route("/notes", methods=["GET", "POST"])
def notes():
    if not is_logged_in():
        return redirect(url_for("login"))

    success = False

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if title and content:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO wellness_notes (title, content) VALUES (?, ?)",
                (title, content)
            )
            conn.commit()
            conn.close()
            success = True

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, content FROM wellness_notes ORDER BY id DESC")
    notes_data = cursor.fetchall()
    conn.close()

    return render_template("notes.html", success=success, notes_data=notes_data)


if __name__ == "__main__":
    app.run(debug=True)