from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    user = update.effective_user
    msg = sd.join_player(user.id, user.username or user.full_name)
    await update.message.reply_text(msg["message"])

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    user = update.effective_user
    status_text = sd.get_player_status(user.id)
    await update.message.reply_text(status_text, parse_mode="Markdown")

def register_player_handlers(app):
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("status", status))
