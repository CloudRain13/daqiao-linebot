from flask import Flask, request, abort
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    FollowEvent
)

app = Flask(__name__)

# 環境變數（請在 Vercel 上設定）
channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not channel_secret or not channel_access_token:
    raise Exception("❗請設定 LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# 使用者進度記錄（暫時存在記憶體，之後可改用資料庫）
user_stage = {}

# 之後可再填充
stage_prompts = {
    1: "🔍 第一關提示：XXX（待填）",
    2: "🔍 第二關提示：YYY（待填）",
}
stage_answers = {
    1: ["答案1", "ans1"],
    2: ["答案2", "ans2"],
}

@app.route("/api", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK", 200

@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    user_stage[user_id] = 1  # 新用戶從第一關開始
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="👋 歡迎加入大橋實境解謎！傳送「主選單」即可開始～")
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()
    reply_token = event.reply_token

    if msg in ["主選單", "menu", "Menu"]:
        send_main_menu(reply_token)
        return

    if msg == "我要解謎":
        stage = user_stage.get(user_id, 1)
        prompt = stage_prompts.get(stage, "🎉 所有關卡完成！")
        line_bot_api.reply_message(reply_token, TextSendMessage(text=prompt))
        return

    if msg == "我要認識大橋":
        send_intro(reply_token)
        return

    # 判斷答案是否正確
    stage = user_stage.get(user_id, 1)
    correct_answers = stage_answers.get(stage, [])
    if msg in correct_answers:
        user_stage[user_id] = stage + 1
        next_prompt = stage_prompts.get(stage + 1, "🎉 所有關卡完成，感謝參與！")
        line_bot_api.reply_message(reply_token, TextSendMessage(text="✅ 正確！\n\n" + next_prompt))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="❌ 不對喔～再想想！"))

# 傳送主選單
def send_main_menu(reply_token):
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text="請選擇：\n👉 我要解謎\n👉 我要認識大橋")
    )

# 認識大橋 Flex Message（可改成圖文式）
def send_intro(reply_token):
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text="📍 大橋社區是一個有豐富農業與文化的小鎮…（這段之後補）")
    )

