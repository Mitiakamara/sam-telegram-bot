import os
import asyncio
import logging
import httpx
import json
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================

print("🧠 Booting S.A.M. background worker...", flush=True)
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
SRD_SERVICE_URL = os.getenv("SRD_SERVICE_URL", "https://sam-srdservice.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================================================================
# 🧙‍♂️ COMANDOS PRINCIPALES
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 *Bienvenido a S.A.M.*, tu Dungeon Master virtual.\n\n"
        "Usa `/join` para unirte a la aventura o escribe directamente tus acciones.\n\n"
        "Por ejemplo:\n"
        "➡️ `combat medium`\n"
        "➡️ `explore dungeon`\n"
        "➡️ `rest junto a la fogata`\n\n"
        "Prepárate para adentrarte en un mundo de fantasía...",
        parse_mode="Markdown"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(f"🧙‍♂️ {user}, te has unido a la partida. ¡Que comience la aventura!")

async def state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Estado de la partida: pronto disponible.")

# ================================================================
# ⚔️ GAME API HELPERS
# ================================================================

async def send_action(player: str, action: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"player": player, "action": action}
            r = await client.post(f"{GAME_API_URL}/game/action", json=payload)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": f"No se pudo conectar al GameAPI: {e}"}

async def start_game():
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"party_levels": [3, 3, 4]}
            r = await client.post(f"{GAME_API_URL}/game/start", json=payload)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": f"Error iniciando partida: {e}"}

# ================================================================
# 🎨 FORMATOS DE RESPUESTA
# ================================================================

async def format_encounter_message(encounter_data: dict) -> str:
    difficulty = encounter_data.get("difficulty", "desconocida")
    xp_total = encounter_data.get("xp_total", 0)
    monsters = encounter_data.get("monsters", [])
    monster_counts = {}

    for monster in monsters:
        name = monster.get("name", "Criatura Desconocida")
        monster_counts[name] = monster_counts.get(name, 0) + 1

    enemy_lines = []
    for name, count in monster_counts.items():
        stats = next((m for m in monsters if m.get("name") == name), {})
        cr = stats.get("cr", "N/A")
        hp = stats.get("hp", "N/A")
        ac = stats.get("ac", "N/A")
        attack = stats.get("attack", "N/A")
        enemy_lines.append(f"*{count}x {name}* (CR {cr}) — ❤️ {hp} | 🛡️ {ac} | ⚔️ {attack}")

    header = f"⚔️ *¡Encuentro de Combate!* (Dificultad: {difficulty.upper()})"
    xp_info = f"🪙 Experiencia total: {xp_total} XP"
    enemies = "\n".join(enemy_lines)
    return f"{header}\n\n{xp_info}\n\n👹 *Enemigos:*\n{enemies}"

async def format_narrative_message(data: dict, player: str) -> str:
    scene = data.get("scene", "unknown")
    narrative = data.get("narrative", "No se recibió narrativa.")
    story_state = data.get("story_state", {})

    location = story_state.get("location", "Ubicación desconocida")
    objective = story_state.get("objective", "Sin objetivo actual")
    events_completed = story_state.get("events_completed", 0)

    emoji = {
        "exploration": "🌲",
        "combat": "⚔️",
        "rest": "🔥",
        "dialogue": "💬"
    }.get(scene, "✨")

    return (
        f"{emoji} *{scene.title()} — {location}*\n\n"
        f"_{narrative}_\n\n"
        f"🎯 *Objetivo:* {objective}\n"
        f"📖 Eventos completados: {events_completed}\n\n"
        f"👉 ¿Qué harás ahora, {player}? "
    )

# ================================================================
# 💬 MANEJO DE MENSAJES
# ================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = update.effective_user.first_name
    action = update.message.text.strip()
    logging.info(f"[{player}] Acción recibida: {action}")
    result = await send_action(player, action)

    if "error" in result and "No hay partida" in result["error"]:
        await update.message.reply_text("🧙 No hay partida activa. Iniciando una nueva...")
        start_result = await start_game()
        if "error" in start_result:
            await update.message.reply_text(f"⚠️ Error al iniciar partida: {start_result['error']}")
            return
        else:
            await update.message.reply_text("✅ Nueva partida iniciada. ¡Comienza la aventura!")
            result = await send_action(player, action)

    if "error" in result:
        await update.message.reply_text(f"⚠️ {result['error']}")
        return

    if "encounter" in result:
        msg = await format_encounter_message(result["encounter"])
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif "narrative" in result or "scene" in result:
        msg = await format_narrative_message(result, player)
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif "echo" in result:
        await update.message.reply_text(f"💬 *Narrador:*\n_{result['echo']}_", parse_mode="Markdown")
    else:
        formatted = json.dumps(result, indent=2, ensure_ascii=False)
        await update.message.reply_text(
            f"📜 *Resultado sin formato:*\n```json\n{formatted}\n```",
            parse_mode="Markdown"
        )

# ================================================================
# 🔄 KEEP ALIVE
# ================================================================

async def check_service_health(name: str, url: str):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url)
            if r.status_code == 200:
                logging.info(f"✅ {name} está activo ({url})")
            else:
                logging.warning(f"⚠️ {name} respondió con {r.status_code}")
    except Exception as e:
        logging.error(f"❌ {name} inalcanzable: {e}")

async def keep_alive(bot: Bot):
    logging.info("🔄 Iniciando verificación periódica de servicios...")
    while True:
        await check_service_health("GameAPI", f"{GAME_API_URL}/health")
        await check_service_health("SRDService", f"{SRD_SERVICE_URL}/health")
        await asyncio.sleep(300)

# ================================================================
# 🚀 ARRANQUE (MANEJO MANUAL DEL LOOP)
# ================================================================

async def main_async():
    print("🚀 Lanzando S.A.M. Bot...", flush=True)

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("state", state))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.bot.delete_webhook(drop_pending_updates=True)
    logging.info("🧹 Webhook anterior eliminado. Polling limpio garantizado.")

    asyncio.create_task(keep_alive(app.bot))
    await app.initialize()
    await app.start()
    logging.info("🤖 S.A.M. Bot iniciado correctamente. Escuchando mensajes...")
    await app.run_polling()

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main_async())
    except KeyboardInterrupt:
        logging.info("🛑 S.A.M. detenido manualmente.")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
