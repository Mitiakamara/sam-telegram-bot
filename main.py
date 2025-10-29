# =============================================================
# S.A.M. - Storytelling AI Dungeon Master
# =============================================================
# Main entrypoint para despliegue en Render
# Conexión remota con GameAPI y SRDService
# Controla la narrativa, jugadores y escenas
# =============================================================

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from core.orchestrator import Orchestrator

# =============================================================
# ⚙️ CONFIGURACIÓN INICIAL
# =============================================================
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
SRD_SERVICE_URL = os.getenv("SRD_SERVICE_URL", "https://sam-srdservice.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =============================================================
# 🧠 INICIALIZACIÓN DE SAM (Orchestrator remoto)
# =============================================================
sam = Orchestrator(
    gameapi_url=GAME_API_URL,
    srdservice_url=SRD_SERVICE_URL,
)

# =============================================================
# 🧩 HANDLERS DE COMANDOS
# =============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Saludos, aventurero! Soy *S.A.M.*, tu narrador de campaña.\n"
        "Usa /join para unirte o /loadcampaign para comenzar una aventura.",
        parse_mode="Markdown"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🧙‍♂️ {user.first_name} se ha unido al grupo de aventureros."
    )

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Debes indicar a quién expulsar. Ejemplo: /kick @usuario")
        return
    target = " ".join(context.args)
    await update.message.reply_text(f"⚔️ {target} ha sido expulsado del grupo (por motivos narrativos).")

async def create_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 Creemos tu personaje...\n"
        "Por favor escribe su nombre, raza y clase (ej: 'Asterix, humano guerrero')."
    )

async def load_campaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Cargando campaña desde GameAPI remoto..."
    )
    await sam.reset_world()
    scene = await sam.generate_scene_description()
    await update.message.reply_text(f"🌍 {scene}")

async def describe_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scene = await sam.generate_scene_description()
    await update.message.reply_text(f"🎬 {scene}")

async def player_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    logger.info(f"[Action] Recibida acción: {text}")
    result = await sam.process_player_action(text)
    scene = result.get("scene", "El silencio domina la escena...")
    emotion = result.get("emotion", {}).get("mood", "neutral")
    await update.message.reply_text(f"🎭 *Narrador*: {scene}\n\n_Emoción actual: {emotion}_", parse_mode="Markdown")

async def query_srd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🔍 Usa /srd [término] para consultar las reglas (ejemplo: /srd fireball)")
        return
    term = " ".join(context.args)
    data = await sam.query_srd(term)
    if not data or "error" in data:
        await update.message.reply_text(f"⚠️ No se encontró información sobre '{term}'.")
        return

    formatted = "\n".join([f"*{k.capitalize()}*: {v}" for k, v in data.items()])
    await update.message.reply_text(f"📚 Resultado de SRD:\n{formatted}", parse_mode="Markdown")

async def reset_world(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("♻️ Reiniciando mundo narrativo remoto...")
    await sam.reset_world()
    await update.message.reply_text("✅ Mundo reiniciado correctamente.")

async def get_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = await sam.get_state()
    await update.message.reply_text(f"🧭 Estado actual:\n`{state}`", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Comandos disponibles:*\n"
        "/join - Unirse a la aventura\n"
        "/kick [usuario] - Expulsar jugador\n"
        "/createcharacter - Crear personaje\n"
        "/loadcampaign - Cargar nueva campaña\n"
        "/describe - Describir la escena\n"
        "/srd [término] - Consultar reglas D&D SRD\n"
        "/reset - Reiniciar mundo narrativo\n"
        "/state - Ver estado actual\n"
        "/help - Mostrar esta lista\n",
        parse_mode="Markdown"
    )

# =============================================================
# 🩺 HEALTHCHECK ENDPOINT (modo Render)
# =============================================================
from fastapi import FastAPI
import uvicorn

health_app = FastAPI(title="SAM Health Monitor")

@health_app.get("/health")
async def healthcheck():
    return {
        "status": "ok",
        "service": "sam-telegram-bot",
        "connected_to": {
            "GameAPI": GAME_API_URL,
            "SRDService": SRD_SERVICE_URL
        }
    }

# =============================================================
# 🚀 FUNCIÓN PRINCIPAL
# =============================================================

async def main():
    logger.info("🚀 Iniciando SAM en modo Render remoto...")

    # Crear aplicación Telegram
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Registrar comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("createcharacter", create_character))
    app.add_handler(CommandHandler("loadcampaign", load_campaign))
    app.add_handler(CommandHandler("describe", describe_scene))
    app.add_handler(CommandHandler("srd", query_srd))
    app.add_handler(CommandHandler("reset", reset_world))
    app.add_handler(CommandHandler("state", get_state))
    app.add_handler(CommandHandler("help", help_command))

    # Captura cualquier texto como acción del jugador
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, player_action))

    # Ejecutar bot y health server en paralelo
    async def run_health_server():
        uvicorn_config = uvicorn.Config(
            health_app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", 10000)),
            log_level="info",
        )
        server = uvicorn.Server(uvicorn_config)
        await server.serve()

    async def run_bot():
        logger.info("🤖 SAM listo y en ejecución (modo campaña).")
        await app.run_polling(close_loop=False)

    # Ejecutar concurrentemente
    await asyncio.gather(run_bot(), run_health_server())

# =============================================================
# 🧩 PUNTO DE ENTRADA
# =============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("⚠️ SAM detenido manualmente.")
    except Exception as e:
        logger.exception(f"💥 Error crítico: {e}")
