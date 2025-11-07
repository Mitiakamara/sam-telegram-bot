import os
import logging
import asyncio

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Handlers de jugador (status, progress, scene)
from core.handlers.player_handler import register_player_handlers

# Si tienes otros handlers separados, los puedes importar aquí
# from core.handlers.admin_handler import register_admin_handlers
# from core.handlers.game_handler import register_game_handlers

# ================================================================
# 🔧 LOGGING
# ================================================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("SAM-Bot")


# ================================================================
# ⚙️ CONFIG
# ================================================================
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# ================================================================
# 🧠 HANDLERS BÁSICOS
# ================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start – mensaje de bienvenida
    """
    text = (
        "🧙‍♂️ Bienvenido a SAM The Dungeon Bot\n"
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
        "Versión estable: 7.7-clean SRD 5.1.2"
    )
    await update.message.reply_text(text)


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /join – aquí normalmente vinculas al usuario con la campaña activa.
    En tu proyecto real esto lo hace el CampaignManager + StoryDirector.
    Aquí dejo una versión mínima.
    """
    user = update.effective_user
    # Aquí es donde en tu repo llamas al campaign_manager para añadir al player
    # Por ahora solo respondemos:
    await update.message.reply_text(f"✅ {user.first_name} se unió a la campaña.")


async def createcharacter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /createcharacter – en tu proyecto esto dispara el flujo del CharacterBuilder
    que ya tienes en core/character_builder/.
    Aquí dejo una versión placeholder para que no truene.
    """
    # Si ya tienes un handler dedicado, sustitúyelo aquí.
    await update.message.reply_text(
        "🧙‍♂️ Vamos a crear tu personaje.\n\n¿Cómo se llamará?"
    )
    # Aquí normalmente guardarías en context.user_data["state"] = "creating_character"
    # y el siguiente MessageHandler recogería el nombre, etc.


# ================================================================
# 🏁 MAIN
# ================================================================
async def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN no está definido en el entorno.")

    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers básicos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("createcharacter", createcharacter))

    # 🔗 Enganche que me pediste
    register_player_handlers(application)

    # Si tienes más registros, van aquí:
    # register_admin_handlers(application)
    # register_game_handlers(application)

    logger.info("🤖 SAM The Dungeon Bot iniciado correctamente.")
    logger.info("Esperando comandos en Telegram...")

    # Modo polling (como muestran tus logs)
    await application.run_polling(close_loop=False)


if __name__ == "__main__":
    asyncio.run(main())
