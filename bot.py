import os
import logging
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

PUBLIC_CHANNEL = "https://t.me/crazy_tasnu"
PUBLIC_USERNAME = "@crazy_tasnu"

PRIVATE_LINK = "https://t.me/+K4NnT9Xqs3dmNGU9"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)


def keyboard():
    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton(
            "📢 Join Channel",
            url=PUBLIC_CHANNEL
        )
    )

    kb.add(
        InlineKeyboardButton(
            "✅ I've Joined",
            callback_data="check"
        )
    )

    return kb


@bot.message_handler(commands=["start"])
def start(message):
    print("START COMMAND RECEIVED")

    bot.send_message(
        message.chat.id,
        "🔒 *Private Channel Access*\n\n"
        "প্রথমে নিচের Public Channel Join করুন।",
        parse_mode="Markdown",
        reply_markup=keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):

    try:

        member = bot.get_chat_member(
            PUBLIC_USERNAME,
            call.from_user.id
        )

        if member.status in [
            "member",
            "administrator",
            "creator"
        ]:

            bot.edit_message_text(
                "✅ Verification Successful\n\n"
                f"Private Link:\n{PRIVATE_LINK}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )

        else:

            bot.answer_callback_query(
                call.id,
                "আগে Channel Join করুন।",
                show_alert=True
            )

    except Exception as e:

        print(e)

        bot.answer_callback_query(
            call.id,
            "Verification Failed",
            show_alert=True
        )
        @app.route("/" + TOKEN, methods=["POST"])
def webhook():
    try:
        json_str = request.get_data().decode("utf-8")

        update = telebot.types.Update.de_json(json_str)

        bot.process_new_updates([update])

    except Exception as e:
        print("Webhook Error:", e)

    return "OK", 200


@app.route("/")
def home():
    return "Bot Running", 200


def set_webhook():
    try:
        bot.remove_webhook()

        webhook_url = f"{RENDER_URL}/{TOKEN}"

        bot.set_webhook(url=webhook_url)

        print("Webhook Set:", webhook_url)

    except Exception as e:
        print("Webhook Error:", e)


# Gunicorn চালু হলে এই কোড একবার execute হবে
set_webhook()
