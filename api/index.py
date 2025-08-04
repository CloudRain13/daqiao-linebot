# api/index.py

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, FollowEvent,
    TextSendMessage, StickerSendMessage, TemplateSendMessage,
    ButtonsTemplate, URIAction, FlexSendMessage
)
import os
import sys

# 初始化 Flask
app = Flask(__name__)

# 從環境變數讀取 channel secret 和 token
channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if channel_secret is None or channel_access_token is None:
    raise Exception("請設定 LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN 環境變數")

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/api", methods=['POST'])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    # Debug log
    print("[Headers]", request.headers, file=sys.stderr)
    print("[Body]", body, file=sys.stderr)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK", 200

@handler.add(FollowEvent)
def handle_follow(event):
    send_flex_menu(event.reply_token)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    token = event.reply_token

    if text in ["主選單", "menu", "Menu"]:
        send_flex_menu(token)
    elif text == "我要解謎":
        line_bot_api.reply_message(token, [
            TextSendMessage(text="準備好了嗎？傳出第一張貼圖開始解謎吧！"),
            StickerSendMessage(package_id="11537", sticker_id="52002734")
        ])
    elif text == "我要認識大橋":
        line_bot_api.reply_message(token, TextSendMessage(
            text="大橋社區位於彰化大村，擁有超過300年歷史的慈鳳宮、柑仔店、石笱大埤等特色景點，等你來探索！"
        ))
    elif text == "追蹤我們":
        line_bot_api.reply_message(token, TemplateSendMessage(
            alt_text='社群連結',
            template=ButtonsTemplate(
                title='追蹤我們',
                text='點選以下連結追蹤我們的社群平台：',
                actions=[
                    URIAction(label='Instagram', uri='https://www.instagram.com/你的IG'),
                    URIAction(label='Facebook', uri='https://www.facebook.com/你的FB')
                ]
            )
        ))
    else:
        line_bot_api.reply_message(token, TextSendMessage(text="請點選主選單或輸入「主選單」～"))

def send_flex_menu(token):
    flex = FlexSendMessage(
        alt_text="主選單",
        contents={
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://i.imgur.com/OWcHzpD.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "歡迎來到大橋社區！", "weight": "bold", "size": "xl"},
                    {"type": "text", "text": "請選擇你想進行的項目：", "size": "sm", "color": "#888888"}
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {"type": "button", "style": "primary", "action": {"type": "message", "label": "🎩 參加解謎", "text": "我要解謎"}},
                    {"type": "button", "style": "secondary", "action": {"type": "message", "label": "📍 認識大橋", "text": "我要認識大橋"}},
                    {"type": "button", "style": "link", "action": {"type": "uri", "label": "🔗 IG / FB", "uri": "https://linktr.ee/你的社群連結"}}
                ]
            }
        }
    )
    line_bot_api.reply_message(token, flex)

# Vercel 部署需要這行
app = app
