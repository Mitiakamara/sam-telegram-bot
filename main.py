import os
import asyncio
import logging
import nest_asyncio
from fastapi import FastAPI
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from dotenv import load_dotenv
import uvicorn

# =============================================================
# ⚙️ CONFIGURACIÓN INICIAL
# =============================================================
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
SRD_SERVICE_URL = os.getenv("SRD_SERVICE_URL", "https://sam-srdservice.onrender.com")
PORT = int(os.getenv("PORT", 10000))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# =============================================================
# 🤖 BOT HANDLERS BÁSICOS
# =============================================================

async def start(update, context):
    await update.message.reply_text(
        "👋 ¡Bienvenido a *SAM*, tu Dungeon Master AI!\n\n"
        "Usa /join para unirte a la campaña o /help para ver opciones.",
        parse_mode="Markdown",
    )

async def help_command(update, context):
    await update.message.reply_text(
        "📜 *Comandos disponibles:*\n"
        "/start – Inicia la aventura.\n"
        "/join – Únete a la partida.\n"
        "/status – Estado del mundo actual.\n"
        "/reset – Reinicia la campaña (admin).\n",
        parse_mode="Markdown",
    )

# =============================================================
# 🌐 FASTAPI HEALTHCHECK
# =============================================================
app_health = FastAPI()

@app_health.get("/")
async def root():
    return {"status": "ok", "bot": "SAM", "mode": "Render", "remote_gameapi": GAME_API_URL}

# =============================================================
# ⚙️ FUNCIÓN PRINCIPAL
# =============================================================
async def main():
    logger.info("🚀 Iniciando SAM en modo Render remoto...")

    # Permite que loops se mezclen (corrige RuntimeError)
    nest_asyncio.apply()

    # --- Inicializa el bot ---
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    logger.info("🤖 SAM listo y en ejecución (modo campaña).")

    # --- Lanza el healthcheck FastAPI ---
    async def run_health_server():
        config = uvicorn.Config(app_health, host="0.0.0.0", port=PORT, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    # --- Ejecuta ambos en paralelo ---
    await asyncio.gather(
        app.run_polling(close_loop=False),
        run_health_server()
    )

# =============================================================
# 🚀 ENTRY POINT
# =============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logger.error(f"💥 Error crítico: {e}")
        # En caso de que el loop ya esté corriendo (Render hot reload)
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
