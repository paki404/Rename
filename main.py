import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN") # Railway me env variable se lenge

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("hi kasai ho 👋") # Yahan tumhara text

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot running...")
    app.run_polling()