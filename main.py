import os
import asyncio
import logging
import nest_asyncio
from fastapi import FastAPI
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import uvicorn

# =============================================================
# 🧩 Importar módulos SAM Core
# =============================================================
from core.orchestrator import Orchestrator
from core.renderer import Renderer

# 🧙‍♂️ Módulo de creación de personajes
from core.character_builder import start_character_creation, handle_response, handle_callback
from core.character_builder.loader import load_party

# =============================================================
# ⚙️ CONFIGURACIÓN GLOBAL
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
# 🎭 INICIALIZACIÓN SAM CORE
# =============================================================
orchestrator = Orchestrator()
renderer = Renderer()

# =============================================================
# 🌐 FASTAPI HEALTHCHECK
# =============================================================
app_health = FastAPI()

@app_health.get("/")
async def root():
    return {
        "status": "ok",
        "bot": "SAM",
        "mode": "Render",
        "remote_gameapi": GAME_API_URL,
    }

# =============================================================
# 🤖 HANDLERS DE COMANDOS
# =============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Bienvenido a *SAM*, tu Dungeon Master AI!\n\n"
        "Usa /join para unirte a la campaña o /help para ver opciones.",
        parse_mode="Markdown",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 *Comandos disponibles:*\n"
        "/start – Inicia la aventura.\n"
        "/join – Únete a la partida.\n"
        "/createcharacter – Crea tu personaje.\n"
        "/status – Estado del mundo actual.\n"
        "/reset – Reinicia la campaña (admin).",
        parse_mode="Markdown",
    )

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name

    # 1️⃣ Cargar personajes creados desde data/party/
    party = load_party()
    if not party:
        await update.message.reply_text(
            "⚠️ No hay personajes creados todavía.\nUsa /createcharacter antes de unirte a la aventura.",
            parse_mode="Markdown",
        )
        return

    # 2️⃣ Mostrar resumen rápido de la party
    names = ", ".join([p.get("name", "??") for p in party])
    await update.message.reply_text(
        f"🎲 Formando grupo con: *{names}*\nEl viaje está por comenzar...",
        parse_mode="Markdown",
    )

    # 3️⃣ Iniciar la aventura grupal
    try:
        scene = orchestrator.start_new_adventure(user)
        rendered = renderer.render_scene(scene)
        await update.message.reply_text(rendered, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[SAM Error] Fallo al iniciar aventura: {e}")
        await update.message.reply_text(
            "💥 Ocurrió un error al iniciar la aventura. SAM se está recuperando...",
            parse_mode="Markdown",
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = orchestrator.get_world_status()
    await update.message.reply_text(status, parse_mode="Markdown")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username or update.effective_user.first_name
    orchestrator.reset_world()
    await update.message.reply_text(
        f"🌀 El mundo narrativo ha sido reiniciado por *{user}*.",
        parse_mode="Markdown",
    )

# =============================================================
# 💬 HANDLER DE MENSAJES LIBRES (jugadores)
# =============================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user_name = update.effective_user.first_name

    try:
        # SAM procesa el mensaje (acción del jugador)
        scene_result = orchestrator.process_player_input(user_name, user_input)
        rendered = renderer.render_scene(scene_result)
        await update.message.reply_text(rendered, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"[SAM Error] {e}")
        await update.message.reply_text(
            "💥 Algo salió mal procesando tu acción. SAM se está recuperando...",
            parse_mode="Markdown",
        )

# =============================================================
# 🚀 BUCLE PRINCIPAL
# =============================================================
async def main():
    logger.info("🚀 Iniciando SAM en modo Render remoto...")
    nest_asyncio.apply()

    # --- Inicializar bot Telegram ---
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # --- Registrar comandos principales ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("join", join_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("reset", reset_command))

    # --- Registrar creación de personajes ---
    app.add_handler(CommandHandler("createcharacter", start_character_creation))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    # --- Capturar mensajes normales (narrativa) ---
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # --- Servidor de salud interno (FastAPI) ---
    async def run_health_server():
        config = uvicorn.Config(app_health, host="0.0.0.0", port=PORT, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    # --- Ejecutar ambos procesos ---
    logger.info("🤖 SAM listo y en ejecución (modo campaña).")
    await asyncio.gather(
        app.run_polling(close_loop=False),
        run_health_server()
    )

# =============================================================
# 🏁 ENTRY POINT
# =============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logger.error(f"💥 Error crítico: {e}")
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
