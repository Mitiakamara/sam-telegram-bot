import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from core.handlers.createcharacter_handler import register_createcharacter_conversation

logger = logging.getLogger("PlayerHandler")

def register_player_handlers(application, campaign_manager):
    """
    Registra los comandos básicos del jugador.
    """
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = (
            "🧙‍♂️ Bienvenido a *SAM The Dungeon Bot*\n"
            "DM automático para campañas SRD 5.1.2.\n\n"
            "Comandos principales:\n"
            "• /createcharacter – crear tu personaje\n"
            "• /join – unirte a la campaña\n"
            "• /scene – mostrar o continuar la escena\n"
            "• /status – ver tu estado actual\n"
            "• /progress – ver progreso de la campaña\n\n"
            "_Versión estable: 7.9 – Integración narrativa funcional_"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        player = campaign_manager.get_player(user.id)
        if player:
            await update.message.reply_text(f"🎭 Ya estás en la campaña como {player['name']}.")
        else:
            await update.message.reply_text("⚠️ No tienes personaje aún. Usa /createcharacter primero.")

    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        player = campaign_manager.get_player(user.id)
        if not player:
            await update.message.reply_text("❌ No se encontró tu personaje.")
            return
        stats = "\n".join([f"{k}: {v}" for k, v in player["attributes"].items()])
        await update.message.reply_text(f"📊 Estado de {player['name']}:\n{stats}")

    async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
        scene = campaign_manager.get_current_scene()
        if not scene:
            await update.message.reply_text("⚠️ No hay progreso disponible aún.")
        else:
            await update.message.reply_text(f"📖 Escena actual: {scene['title']}\n{scene['description']}")

    # Registro de handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("progress", progress))

    # Registro del flujo de creación
    register_createcharacter_conversation(application, campaign_manager)

    logger.info("[PlayerHandler] Comandos /start, /createcharacter, /join, /status, /progress registrados.")
