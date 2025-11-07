from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

async def scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    result = sd.render_current_scene()
    await update.message.reply_text(result, parse_mode="Markdown")

async def event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    if not context.args:
        await update.message.reply_text("Usa: `/event <tipo>` (ej: `/event combat_victory`)", parse_mode="Markdown")
        return
    result = sd.trigger_event(context.args[0])
    await update.message.reply_text(result, parse_mode="Markdown")

def register_narrative_handlers(app):
    app.add_handler(CommandHandler("scene", scene))
    app.add_handler(CommandHandler("event", event))
