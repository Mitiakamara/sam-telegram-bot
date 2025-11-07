# ================================================================
# 🤖 SAM The Dungeon Bot – main.py
# Versión: 7.7-clean (SRD 5.1.2)
# ================================================================
# Entry point del bot de Telegram.
# Integra:
#   - StoryDirector (motor narrativo)
#   - Character Builder (creación guiada de PJ)
#   - Handlers modulares para campaña, jugador y narrativa
# ================================================================

import os
import logging
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# ---------------------------------------------------------------
# 📦 Core imports
# ---------------------------------------------------------------
from core.story_director import StoryDirector
from core.character_builder.builder import (
    start_character_creation,
    handle_response,
    handle_callback,
)
from core.handlers.campaign_handler import register_campaign_handlers
from core.handlers.player_handler import register_player_handlers
from core.handlers.narrative_handler import register_narrative_handlers

# ---------------------------------------------------------------
# ⚙️ Configuración básica
# ---------------------------------------------------------------
load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("SAM-Bot")

# ================================================================
# 🧙‍♂️ Handler: /start
# ================================================================
async def start(update, context):
    text = (
        "🧙‍♂️ *Bienvenido a SAM The Dungeon Bot*\n"
        "DM automático para campañas SRD 5.1.2.\n\n"
        "Comandos principales:\n"
        "• /createcharacter – crear tu personaje paso a paso\n"
        "• /join – unirte a la campaña activa\n"
        "• /scene – mostrar o continuar la escena actual\n"
        "• /event <tipo> – ejecutar un evento narrativo\n"
        "• /status – ver tu estado actual\n"
        "• /progress – ver progreso de la campaña\n"
        "• /restart – reiniciar la campaña\n"
        "• /loadcampaign <slug> – (admin) cambiar de campaña\n\n"
        "_Versión estable: 7.7-clean SRD 5.1.2_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# 🚀 Función principal
# ================================================================
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ Falta TELEGRAM_BOT_TOKEN en tu archivo .env")

    story_director = StoryDirector()

    app = ApplicationBuilder().token(token).build()
    app.bot_data["story_director"] = story_director

    # ------------------------------------------------------------
    # Registro de comandos base
    # ------------------------------------------------------------
    app.add_handler(CommandHandler("start", start))

    # ------------------------------------------------------------
    # Character Builder (flujo guiado SRD 5.1.2)
    # ------------------------------------------------------------
    app.add_handler(CommandHandler("createcharacter", start_character_creation))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))
    app.add_handler(CallbackQueryHandler(handle_callback))

    # ------------------------------------------------------------
    # Handlers modulares
    # ------------------------------------------------------------
    register_campaign_handlers(app)
    register_player_handlers(app)
    register_narrative_handlers(app)

    # ------------------------------------------------------------
    # Inicio del bot
    # ------------------------------------------------------------
    logger.info("🤖 SAM The Dungeon Bot iniciado correctamente.")
    logger.info("Esperando comandos en Telegram...")
    app.run_polling()

# ================================================================
# 💫 Punto de entrada
# ================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Error crítico en SAM: {e}")
        raise
