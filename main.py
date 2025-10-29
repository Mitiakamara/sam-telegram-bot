# ================================================================
# 🤖 SAM – Storytelling AI Dungeon Master
# ================================================================
# Punto de entrada principal del bot de Telegram.
# Integra el Orchestrator, maneja los comandos del usuario
# y garantiza que todas las respuestas sean generadas dinámicamente
# por el sistema narrativo (no hardcodeadas).
# ================================================================

import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Core system
from core.orchestrator import Orchestrator

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Inicializamos el sistema narrativo de SAM
sam = Orchestrator()


# ================================================================
# 🧩 COMANDOS PRINCIPALES
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia la sesión narrativa. Solo mensaje introductorio.
    El resto será generado dinámicamente al primer input del jugador.
    """
    await update.message.reply_text(
        "🎲 ¡Bienvenido aventurero! Soy **SAM**, tu narrador en esta campaña.\n"
        "Describe tus acciones o habla con los NPCs. Cuando quieras reiniciar, usa /reset."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Reinicia el mundo narrativo a través del Orchestrator.
    """
    sam.reset_world()
    await update.message.reply_text("🌍 El mundo ha sido reiniciado. La historia comienza de nuevo...")


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Permite unirse a la sesión o campaña activa.
    """
    msg = sam.handle_command("/join")
    await update.message.reply_text(msg)


async def create_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia la creación de personaje, pero la descripción debe ser narrada por SAM.
    """
    # Genera una introducción al proceso, no un texto estático
    prompt = "El jugador quiere crear su personaje. Guíalo con una breve introducción al proceso de creación."
    ai_response = sam.process_scene(prompt)
    await update.message.reply_text(ai_response.text)


# ================================================================
# 💬 MENSAJES DEL JUGADOR
# ================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Procesa toda entrada de texto del jugador (acciones, decisiones, diálogo, etc.).
    """
    user_input = update.message.text
    logger.info(f"[Jugador] {user_input}")

    try:
        response = sam.process_scene(user_input)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.exception("Error al procesar escena")
        await update.message.reply_text(
            "⚠️ Hubo un error procesando tu acción. SAM medita en silencio..."
        )


# ================================================================
# 🚀 MAIN LOOP
# ================================================================

async def main():
    """
    Configura e inicia el bot de Telegram en modo polling.
    (Evita conflictos de múltiples instancias activas)
    """
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(False)
        .build()
    )

    # --- Comandos básicos ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("createcharacter", create_character))

    # --- Mensajes del jugador ---
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 SAM listo y en ejecución (modo campaña IA-driven).")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    asyncio.run(main())
