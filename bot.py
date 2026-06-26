import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from mega import Mega

BOT_TOKEN = os.getenv("BOT_TOKEN")
MEGA_EMAIL = os.getenv("MEGA_EMAIL") 
MEGA_PASS = os.getenv("MEGA_PASS")

user_data = {} # {user_id: {'mode': 'prefix', 'files': []}}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot On hai\nMujhe MEGA folder ka link bhejo.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user.id
    link = update.message.text
    if 'mega.nz/folder/' not in link:
        return await update.message.reply_text("Sahi MEGA folder link bhejo.")
    
    await update.message.reply_text("⏳ Folder scan kar raha hun...")
    try:
        mega = Mega().login(MEGA_EMAIL, MEGA_PASS)
        files = mega.get_files_from_folder(mega.find(link.split('/')[-1].split('#')[0]))
        user_data[u] = {'files': files, 'link': link}
        
        keyboard = [[
            InlineKeyboardButton("Prefix", callback_data='prefix'),
            InlineKeyboardButton("Suffix", callback_data='suffix')
        ]]
        await update.message.reply_text(f"704 files mil gayi. Kya lagana hai?", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    u = query.from_user.id
    await query.answer()
    user_data[u]['mode'] = query.data # 'prefix' or 'suffix'
    await query.edit_message_text("Theek hai. Ab Prefix/Suffix likh ke bhejo. Ex: Videohd_")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user.id
    if u not in user_data or 'mode' not in user_data[u]: return
    
    text = update.message.text
    mode = user_data[u]['mode']
    files = user_data[u]['files']
    
    await update.message.reply_text(f"⏳ Kaam shuru... {len(files)} files rename ho rahi hain. 5-10 min lagega.")
    
    mega = Mega().login(MEGA_EMAIL, MEGA_PASS)
    for i, (node_id, file_info) in enumerate(files.items()):
        old_name = file_info['name']
        if mode == 'prefix':
            new_name = f"{text}{i+1}{os.path.splitext(old_name)[1]}"
        else:
            name, ext = os.path.splitext(old_name)
            new_name = f"{name}{text}{ext}"
        
        try:
            mega.rename(node_id, new_name)
            await asyncio.sleep(0.5) # MEGA block na kare
        except: pass
            
    await update.message.reply_text("✅ Ho gaya bhai. Sab rename ho gaye.")
    del user_data[u]

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)) # Link pakrega
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)) # Text pakrega
    app.add_handler(CallbackQueryHandler(button))
    print("🔥 Bot On hai")
    app.run_polling()

if __name__ == '__main__':
    main()
