from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "YOUR_BOT_TOKEN"

PUBLIC_CHANNEL = "@crazy_tasnu"
PRIVATE_LINK = "https://t.me/+K4NnT9Xqs3dmNGU9"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(PUBLIC_CHANNEL, user_id)

        if member.status in ["member", "administrator", "creator"]:
            await update.message.reply_text(
                f"✅ আপনি চ্যানেলে Join করেছেন।\n\nPrivate Channel Link:\n{PRIVATE_LINK}"
            )
        else:
            await update.message.reply_text(
                f"❌ আগে {PUBLIC_CHANNEL} চ্যানেলে Join করুন।"
            )

    except Exception:
        await update.message.reply_text(
            f"❌ আগে {PUBLIC_CHANNEL} চ্যানেলে Join করুন।"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
