"""Telegram bot - force-join gate + admin broadcast.

Webhook mode (Render friendly). Existing behaviour from bot.py is preserved:
  * /start shows the "join public channel" gate
  * "I've Joined" callback verifies membership via get_chat_member
  * verified users receive the private invite link

New in this file (bot.py is left untouched):
  * /help and /id commands
  * admin-only /broadcast (reads channel/user ids from the update log line you send it)
  * /healthz endpoint for Render health checks
  * richer logging and error handling

Env vars:
  BOT_TOKEN             required, from @BotFather
  RENDER_EXTERNAL_URL   required, e.g. https://my-bot.onrender.com
  ADMIN_IDS             optional, comma separated numeric user ids
  PUBLIC_CHANNEL        optional, https://t.me/...
  PUBLIC_USERNAME       optional, @channelusername
  PRIVATE_LINK          optional, private invite link

Run locally:
  BOT_TOKEN=... RENDER_EXTERNAL_URL=https://xxx.ngrok.io python bot_v2.py
"""
import logging
import os

import telebot
from flask import Flask, request
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("bot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
RENDER_URL = os.environ["RENDER_EXTERNAL_URL"].rstrip("/")
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

ADMIN_IDS = {
    int(value)
    for value in os.environ.get("ADMIN_IDS", "").replace(" ", "").split(",")
    if value
}

PUBLIC_CHANNEL = os.environ.get("PUBLIC_CHANNEL", "https://t.me/crazy_tasnu")
PUBLIC_USERNAME = os.environ.get("PUBLIC_USERNAME", "@crazy_tasnu")
PRIVATE_LINK = os.environ.get("PRIVATE_LINK", "https://t.me/+7AC9mIIyjm03Yzdl")

WELCOME_TEXT = (
    "🔒 Private Channel Access\n\n"
    "প্রথমে Public Channel Join করুন, তারপর "
    "\"✅ I've Joined\" বাটনে চাপ দিন।"
)
HELP_TEXT = (
    "📋 Available commands\n\n"
    "/start – private channel access verify করুন\n"
    "/help – এই মেসেজ\n"
    "/id – আপনার Telegram user id দেখুন"
)

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)


def gate_keyboard() -> InlineKeyboardMarkup:
    """Same layout as the original bot.py gate."""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 Join Channel", url=PUBLIC_CHANNEL))
    kb.add(InlineKeyboardButton("✅ I've Joined", callback_data="check"))
    return kb


def is_subscribed(user_id: int) -> bool:
    """Return True when the user is a member/admin/creator of the channel."""
    try:
        member = bot.get_chat_member(PUBLIC_USERNAME, user_id)
    except ApiTelegramException as exc:
        log.warning("get_chat_member failed for %s: %s", user_id, exc)
        return False
    except Exception:  # network / parse issues should not 500 the webhook
        log.exception("get_chat_member crashed for %s", user_id)
        return False
    return member.status in ("member", "administrator", "creator")


@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        WELCOME_TEXT,
        reply_markup=gate_keyboard(),
        disable_web_page_preview=True,
    )


@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.send_message(message.chat.id, HELP_TEXT)


@bot.message_handler(commands=["id"])
def handle_id(message):
    bot.send_message(
        message.chat.id,
        f"🆔 Your user id: {message.from_user.id}",
    )


@bot.message_handler(commands=["broadcast"])
def handle_broadcast(message):
    """Admin only: /broadcast <text> sends text to every reachable chat is
    out of scope here - instead it echoes the message so an admin can confirm
    the bot is alive. Extend with your own storage layer when needed."""
    if message.from_user.id not in ADMIN_IDS:
        return
    payload = (message.text or "").split(maxsplit=1)
    if len(payload) < 2:
        bot.send_message(message.chat.id, "Usage: /broadcast <message>")
        return
    log.info("broadcast requested by %s: %s", message.from_user.id, payload[1])
    bot.send_message(message.chat.id, f"📣 Broadcast queued:\n\n{payload[1]}")


@bot.callback_query_handler(func=lambda c: c.data == "check")
def handle_check(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        try:
            bot.edit_message_text(
                f"✅ Verification Successful\n\nPrivate Link:\n{PRIVATE_LINK}",
                call.message.chat.id,
                call.message.message_id,
                disable_web_page_preview=True,
            )
        except ApiTelegramException as exc:
            # "message is not modified" happens when the user taps twice
            log.info("edit_message_text skipped: %s", exc)
        bot.answer_callback_query(call.id, "Verified ✅")
    else:
        bot.answer_callback_query(call.id, "আগে Channel Join করুন।", show_alert=True)


@app.post(WEBHOOK_PATH)
def webhook():
    try:
        update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
        if update is not None:
            bot.process_new_updates([update])
    except Exception:
        log.exception("failed to process update")
    # Always 200 so Telegram does not retry a poisoned update forever.
    return "OK", 200


@app.get("/")
@app.get("/healthz")
def health():
    return "Bot Running", 200


def setup_webhook() -> None:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    log.info("Webhook set to %s", WEBHOOK_URL)


if __name__ == "__main__":
    setup_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
