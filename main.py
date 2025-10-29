# ============================================================
# SAM - Storytelling Adventure Machine
# Render Deployment (Standalone - Remote APIs)
# ============================================================

import os
import sys
import asyncio
import logging
from contextlib import suppress
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ------------------------------------------------------------
# 🔧 CONFIG
# ------------------------------------------------------------
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
SRD_SERVICE_URL = os.getenv("SRD_SERVICE_URL", "https://sam-srdservice.onrender.com")
PORT = int(os.getenv("PORT", "10000"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("SAM")

# ------------------------------------------------------------
# 🧠 SAM CORE
# ------------------------------------------------------------
from core.orchestrator import Orchestrator

sam = Orchestrator(gameapi_url=GAME_API_URL, srdservice_url=SRD_SERVICE_URL)
sam.reset_world()

# ------------------------------------------------------------
# 🤖 TELEGRAM HANDLERS
# ------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎲 ¡Bienvenido a *SAM*!\n"
        "Tu narrador está listo. Usa /begin para iniciar una nueva aventura.",
        parse_mode="Markdown",
    )

async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sam.reset_world()
    scene = sam.get_state().get("scene", {})
    await update.message.reply_text(
        f"✨ *Aventura iniciada*\n\n🏞️ {scene.get('title','Inicio')}\n{scene.get('description','...')}",
        parse_mode="Markdown",
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 *Comandos disponibles:*\n"
        "/begin – Nueva aventura\n"
        "/reset – Reiniciar mundo\n"
        "/state – Mostrar estado actual\n"
        "/help – Mostrar esta ayuda",
        parse_mode="Markdown",
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sam.reset_world()
    await update.message.reply_text("♻️ Mundo reiniciado. ¡Nuevo comienzo!", parse_mode="Markdown")

async def show_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = sam.get_state()
    scene = state.get("scene", {})
    emotion = state.get("emotion", {})
    await update.message.reply_text(
        f"🏞️ Escena: {scene.get('title','-')}\n"
        f"🎭 Tono: {emotion.get('tone','neutral')}\n"
        f"💫 Intensidad: {emotion.get('intensity',0)}",
        parse_mode="Markdown",
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    try:
        response = sam.process_player_action(user_input)
        scene = response.get("scene", {})
        emotion = response.get("emotion", {})
        await update.message.reply_text(
            f"🎬 *{scene.get('title','Escena')}*\n{scene.get('description','...')}\n\n"
            f"🎭 {emotion.get('tone','neutral')} ({emotion.get('intensity',0)})",
            parse_mode="Markdown",
        )
    except Exception as e:
        log.error(f"[Error Narrativo] {e}")
        await update.message.reply_text("⚠️ El narrador tuvo un error interno.")

# ------------------------------------------------------------
# 🧩 BUILD TELEGRAM APP
# ------------------------------------------------------------
def build_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("begin", begin))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("state", show_state))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app

# ------------------------------------------------------------
# 🌐 FASTAPI: Health endpoint para Render
# ------------------------------------------------------------
api = FastAPI(title="SAM Health API")

@api.get("/health")
def health():
    return {"status": "ok", "service": "SAM", "gameapi": GAME_API_URL, "srd": SRD_SERVICE_URL}

# ------------------------------------------------------------
# 🚀 MAIN LOOP
# ------------------------------------------------------------
async def main():
    log.info("🤖 Iniciando SAM (modo remoto)")
    bot_app = build_bot()

    async def run_bot():
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True)
        log.info("✅ Bot Telegram activo.")
        await bot_app.wait_until_shutdown()

    async def run_fastapi():
        config = uvicorn.Config(api, host="0.0.0.0", port=PORT, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    # Ejecuta bot y API /health en paralelo
    await asyncio.gather(run_bot(), run_fastapi())

# ------------------------------------------------------------
# ▶️ ENTRY POINT
# ------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 SAM detenido manualmente")
    except Exception as e:
        log.exception(f"💥 Error crítico en SAM: {e}")
        sys.exit(1)
