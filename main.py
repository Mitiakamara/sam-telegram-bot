# ================================================================
# 🤖 SAM - Storytelling Adventure Machine
# ================================================================
# Sistema central del bot de Telegram y servidor narrativo.
# Fase 7.0 – Dynamic World Events & Consequences
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
# 🔧 CONFIGURACIÓN INICIAL
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
    """Inicia sesión del jugador."""
    logger.info("[Jugador] /start")
    await update.message.reply_text(
        "🎲 ¡Bienvenido aventurero! Soy *SAM*, tu narrador dinámico.\n"
        "Usa /begin para iniciar la aventura o /help para ver comandos.",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra comandos disponibles."""
    await update.message.reply_text(
        "📜 *Comandos disponibles:*\n"
        "/begin – Iniciar nueva aventura\n"
        "/reset – Reiniciar mundo narrativo\n"
        "/state – Mostrar estado actual\n"
        "/join – Unirse al grupo\n"
        "/kick – Expulsar jugador\n"
        "/deletesession – Borrar sesión activa\n"
        "/help – Mostrar ayuda",
        parse_mode="Markdown",
    )


async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia nueva aventura."""
    logger.info("[Jugador] /begin")
    sam.reset_world()
    state = sam.get_state()
    scene = state.get("scene", {})
    await update.message.reply_text(
        f"✨ *Nueva aventura iniciada*\n\n🏞️ {scene.get('title','Escena inicial')}\n{scene.get('description','...')}",
        parse_mode="Markdown",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reinicia el mundo narrativo."""
    logger.info("[Jugador] /reset")
    sam.reset_world()
    await update.message.reply_text("♻️ Mundo reiniciado. ¡Un nuevo destino te espera!", parse_mode="Markdown")


async def show_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra estado actual."""
    state = sam.get_state()
    scene = state.get("scene", {})
    emotion = state.get("emotion", {})
    await update.message.reply_text(
        f"📖 *Estado Actual*\n\n"
        f"🏞️ Escena: {scene.get('title','-')}\n"
        f"🎭 Tono: {emotion.get('tone','neutral')}\n"
        f"💫 Intensidad: {emotion.get('intensity',0)}\n"
        f"🕰️ Última actualización: {state.get('timestamp','N/A')}",
        parse_mode="Markdown",
    )


# ================================================================
# 👥 COMANDOS DE ADMINISTRACIÓN DE JUGADORES
# ================================================================
async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simula unión de jugador."""
    player = update.effective_user.first_name
    logger.info(f"[Jugador] {player} se une a la partida.")
    await update.message.reply_text(f"👋 ¡{player} se ha unido al grupo de aventureros!", parse_mode="Markdown")


async def kick_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Expulsa jugador ficticio."""
    args = context.args
    if not args:
        await update.message.reply_text("Debes especificar a quién expulsar. Ej: /kick Valen")
        return
    target = args[0]
    logger.info(f"[Admin] Expulsó a {target}")
    await update.message.reply_text(f"🪓 {target} ha sido expulsado del grupo.")


async def delete_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elimina sesión completa."""
    logger.warning("[Admin] Eliminando sesión activa...")
    try:
        from core.persistence.state_persistence import StatePersistence
        StatePersistence().delete_state()
        await update.message.reply_text("🔥 Sesión eliminada exitosamente.")
    except Exception as e:
        logger.error(f"[Error] {e}")
        await update.message.reply_text("⚠️ No se pudo eliminar la sesión.")


# ================================================================
# 💬 INTERACCIÓN NATURAL
# ================================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa entradas del jugador."""
    user_input = update.message.text.strip()
    logger.info(f"[Jugador] {user_input}")

    try:
        result = sam.process_player_action(user_input)
        scene = result.get("scene", {})
        emotion = result.get("emotion", {})
        outcome = result.get("outcome", "neutral")

        text = (
            f"🎬 *{scene.get('title','Nueva escena')}*\n"
            f"{scene.get('description','...')}\n\n"
            f"🎭 Emoción: {emotion.get('tone','neutral')} ({emotion.get('intensity',0)})\n"
            f"⚖️ Resultado: {outcome}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[Error] Procesando acción: {e}")
        await update.message.reply_text("⚠️ Error interno del narrador.")


# ================================================================
# 🧩 FASTAPI ENDPOINT (modo servidor opcional)
# ================================================================
from fastapi import FastAPI
api = FastAPI(title="SAM API")

@api.get("/health")
def health():
    return {"status": "ok", "system": "SAM Engine"}

@api.get("/state")
def state():
    return sam.get_state()


# ================================================================
# 🚀 FUNCIÓN PRINCIPAL
# ================================================================
async def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # Comandos principales
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("begin", begin))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("state", show_state))

    # Administración
    app.add_handler(CommandHandler("join", join_game))
    app.add_handler(CommandHandler("kick", kick_player))
    app.add_handler(CommandHandler("deletesession", delete_session))

    # Mensajes libres
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 SAM listo y en ejecución (modo campaña).")
    await app.run_polling(close_loop=False)


# ================================================================
# 🧠 EJECUCIÓN SEGURA PARA RENDER / PYTHON 3.13 (FINAL)
# ================================================================
if __name__ == "__main__":
    import nest_asyncio
    import uvloop

    # Habilita compatibilidad de loops anidados y acelera asyncio
    nest_asyncio.apply()
    uvloop.install()

    logger.info("🚀 Iniciando SAM en modo asíncrono seguro (Render + PTB 21.6)...")

    async def safe_launcher():
        try:
            await main()
        except Exception as e:
            logger.error(f"[Launcher] Error en ejecución principal: {e}")

    try:
        # Ejecuta el bot con un nuevo loop limpio
        asyncio.run(safe_launcher())
    except RuntimeError as e:
        # Fallback si el loop ya está activo (Render warmup)
        logger.warning(f"[Loop Warning] {e} — utilizando fallback asyncio.create_task()")
        loop = asyncio.get_event_loop()
        loop.create_task(safe_launcher())
        loop.run_forever()
