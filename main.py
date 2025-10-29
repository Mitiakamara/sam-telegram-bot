# ==========================================================
# 🤖 SAM Main – Campaña Pre-Creada (versión estable)
# ==========================================================
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Core orchestrator
from core.orchestrator import Orchestrator

# ==========================================================
# CONFIGURACIÓN INICIAL
# ==========================================================
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inicializar SAM
sam = Orchestrator()

# ==========================================================
# COMANDOS BÁSICOS
# ==========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start – Inicia la aventura."""
    await update.message.reply_text(
        "🎲 ¡Bienvenido aventurero! Soy **SAM**, tu narrador en esta campaña.\n"
        "Describe tus acciones o habla con los NPCs. Cuando quieras reiniciar, usa /reset."
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /reset – Reinicia el estado narrativo."""
    sam.reset_world()
    await update.message.reply_text("🔄 El mundo ha sido reiniciado. La historia comienza de nuevo...")

# ==========================================================
# MANEJO DE MENSAJES DE JUGADOR
# ==========================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    logger.info(f"[Jugador] {user_input}")
    response = sam.process_scene(user_input)
    await update.message.reply_text(response)

# ==========================================================
# CONFIGURACIÓN DEL BOT
# ==========================================================
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 SAM listo y en ejecución (modo campaña).")
    application.run_polling()

if __name__ == "__main__":
    main()
