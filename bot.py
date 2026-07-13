import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

TOKEN = os.environ["BOT_TOKEN"]
RENDER_URL = os.environ["RENDER_EXTERNAL_URL"]

PUBLIC_CHANNEL = "https://t.me/crazy_tasnu"
PUBLIC_USERNAME = "@crazy_tasnu"
PRIVATE_LINK = "https://t.me/+7AC9mIIyjm03Yzdl"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

def keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 Join Channel", url=PUBLIC_CHANNEL))
    kb.add(InlineKeyboardButton("✅ I've Joined", callback_data="check"))
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔒 Private Channel Access\n\nপ্রথমে Public Channel Join করুন।",
        reply_markup=keyboard()
    )

@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(c):
    try:
        m = bot.get_chat_member(PUBLIC_USERNAME, c.from_user.id)
        if m.status in ("member","administrator","creator"):
            bot.edit_message_text(
                f"✅ Verification Successful\n\nPrivate Link:\n{PRIVATE_LINK}",
                c.message.chat.id,
                c.message.message_id
            )
        else:
            bot.answer_callback_query(c.id,"আগে Channel Join করুন।",show_alert=True)
    except Exception as e:
        print(e)
        bot.answer_callback_query(c.id,"Verification failed.",show_alert=True)

@app.post("/" + TOKEN)
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK",200

@app.get("/")
def home():
    return "Bot Running",200

try:
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    print("Webhook set")
except Exception as e:
    print(e)
