import os, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ConversationHandler, ContextTypes, filters
)
from mega import Mega

BOT_TOKEN = os.getenv("BOT_TOKEN")
GET_EMAIL, GET_PASS, CHOOSE_TYPE, GET_TEXT, WAITING_FILE = range(5)

START_TEXT = """
**Welcome to RENAME Bot!**

**Features:** Prefix, Suffix, MEGA Login
**Commands:** /start /help /settings /rename /accounts

"""

def save_session(uid, session):
    with open(f"{uid}.json", "w") as f: json.dump(session, f)

def load_mega(uid):
    if os.path.exists(f"{uid}.json"):
        with open(f"{uid}.json", "r") as f: session = json.load(f)
        return Mega().login(email=None, password=None, session=session)
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📂 Accounts", callback_data="accounts"), InlineKeyboardButton("⚙️ Settings", callback_data="settings")]]
    await update.message.reply_text(START_TEXT, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    if query.data == "accounts": await query.edit_message_text("MEGA link karne ke liye /accounts likho.")
    elif query.data == "settings": await query.edit_message_text("Default Prefix/Suffix yahan set hoga.")

# --- MEGA LOGIN ---
async def accounts_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Step 1/2: MEGA ka Email bhejo 👇"); return GET_EMAIL
async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text; await update.message.delete()
    await update.message.reply_text("Step 2/2: Ab Password bhejo. Delete ho jayega."); return GET_PASS
async def get_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email, password = context.user_data['email'], update.message.text; await update.message.delete()
    try:
        m = Mega().login(email, password); save_session(update.effective_user.id, m.session_id)
        await update.message.reply_text("✅ MEGA Login ho gaya!"); return ConversationHandler.END
    except: await update.message.reply_text("❌ Login fail. Dobara /accounts try karo."); return ConversationHandler.END

# --- RENAME LOGIC ---
async def rename_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not load_mega(update.effective_user.id):
        await update.message.reply_text("Pehle /accounts se MEGA login karo."); return ConversationHandler.END
    keyboard = [[InlineKeyboardButton("Prefix", callback_data="type_prefix"), InlineKeyboardButton("Suffix", callback_data="type_suffix")]]
    await update.message.reply_text("Rename type choose karo:", reply_markup=InlineKeyboardMarkup(keyboard)); return CHOOSE_TYPE

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    context.user_data['type'] = query.data.split("_")[1]
    await query.edit_message_text(f"{context.user_data['type'].title()} mode ✅\nAb text bhejo: `HD_` ya `_2026`"); return GET_TEXT

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['text'] = update.message.text
    await update.message.reply_text("Ok. Ab MEGA link bhejo ya Telegram file bhejo 👇"); return WAITING_FILE

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mega = load_mega(update.effective_user.id); doc = update.message.document
    if not doc: return
    old_name, text, rtype = doc.file_name, context.user_data['text'], context.user_data['type']
    name, ext = os.path.splitext(old_name)
    new_name = f"{text}{name}{ext}" if rtype == 'prefix' else f"{name}{text}{ext}"
    file = await context.bot.get_file(doc.file_id); await file.download_to_drive(new_name)
    await update.message.reply_document(document=open(new_name, 'rb'), caption=f"✅ `{old_name}` → `{new_name}`", parse_mode="Markdown")
    os.remove(new_name); return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancel."); return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    acc_conv = ConversationHandler(entry_points=[CommandHandler("accounts", accounts_start)], states={GET_EMAIL:[MessageHandler(filters.TEXT, get_email)], GET_PASS:[MessageHandler(filters.TEXT, get_pass)]}, fallbacks=[CommandHandler("cancel", cancel)])
    ren_conv = ConversationHandler(entry_points=[CommandHandler("rename", rename_start)], states={CHOOSE_TYPE:[CallbackQueryHandler(choose_type, pattern="^type_")], GET_TEXT:[MessageHandler(filters.TEXT, get_text)], WAITING_FILE:[MessageHandler(filters.Document.ALL, handle_file)]}, fallbacks=[CommandHandler("cancel", cancel)])
    app.add_handler(CommandHandler("start", start)); app.add_handler(CommandHandler("help", start)); app.add_handler(acc_conv); app.add_handler(ren_conv); app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot running..."); app.run_polling()