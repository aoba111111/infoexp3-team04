from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
import sqlite3
from pathlib import Path

app = Flask(__name__)

DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "miniboard.db"
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        # likes INTEGER DEFAULT 0 を追加しました
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                likes INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                commenter_name TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.get("/api/messages")
def get_messages():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM messages ORDER BY id DESC")
        messages_rows = cursor.fetchall()
        
        messages = []
        for row in messages_rows:
            msg = dict(row)
            cursor.execute("SELECT * FROM comments WHERE message_id = ? ORDER BY id ASC", (msg['id'],))
            msg['comments'] = [dict(c) for c in cursor.fetchall()]
            messages.append(msg)

    return jsonify(messages)

@app.post("/api/messages")
def create_message():
    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    photo = request.files.get("photo")

    if not name or not price or not photo:
        return jsonify({"error": "name, price, and photo are required"}), 400

    filename = photo.filename
    save_path = UPLOAD_DIR / filename
    photo.save(save_path)
    photo_path = f"/static/uploads/{filename}"
    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (name, price, photo_path, created_at, likes) VALUES (?, ?, ?, ?, 0)",
            (name, int(price), photo_path, created_at)
        )
        conn.commit()

    return jsonify({"message": "success"}), 201

# 新しく追加：グッドボタンを押したときの処理
@app.post("/api/messages/<int:message_id>/like")
def like_message(message_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE messages SET likes = likes + 1 WHERE id = ?", (message_id,))
        conn.commit()
    return jsonify({"message": "liked"}), 200

@app.post("/api/messages/<int:message_id>/comments")
def create_comment(message_id):
    data = request.get_json()
    commenter_name = data.get("name", "").strip()
    comment_text = data.get("text", "").strip()

    if not commenter_name or not comment_text:
        return jsonify({"error": "name and text are required"}), 400

    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO comments (message_id, commenter_name, comment_text, created_at) VALUES (?, ?, ?, ?)",
            (message_id, commenter_name, comment_text, created_at)
        )
        conn.commit()

    return jsonify({"message": "comment added"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)