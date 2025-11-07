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

# ================================================================
# 🔗 Importa los handlers del jugador (status, progress, scene)
# ================================================================
from core.handlers.player_handler import register_player_handlers


# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL Y LOGGING
# ================================================================
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("SAM-Bot")


# ================================================================
# 🤖 HANDLERS PRINCIPALES
# ================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start – Mensaje de bienvenida y lista de comandos.
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
    /join – Añade al usuario actual a la campaña activa.
    (Placeholder; en tu repo real se enlaza con CampaignManager)
    """
    user = update.effective_user
    await update.message.reply_text(f"✅ {user.first_name} se unió a la campaña.")


async def createcharacter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /createcharacter – Inicia la creación de personaje paso a paso.
    (Placeholder; se conecta con core/character_builder/builder.py)
    """
    await update.message.reply_text(
        "🧙‍♂️ Vamos a crear tu personaje.\n\n¿Cómo se llamará?"
    )


# ================================================================
# 🏁 MAIN ASÍNCRONO
# ================================================================
async def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN no está definido en el entorno.")

    # Inicializa la app
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers base
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("createcharacter", createcharacter))

    # Handlers de jugador (status, progress, scene)
    register_player_handlers(application)

    logger.info("🤖 SAM The Dungeon Bot iniciado correctamente.")
    logger.info("Esperando comandos en Telegram...")

    # Ejecuta en modo polling
    await application.run_polling(close_loop=False)


# ================================================================
# 🚀 EJECUCIÓN SEGURA (compatible con Render / Python 3.13)
# ================================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "already running" in str(e):
            logger.warning(
                "⚠️ Loop asyncio ya en ejecución. Usando loop existente (Render safe mode)."
            )
            try:
                # Python 3.13: preferir get_running_loop()
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # Si no existe, crear uno nuevo
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.create_task(main())
            loop.run_forever()
        else:
            raise
