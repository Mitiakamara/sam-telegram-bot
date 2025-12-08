# ================================================================
# 🎬 NARRATIVE HANDLER
# ================================================================
# Controla los comandos narrativos:
#   /scene – muestra o continúa la escena actual
#   /event <tipo> – ejecuta un evento narrativo
# ================================================================

import logging
from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("[NarrativeHandler] /scene command received")
    sd = context.bot_data.get("story_director")
    if not sd:
        logger.error("[NarrativeHandler] StoryDirector not found in bot_data")
        await update.message.reply_text("⚠️ Error: StoryDirector no disponible.")
        return
    
    logger.info("[NarrativeHandler] Calling render_current_scene()")
    result = sd.render_current_scene()
    logger.info(f"[NarrativeHandler] render_current_scene returned: {result[:100]}...")
    await update.message.reply_text(result, parse_mode="Markdown")

async def event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    if not context.args:
        await update.message.reply_text(
            "Usa: `/event <tipo>` (ej: `/event combat_victory`)", parse_mode="Markdown"
        )
        return
    result = sd.trigger_event(context.args[0])
    await update.message.reply_text(result, parse_mode="Markdown")

def register_narrative_handlers(app):
    app.add_handler(CommandHandler("scene", scene))
    app.add_handler(CommandHandler("event", event))
