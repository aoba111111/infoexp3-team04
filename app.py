from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone

app = Flask(__name__)

# メモリ上にメッセージを保存するリスト（テスト用）
messages = [
    {
        "id": 1,
        "name": "api-test",
        "message": "Hello API",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

@app.route('/')
def index():
    return render_template('index.html')

# 投稿一覧を取得するAPI (GET)
@app.get("/api/messages")
def get_messages():
    return jsonify(messages)

# 新規投稿を登録するAPI (POST)
@app.post("/api/messages")
def create_message():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    name = data.get("name", "").strip()
    message = data.get("message", "").strip()

    # 1. 必須チェック（名前和メッセージが空の場合）
    if not name or not message:
        return jsonify({"error": "name and message are required"}), 400

    # 2. 禁止ワード（うんこ）のチェック
    forbidden_word = "うんこ"
    if forbidden_word in name or forbidden_word in message:
        return jsonify({"error": "禁止ワードが含まれているため投稿できません"}), 400

    # 3. 新しい投稿データの作成と追加
    new_msg = {
        "id": len(messages) + 1,
        "name": name,
        "message": message,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    messages.append(new_msg)

    return jsonify(new_msg), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)