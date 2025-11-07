import logging
from telegram import Update
from telegram.ext import ContextTypes

# Importamos el StoryDirector central
from core.story_director.story_director import StoryDirector

logger = logging.getLogger("PlayerHandler")

# instancia única para este handler
story_director = StoryDirector()


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /status – muestra el estado del personaje que está hablando.
    """
    try:
        user = update.effective_user
        user_id = user.id

        status_text = story_director.get_player_status(user_id)
        await update.message.reply_text(status_text, parse_mode="Markdown")

    except Exception as e:
        logger.exception(f"[PlayerHandler] Error en /status: {e}")
        await update.message.reply_text(
            "⚠️ Ocurrió un error al obtener tu estado. Intenta de nuevo."
        )


async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /progress – muestra el estado de la campaña actual.
    """
    try:
        progress_text = story_director.get_campaign_progress()
        await update.message.reply_text(progress_text, parse_mode="Markdown")
    except Exception as e:
        logger.exception(f"[PlayerHandler] Error en /progress: {e}")
        await update.message.reply_text(
            "⚠️ Ocurrió un error al obtener el progreso de la campaña."
        )


async def scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /scene – muestra o genera la escena actual dependiendo del estado.
    """
    try:
        current_scene = story_director.get_current_scene()
        if not current_scene:
            await update.message.reply_text("No hay ninguna escena activa.")
            return

        # Genera una versión adaptada con el tono/emoción actual
        description = story_director.generate_scene_description()
        await update.message.reply_text(description)
    except Exception as e:
        logger.exception(f"[PlayerHandler] Error en /scene: {e}")
        await update.message.reply_text(
            "⚠️ No pude mostrar la escena actual."
        )


# Opcional: si quieres un helper para registrar rápido en main.py
def register_player_handlers(application):
    """
    Helper para main.py:
        from core.handlers.player_handler import register_player_handlers
        register_player_handlers(application)
    """
    from telegram.ext import CommandHandler

    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("progress", progress))
    application.add_handler(CommandHandler("scene", scene))
    logger.info("[PlayerHandler] Comandos /status, /progress y /scene registrados.")
