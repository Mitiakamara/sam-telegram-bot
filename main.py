# ================================================================
# 🤖 SAM - Storytelling Adventure Machine
# ================================================================
# Archivo principal del bot de Telegram.
# Inicia SAM, maneja comandos y enruta mensajes al Orchestrator.
#
# Compatible con:
#   - Fase 7.0: Dynamic World Events & Consequences
#   - Python 3.13 / Render
#   - Telegram Bot API v21.6
# ================================================================

import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ------------------------------------------------------------
# 🔧 Configuración inicial
# ------------------------------------------------------------
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

from core.orchestrator import Orchestrator

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Instancia global de SAM
sam = Orchestrator()


# ================================================================
# 🧭 COMANDOS PRINCIPALES
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start — Inicia la sesión de campaña."""
    logger.info("[Jugador] Ha iniciado la campaña con /start")
    await update.message.reply_text(
        "🎲 ¡Bienvenido aventurero! Soy *SAM*, tu narrador de historias dinámicas.\n"
        "Usa /begin para comenzar una nueva aventura o /help para ver las opciones.",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help — Muestra ayuda básica."""
    await update.message.reply_text(
        "📜 *Comandos disponibles:*\n"
        "/begin – Iniciar una nueva aventura\n"
        "/reset – Reiniciar el mundo narrativo\n"
        "/state – Ver el estado actual del mundo\n"
        "/help – Mostrar esta ayuda",
        parse_mode="Markdown",
    )


async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /begin — Inicia la primera escena."""
    logger.info("[Jugador] Ha comenzado una nueva aventura con /begin")
    sam.reset_world()
    state = sam.get_state()

    scene_title = state.get("scene", {}).get("title", "Escena desconocida")
    description = state.get("scene", {}).get("description", "Sin descripción disponible.")

    await update.message.reply_text(
        f"✨ *Nueva aventura iniciada*\n\n🏞️ {scene_title}\n{description}",
        parse_mode="Markdown",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /reset — Reinicia la sesión de campaña."""
    logger.info("[Jugador] Solicitó reinicio del mundo narrativo.")
    sam.reset_world()
    await update.message.reply_text(
        "♻️ El mundo narrativo ha sido reiniciado. ¡Prepárate para un nuevo comienzo!",
        parse_mode="Markdown",
    )


async def show_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /state — Muestra el estado actual del mundo."""
    state = sam.get_state()
    scene = state.get("scene", {})
    emotion = state.get("emotion", {})

    text = (
        f"📖 *Estado Actual del Mundo*\n\n"
        f"🏞️ Escena: {scene.get('title', 'Desconocida')}\n"
        f"🎭 Tono: {emotion.get('tone', 'neutral')}\n"
        f"💫 Intensidad emocional: {emotion.get('intensity', '0')}\n"
        f"🕰️ Última actualización: {state.get('timestamp', 'N/A')}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ================================================================
# 💬 GESTOR DE MENSAJES LIBRES
# ================================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa entradas naturales del jugador."""
    user_input = update.message.text.strip()
    logger.info(f"[Jugador] {user_input}")

    try:
        result = sam.process_player_action(user_input)
        scene = result.get("scene", {})
        emotion = result.get("emotion", {})
        outcome = result.get("outcome", "neutral")

        response = (
            f"🎬 *{scene.get('title', 'Nueva escena')}*\n"
            f"{scene.get('description', '')}\n\n"
            f"🎭 Emoción actual: {emotion.get('tone', 'neutral')} ({emotion.get('intensity', 0)})\n"
            f"⚖️ Resultado narrativo: {outcome}"
        )

        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"[Error] Al procesar mensaje del jugador: {e}")
        await update.message.reply_text(
            "⚠️ Ocurrió un error procesando la acción. SAM lo anotará en sus pergaminos.",
            parse_mode="Markdown",
        )


# ================================================================
# 🚀 FUNCIÓN PRINCIPAL
# ================================================================
async def main():
    """Punto de entrada principal del bot."""
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # Comandos básicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("begin", begin))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("state", show_state))

    # Mensajes naturales
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 SAM listo y en ejecución (modo campaña).")
    await app.run_polling()


# ================================================================
# 🧠 EJECUCIÓN SEGURA PARA RENDER / PYTHON 3.13
# ================================================================
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            logger.warning("⚙️ Loop ya activo, ejecutando SAM en modo no bloqueante.")
            loop.create_task(main())
            loop.run_forever()
        else:
            loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 SAM detenido manualmente.")
    except RuntimeError as e:
        if "already running" in str(e):
            logger.warning("⚠️ SAM ya está corriendo en un loop activo, usando alternativa segura.")
            asyncio.get_event_loop().create_task(main())
        else:
            raise
