import logging
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)

logger = logging.getLogger("PlayerHandler")

# ---------------------------------------------------------------------------
# Comando /start
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra mensaje de bienvenida."""
    await update.message.reply_text(
        "🧙‍♂️ Bienvenido a SAM The Dungeon Bot\n"
        "DM automático para campañas SRD 5.1.2.\n\n"
        "Comandos principales:\n"
        "• /createcharacter – crear tu personaje\n"
        "• /join – unirte a la campaña\n"
        "• /scene – mostrar o continuar la escena\n"
        "• /status – ver tu estado actual\n"
        "• /progress – ver progreso de la campaña\n\n"
        "Versión estable: 7.9 – Integración narrativa funcional"
    )


# ---------------------------------------------------------------------------
# Comandos /status, /progress, /scene
# ---------------------------------------------------------------------------
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    story_director = context.application.bot_data.get("story_director")
    if not story_director:
        await update.message.reply_text("⚠️ El sistema no está listo todavía.")
        return

    data = story_director.get_player_status(update.effective_user.id)
    if not data["found"]:
        await update.message.reply_text(f"❌ {data['message']}")
    else:
        player = data["player"]
        await update.message.reply_text(
            f"📜 *{player['name']}* – Nivel {player['level']} {player['class']} ({player['race']})\n"
            f"Estado emocional actual: {data['emotion']}",
            parse_mode="Markdown",
        )


async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    story_director = context.application.bot_data.get("story_director")
    if not story_director:
        await update.message.reply_text("⚠️ El sistema no está listo todavía.")
        return

    progress = story_director.get_campaign_progress()
    scene_title = progress.get("active_scene_title", "Sin escena activa")
    await update.message.reply_text(
        f"📖 *Campaña:* {progress['campaign']}\n"
        f"🗺️ *Capítulo:* {progress['chapter']}\n"
        f"🎭 *Escena actual:* {scene_title}\n"
        f"👥 *Jugadores:* {', '.join(progress['players'].values()) or 'Ninguno'}",
        parse_mode="Markdown",
    )


async def scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    story_director = context.application.bot_data.get("story_director")
    if not story_director:
        await update.message.reply_text("⚠️ El sistema no está listo todavía.")
        return

    data = story_director.get_current_scene()
    if not data["found"]:
        await update.message.reply_text(f"⚠️ {data['message']}")
    else:
        await update.message.reply_text(data["narrated"], parse_mode="Markdown")


# ---------------------------------------------------------------------------
# Registro de handlers
# ---------------------------------------------------------------------------
def register_player_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("progress", progress))
    application.add_handler(CommandHandler("scene", scene))
    logger.info("[PlayerHandler] Comandos /start, /status, /progress y /scene registrados.")
