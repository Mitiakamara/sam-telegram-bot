import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from core.handlers.player_handler import register_player_handlers

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
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
    text = (
        "🧙‍♂️ Bienvenido a SAM The Dungeon Bot\n"
        "DM automático para campañas SRD 5.1.2.\n\n"
        "Comandos principales:\n"
        "• /createcharacter – crear tu personaje\n"
        "• /join – unirte a la campaña\n"
        "• /scene – mostrar o continuar la escena\n"
        "• /status – ver tu estado actual\n"
        "• /progress – ver progreso de la campaña\n\n"
        "Versión estable: 7.8 – Render Fix"
    )
    await update.message.reply_text(text)


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"✅ {user.first_name} se unió a la campaña.")


async def createcharacter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧙‍♂️ Vamos a crear tu personaje.\n\n¿Cómo se llamará?"
    )


# ================================================================
# 🏁 INICIALIZACIÓN DE LA APLICACIÓN
# ================================================================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN no está definido en el entorno.")

    application = Application.builder().token(BOT_TOKEN).build()

    # Comandos base
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("createcharacter", createcharacter))

    # Handlers de jugador
    register_player_handlers(application)

    logger.info("🤖 SAM The Dungeon Bot iniciado correctamente.")
    logger.info("Esperando comandos en Telegram...")

    # 🔧 Ejecución SIN asyncio.run() — evita el conflicto del loop
    application.run_polling(close_loop=False)


# ================================================================
# 🚀 ENTRYPOINT
# ================================================================
if __name__ == "__main__":
    main()
