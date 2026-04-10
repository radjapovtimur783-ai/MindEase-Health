import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("mood.db")
    cursor = conn.cursor()

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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("mood.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM moods")
    total_entries = cursor.fetchone()[0]

    cursor.execute("SELECT mood FROM moods ORDER BY id DESC LIMIT 1")
    latest_row = cursor.fetchone()
    latest_mood = latest_row[0] if latest_row else "No entries yet"

    cursor.execute("SELECT COUNT(*) FROM moods WHERE mood IN ('Happy', 'Positive')")
    positive_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM moods WHERE mood IN ('Sad', 'Stressed', 'Anxious', 'Negative', 'Highly Negative')")
    negative_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT mood, COUNT(*) 
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

    for mood, count in mood_counts_raw:
        if mood in mood_counts:
            mood_counts[mood] = count

    conn.close()

    return render_template(
        "dashboard.html",
        total_entries=total_entries,
        latest_mood=latest_mood,
        positive_count=positive_count,
        negative_count=negative_count,
        mood_counts=mood_counts
    )


@app.route("/mood", methods=["GET", "POST"])
def mood():
    result = None
    advice = None

    if request.method == "POST":
        text = request.form["mood_text"].lower()

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

        conn = sqlite3.connect("mood.db")
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
    conn = sqlite3.connect("mood.db")
    cursor = conn.cursor()
    cursor.execute("SELECT text, mood FROM moods ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()

    return render_template("history.html", data=data)


@app.route("/support")
def support():
    return render_template("support.html")


@app.route("/book", methods=["GET", "POST"])
def book():
    success = False

    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        session_type = request.form["session_type"]
        preferred_date = request.form["preferred_date"]
        notes = request.form["notes"]

        conn = sqlite3.connect("mood.db")
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
    success = False

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn = sqlite3.connect("mood.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO wellness_notes (title, content) VALUES (?, ?)",
            (title, content)
        )
        conn.commit()
        conn.close()

        success = True

    conn = sqlite3.connect("mood.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, content FROM wellness_notes ORDER BY id DESC")
    notes_data = cursor.fetchall()
    conn.close()

    return render_template("notes.html", success=success, notes_data=notes_data)


if __name__ == "__main__":
    app.run(debug=True)