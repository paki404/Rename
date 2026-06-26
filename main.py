import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

START_TEXT = """
**Welcome to RENAME Bot!**

I can help you rename files with smart numbering and advanced renaming tools.

**Features:**
• Auto-numbering for duplicate names (01, 02, ...)
• Rename types: Full, Prefix, Suffix 
• Extension handling options
• Word replacement

**Commands:**
/start - Show this message
/help - View detailed help
/settings - User settings panel
/rename - Start rename operation
/accounts - Manage accounts

Get started by pressing a button below 👇
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📂 Accounts", callback_data="accounts"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ],
        [InlineKeyboardButton("Made by You", url="https://t.me/yourusername")] # Link apna daal do
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(START_TEXT, reply_markup=reply_markup, parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("**/help** - Detailed help yahan aayega.\n**/rename** - File bhej kar naam change karo.\n**/settings** - Apni settings set karo.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "accounts":
        await query.edit_message_text("**/accounts** - Yahan apna MEGA ya doosra account link karo.")
    elif query.data == "settings":
        await query.edit_message_text("**/settings** - Rename style: Prefix/Suffix/Full choose karo.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("settings", help_cmd))
    app.add_handler(CommandHandler("rename", help_cmd)) 
    app.add_handler(CommandHandler("accounts", help_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot running...")
    app.run_polling()