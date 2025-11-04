# ================================================================
# 🤖 SAM The Dungeon Bot – main.py
# Versión: 7.6.2 (SRD 5.1.2)
# ================================================================
# Punto de entrada del bot de Telegram.
# Rol:
#   - Actuar como Dungeon Master AI para campañas SRD 5.1.2 precreadas
#   - Coordinar escenas, emociones y tono narrativo (StoryDirector)
#   - Integrar la creación de personajes SRD (Character Builder)
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
# 📦 CORE IMPORTS
# ---------------------------------------------------------------
from core.story_director import StoryDirector
from core.character_builder.builder import (
    start_character_creation,
    handle_response,
    handle_callback
)

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("SAM-Bot")

# ================================================================
# 🧠 HANDLER: /start
# ================================================================
async def start(update, context):
    """
    Mensaje de bienvenida y comandos principales.
    """
    text = (
        "🧙‍♂️ *Bienvenido a SAM The Dungeon Bot*\n"
        "DM automático para campañas SRD 5.1.2.\n\n"
        "Comandos principales:\n"
        "• /createcharacter – crear tu personaje paso a paso\n"
        "• /join – unirte a la campaña activa\n"
        "• /scene – mostrar o continuar la escena actual\n"
        "• /event <tipo> – ejecutar un evento narrativo (p.ej. combat_victory)\n"
        "• /status – ver tu estado y emoción actual\n"
        "• /progress – ver el estado general de la campaña\n"
        "• /restart – reiniciar la campaña actual\n"
        "• /loadcampaign <slug> – (admin) cargar otra campaña SRD\n\n"
        "_Versión estable: 7.6.2 SRD 5.1.2_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# 🚀 FUNCIÓN PRINCIPAL
# ================================================================
def main():
    """
    Inicia la aplicación de Telegram.
    Crea una instancia global del StoryDirector y registra los handlers.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ Falta TELEGRAM_BOT_TOKEN en tu archivo .env")

    # Instancia principal del motor narrativo
    story_director = StoryDirector()

    # Construcción del bot
    app = ApplicationBuilder().token(token).build()

    # Guardamos el StoryDirector global en bot_data
    app.bot_data["story_director"] = story_director

    # ------------------------------------------------------------
    # REGISTRO DE HANDLERS
    # ------------------------------------------------------------
    # Comandos base
    app.add_handler(CommandHandler("start", start))

    # Character Builder (flujo guiado SRD 5.1.2)
    app.add_handler(CommandHandler("createcharacter", start_character_creation))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))
    app.add_handler(CallbackQueryHandler(handle_callback))

    # ------------------------------------------------------------
    # INICIO DEL BOT
    # ------------------------------------------------------------
    logger.info("🤖 SAM The Dungeon Bot iniciado correctamente.")
    logger.info("Esperando comandos en Telegram...")
    app.run_polling()


# ================================================================
# 💫 PUNTO DE ENTRADA
# ================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Error crítico en SAM: {e}")
        raise
