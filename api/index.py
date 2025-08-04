from flask import Flask, request

app = Flask(__name__)

@app.route("/api", methods=["POST"])
def webhook():
    print("✅ Webhook received!")
    print(request.json)  # 觀察 LINE 傳來什麼
    return "OK", 200
