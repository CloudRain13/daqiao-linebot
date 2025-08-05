# app.py
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage,
    StickerSendMessage, TextSendMessage, ImageSendMessage
)

app = Flask(__name__)

# ← 在環境變數或 .env 裡設定以下兩個
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler     = WebhookHandler('YOUR_CHANNEL_SECRET')

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 只針對文字訊息做處理
    if event.message.text == '大橋迷蹤':
        # 1. 一張貼圖
        sticker = StickerSendMessage(
            package_id='1',  # 範例貼圖套件 ID
            sticker_id='1'   # 範例貼圖貼圖 ID
        )
        # 2. 一段文字歡迎
        text = TextSendMessage(text='🎉 遊戲開始！請前往第一站：柑仔店。這是你的地圖：')
        # 3. 一張地圖圖卡（請先把 map1.png 放到公開網址）
        image = ImageSendMessage(
            original_content_url='https://your-domain.com/maps/map1.png',
            preview_image_url='https://your-domain.com/maps/map1.png'
        )
        return line_bot_api.reply_message(event.reply_token, [sticker, text, image])

if __name__ == "__main__":
    app.run(port=3000)
