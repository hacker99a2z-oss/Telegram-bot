import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

TOKEN = os.environ["BOT_TOKEN"]

PUBLIC_CHANNEL = "https://t.me/crazy_tasnu"
PUBLIC_USERNAME = "@crazy_tasnu"

PRIVATE_LINK = "https://t.me/+K4NnT9Xqs3dmNGU9"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


def keyboard():
    kb = InlineKeyboardMarkup()

    kb.row(
        InlineKeyboardButton(
            "📢 Join Channel",
            url=PUBLIC_CHANNEL
        )
    )

    kb.row(
        InlineKeyboardButton(
            "✅ I've Joined",
            callback_data="check"
        )
    )

    return kb


@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(
        message.chat.id,
        "🔒 Private Channel Access\n\n"
        "প্রথমে Public Channel Join করুন।",
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

                call.message.chat.id,

                call.message.message_id

            )

        else:

            bot.answer_callback_query(
                call.id,
                "আগে Channel Join করুন।",
                show_alert=True
            )

    except:

        bot.answer_callback_query(
            call.id,
            "আগে Channel Join করুন।",
            show_alert=True
        )


@app.route("/" + TOKEN, methods=["POST"])
def webhook():

    json_str = request.get_data().decode("utf-8")

    update = telebot.types.Update.de_json(json_str)

    bot.process_new_updates([update])

    return "OK", 200


@app.route("/")
def home():
    return "Bot Running"


if __name__ == "__main__":

    bot.remove_webhook()

    url = os.environ["RENDER_EXTERNAL_URL"]

    bot.set_webhook(url=f"{url}/{TOKEN}")

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
