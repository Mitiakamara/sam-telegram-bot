import logging
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Importa el manejador de creación interactiva
from core.handlers.createcharacter_handler import register_createcharacter_conversation

logger = logging.getLogger("PlayerHandler")


# ============================================================
#  HANDLERS PRINCIPALES DE JUGADOR
# ============================================================

def register_player_handlers(application, campaign_manager):
    """
    Registra los comandos principales del jugador:
    /start, /join, /status, /progress, /scene
    Y la conversación interactiva /createcharacter.
    """

    # ------------------------------------------------------------
    # /start
    # ------------------------------------------------------------
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    # ------------------------------------------------------------
    # /join
    # ------------------------------------------------------------
    async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        player = campaign_manager.get_player_by_telegram_id(user_id)
        if not player:
            await update.message.reply_text(
                "⚠️ No tienes un personaje creado.\nUsa /createcharacter antes de unirte a la aventura."
            )
            return
        await update.message.reply_text(f"🎲 {player['name']} se ha unido a la campaña.")
        campaign_manager.add_to_active_party(user_id)
        logger.info(f"[PlayerHandler] Jugador {player['name']} se unió a la campaña.")

    # ------------------------------------------------------------
    # /status
    # ------------------------------------------------------------
    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        player = campaign_manager.get_player_by_telegram_id(user_id)
        if not player:
            await update.message.reply_text("⚠️ No tienes un personaje creado aún.")
            return

        stats = player.get("attributes", {})
        msg = (
            f"📊 Estado de *{player['name']}*\n"
            f"Clase: {player['class']}, Raza: {player['race']}\n"
            f"Nivel: {player['level']}\n"
            f"Trasfondo: {player.get('background', 'Desconocido')}\n\n"
            f"Fuerza (STR): {stats.get('STR', 0)}\n"
            f"Destreza (DEX): {stats.get('DEX', 0)}\n"
            f"Constitución (CON): {stats.get('CON', 0)}\n"
            f"Inteligencia (INT): {stats.get('INT', 0)}\n"
            f"Sabiduría (WIS): {stats.get('WIS', 0)}\n"
            f"Carisma (CHA): {stats.get('CHA', 0)}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    # ------------------------------------------------------------
    # /progress
    # ------------------------------------------------------------
    async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chapter = campaign_manager.state.get("chapter", 1)
        current_scene = campaign_manager.state.get("current_scene", "Desconocida")
        await update.message.reply_text(
            f"📖 Progreso actual de la campaña:\n"
            f"Capítulo {chapter}: {current_scene}"
        )

    # ------------------------------------------------------------
    # /scene
    # ------------------------------------------------------------
    async def scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
        current_scene = campaign_manager.state.get("current_scene", "No hay escena activa.")
        await update.message.reply_text(f"🎭 Escena actual:\n{current_scene}")

    # ------------------------------------------------------------
    # REGISTRO DE HANDLERS
    # ------------------------------------------------------------
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("progress", progress))
    application.add_handler(CommandHandler("scene", scene))

    # conversación interactiva de creación de personaje
    register_createcharacter_conversation(application, campaign_manager)

    logger.info(
        "[PlayerHandler] Comandos /start, /createcharacter, /join, /status, /progress y /scene registrados."
    )
