# api/webhook.py
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, StickerSendMessage, TextSendMessage, ImageSendMessage
import serverless_wsgi

app = Flask(__name__)
app.logger.setLevel("INFO")

# 一定要在 Vercel Env 設好
LINE_TOKEN  = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_SECRET = os.environ["LINE_CHANNEL_SECRET"]
MAP1_URL    = os.environ.get("MAP1_URL", "https://daqiao-linebot.vercel.app/maps/map1.png")

line_bot_api = LineBotApi(LINE_TOKEN)
handler     = WebhookHandler(LINE_SECRET)

@app.route("/api/index", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body      = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        app.logger.error(f"處理 webhook 時發生錯誤: {e}", exc_info=True)
        # 回 200 讓 LINE 不會一直 retry，或改成 abort(500) 但至少要先 log
        return "OK", 200
    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        if event.message.text == "大橋迷蹤":
            sticker = StickerSendMessage(package_id="1", sticker_id="1")
            text    = TextSendMessage(text="🎉 遊戲開始！請前往第一站：柑仔店。這是你的地圖：")
            image   = ImageSendMessage(original_content_url=MAP1_URL, preview_image_url=MAP1_URL)
            line_bot_api.reply_message(event.reply_token, [sticker, text, image])
    except Exception as e:
        app.logger.error(f"handle_message 內發生錯誤: {e}", exc_info=True)

# 讓 Vercel 呼叫的入口函式，名稱必須是 handler
def handler(request, context):
    return serverless_wsgi.handle_request(app, request, context)


