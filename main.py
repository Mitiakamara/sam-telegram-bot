import asyncio
import logging
import os
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from bot_service import send_action, get_state, start_game, BOT_TOKEN
import aiohttp

# ================================================================
# ⚙️ CONFIGURACIÓN GLOBAL
# ================================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

ADMIN_ID = os.getenv("ADMIN_TELEGRAM_ID")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
SRD_URL = os.getenv("SRD_SERVICE_URL", "https://sam-srdservice.onrender.com")
CHECK_INTERVAL = 300  # 5 minutos
RETRY_DELAY = 30      # segundos entre reintentos


# ================================================================
# 🤖 COMANDOS PRINCIPALES
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Bienvenido a *S.A.M.*, tu Dungeon Master virtual.\n"
        "Usa /join para unirte a la aventura o escribe directamente tus acciones.\n\n"
        "Por ejemplo:\n"
        "👉 combat medium\n"
        "👉 explore dungeon\n"
        "👉 rest junto a la fogata",
        parse_mode="Markdown",
    )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"🧙‍♂️ {user}, te has unido a la partida. ¡Que comience la aventura!"
    )


async def state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state_data = await get_state()
    await update.message.reply_text(f"📜 Estado actual:\n{state_data}")


# ================================================================
# ⚔️ MANEJO DE ACCIONES
# ================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = update.effective_user.first_name
    action = update.message.text.strip()
    logging.info(f"[{player}] Acción recibida: {action}")

    result = await send_action(player, action)

    # Si no hay partida activa, iniciar automáticamente
    if "error" in result and "No hay partida" in result["error"]:
        await update.message.reply_text("🧙‍♂️ No hay partida activa. Iniciando una nueva...")
        start_result = await start_game()
        if "error" in start_result:
            await update.message.reply_text(f"⚠️ Error al iniciar partida: {start_result['error']}")
            return
        else:
            await update.message.reply_text("✅ Nueva partida iniciada. ¡Adelante, aventurero!")
            result = await send_action(player, action)

    # Error de conexión con GameAPI
    if "error" in result:
        await update.message.reply_text(f"⚠️ {result['error']}")
        return

    # Mostrar resultado legible
    msg = result.get("encounter") or result.get("echo") or result
    if isinstance(msg, dict):
        formatted = "\n".join([f"*{k}:* {v}" for k, v in msg.items()])
        await update.message.reply_text(f"🎲 Resultado:\n{formatted}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"🎲 Resultado:\n{msg}")


# ================================================================
# 🔄 SISTEMA KEEP-ALIVE (monitoreo y reintento)
# ================================================================

async def ping_service(session, name, url):
    """Verifica la salud del servicio /health"""
    try:
        async with session.get(f"{url}/health", timeout=15) as resp:
            if resp.status == 200:
                logging.info(f"✅ {name} está activo ({url})")
                return True
            else:
                logging.warning(f"⚠️ {name} respondió con {resp.status}")
                return False
    except Exception as e:
        logging.error(f"❌ {name} no respondió: {e}")
        return False


async def check_and_retry(bot: Bot, session, name, url):
    """Hace ping, reintenta si falla, y notifica solo si ambos intentos fallan."""
    ok = await ping_service(session, name, url)
    if not ok:
        logging.warning(f"⚠️ {name} parece caído. Reintentando en {RETRY_DELAY}s...")
        await asyncio.sleep(RETRY_DELAY)
        ok = await ping_service(session, name, url)

        if not ok:  # segundo fallo
            msg = f"🚨 *Alerta de conexión S.A.M.*\n❌ {name} no responde tras 2 intentos.\n{url}"
            if ADMIN_ID:
                try:
                    await bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")
                except Exception as e:
                    logging.error(f"Error enviando alerta a Telegram: {e}")
    return ok


async def keep_alive(bot: Bot):
    """Monitorea GameAPI y SRDService cada X minutos."""
    logging.info("🔄 Iniciando verificación periódica de servicios...")
    while True:
        async with aiohttp.ClientSession() as session:
            await check_and_retry(bot, session, "GameAPI", GAME_API_URL)
            await check_and_retry(bot, session, "SRDService", SRD_URL)
        await asyncio.sleep(CHECK_INTERVAL)


# ================================================================
# 🚀 INICIALIZACIÓN DEL BOT
# ================================================================

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("state", state))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("🤖 S.A.M. Bot iniciado y escuchando mensajes...")
    await app.run_polling()


if __name__ == "__main__":
    bot = Bot(token=BOT_TOKEN)
    loop = asyncio.get_event_loop()
    loop.create_task(keep_alive(bot))  # mantiene vivos GameAPI y SRDService
    loop.run_until_complete(main())
