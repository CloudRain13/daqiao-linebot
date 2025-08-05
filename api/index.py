import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FollowEvent, FlexSendMessage
)

app = Flask(__name__)

# 從環境變數讀取憑證
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if channel_secret is None or channel_access_token is None:
    raise Exception("❗請確認 Vercel 上有設定環境變數")

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/api", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    print("✅ Webhook received!")
    print(f"[Body] {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK", 200

# 加入好友事件
@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="感謝加入大橋解謎遊戲 🧩 傳送貼圖即可開始遊戲！")
    )

# 文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    reply_token = event.reply_token

    if user_text in ["主選單", "menu", "Menu"]:
        send_flex_menu(reply_token)
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="請輸入「主選單」來查看功能喔～"))

# 傳送主選單 Flex Message
def send_flex_menu(reply_token):
    flex = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                { "type": "text", "text": "👋 歡迎來到大橋社區", "weight": "bold", "size": "xl" },
                { "type": "text", "text": "請選擇功能", "size": "sm", "color": "#aaaaaa" }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "action": { "type": "message", "label": "🔍 我要解謎", "text": "我要解謎" }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": { "type": "message", "label": "📍 認識大橋", "text": "我要認識大橋" }
                }
            ]
        }
    }

    line_bot_api.reply_message(
        reply_token,
        FlexSendMessage(alt_text="主選單", contents=flex)
    )
