from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    summary = sd.get_campaign_progress()
    await update.message.reply_text(summary, parse_mode="Markdown")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    sd.restart_campaign()
    await update.message.reply_text("🔄 Campaña reiniciada desde el inicio.")

async def loadcampaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    if not context.args:
        await update.message.reply_text("Usa: `/loadcampaign <slug>`", parse_mode="Markdown")
        return
    slug = context.args[0]
    try:
        sd.load_campaign(slug)
        await update.message.reply_text(f"📦 Campaña cargada: *{slug}*", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error al cargar campaña: {e}")

def register_campaign_handlers(app):
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("loadcampaign", loadcampaign))
