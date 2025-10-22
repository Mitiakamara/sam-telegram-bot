import os
import asyncio
import logging
import httpx
import json # Necesario para procesar JSON, aunque ahora lo formateamos diferente
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

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
SRD_SERVICE_URL = os.getenv("SRD_SERVICE_URL", "https://sam-srdservice.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================================================================
# 🧠 FUNCIONES PRINCIPALES DEL BOT
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Bienvenido a *S.A.M.*, tu Dungeon Master virtual.\n"
        "Usa /join para unirte a la aventura o escribe directamente tus acciones.\n\n"
        "Por ejemplo:\n"
        "👉 combat medium\n"
        "👉 explore dungeon\n"
        "👉 rest junto a la fogata",
        parse_mode="Markdown"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"🧙‍♂️ {user}, te has unido a la partida. ¡Que comience la aventura!"
    )

async def state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Estado de la partida: pronto disponible.")

# ================================================================
# 🎲 MANEJO DE ACCIONES
# ================================================================

async def send_action(player: str, action: str) -> dict:
    """Envía la acción del jugador al GameAPI."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"player": player, "action": action}
            r = await client.post(f"{GAME_API_URL}/game/action", json=payload)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": f"No se pudo conectar al GameAPI: {e}"}


async def start_game():
    """Inicia una nueva partida en el GameAPI."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"party_levels": [3, 3, 4]}  # grupo base de ejemplo
            r = await client.post(f"{GAME_API_URL}/game/start", json=payload)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": f"Error iniciando partida: {e}"}


async def format_encounter_message(encounter_data: dict) -> str:
    """Formatea la respuesta de encuentro JSON en un mensaje legible."""
    
    difficulty = encounter_data.get("difficulty", "desconocida")
    xp_total = encounter_data.get("xp_total", 0)
    monsters = encounter_data.get("monsters", [])
    
    # Contar la ocurrencia de cada tipo de monstruo
    monster_counts = {}
    for monster in monsters:
        name = monster.get("name", "Criatura Desconocida")
        monster_counts[name] = monster_counts.get(name, 0) + 1

    # Construir la lista de enemigos
    enemy_list = []
    for name, count in monster_counts.items():
        # Busca el primer objeto del monstruo para obtener sus stats
        stats = next((m for m in monsters if m.get("name") == name), {})
        
        cr = stats.get("cr", "N/A")
        hp = stats.get("hp", "N/A")
        ac = stats.get("ac", "N/A")
        attack = stats.get("attack", "N/A")
        
        line = f"*{count}x {name}* (CR {cr}): HP {hp}, AC {ac}, Ataque {attack}"
        enemy_list.append(line)

    # Construir el mensaje final
    header = f"⚔️ *¡Encuentro de Combate!* (Dificultad: {difficulty.upper()})"
    xp_info = f"🪙 Experiencia total: {xp_total} XP"
    
    enemies_section = "👹 *Enemigos:*\n" + "\n".join(enemy_list)
    
    return f"{header}\n\n{xp_info}\n\n{enemies_section}"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = update.effective_user.first_name
    action = update.message.text.strip()
    logging.info(f"[{player}] Acción recibida: {action}")

    result = await send_action(player, action)

    # 1. Manejo de inicio de partida si no hay sesión activa
    if "error" in result and "No hay partida" in result["error"]:
        await update.message.reply_text("🧙 No hay partida activa. Iniciando una nueva...")
        start_result = await start_game()
        
        if "error" in start_result:
            await update.message.reply_text(f"⚠️ Error al iniciar partida: {start_result['error']}")
            return
        else:
            await update.message.reply_text("✅ Nueva partida iniciada. ¡Comienza la aventura!")
            # Vuelve a intentar la acción original
            result = await send_action(player, action)

    # 2. Manejo de errores generales de la API
    if "error" in result:
        await update.message.reply_text(f"⚠️ {result['error']}")
        return

    # 3. Presentación de resultados con formato
    
    # Detecta si es un encuentro y usa el formato legible
    if "encounter" in result:
        message = await format_encounter_message(result["encounter"])
        await update.message.reply_text(
            message, 
            parse_mode="Markdown"
        )
    
    # Detecta si es un mensaje de 'echo' (narración simple)
    elif "echo" in result:
        await update.message.reply_text(
            f"💬 *Narrador:*\n_{result['echo']}_", 
            parse_mode="Markdown"
        )
    
    # Si no es 'encounter' ni 'echo', muestra el resultado JSON completo para depuración
    else:
        formatted = json.dumps(result, indent=2, ensure_ascii=False)
        await update.message.reply_text(
            f"📜 *Resultado sin formato:*\n```json\n{formatted}\n```", 
            parse_mode="Markdown"
        )

# ================================================================
# 🔄 SISTEMA KEEP-ALIVE
# ================================================================

async def check_service_health(name: str, url: str):
    """Verifica que los microservicios SRD y GameAPI sigan activos."""
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
    """Realiza un ping cada 5 minutos a SRD y GameAPI para evitar el sleep."""
    logging.info("🔄 Iniciando verificación periódica de servicios...")
    while True:
        await check_service_health("GameAPI", f"{GAME_API_URL}/health")
        await check_service_health("SRDService", f"{SRD_SERVICE_URL}/health")
        await asyncio.sleep(300)  # 5 minutos

# ================================================================
# 🚀 EJECUCIÓN PRINCIPAL (Render-Safe)
# ================================================================

async def post_init_tasks(app: Application):
    """Callback ejecutado por PTB después de la inicialización, antes del polling.
    Usado para iniciar tareas en segundo plano como el keep-alive."""
    bot = app.bot 
    
    # Ejecuta keep_alive en segundo plano como una tarea asíncrona
    asyncio.create_task(keep_alive(bot))
    logging.info("🤖 S.A.M. Bot iniciado y escuchando mensajes...")

def main():
    """Inicializa el bot de Telegram y el keep-alive loop usando post_init."""
    if not BOT_TOKEN:
        logging.error("❌ TELEGRAM_BOT_TOKEN no está configurado. Abortando.")
        return
        
    # Construir la aplicación e inyectar la tarea de keep-alive en post_init
    app = Application.builder().token(BOT_TOKEN).post_init(post_init_tasks).build()

    # Añadir Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("state", state))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Inicia el polling. Esta función es de bloqueo y maneja el loop de asyncio.
    logging.info("🚀 Iniciando Polling. Esto bloqueará la ejecución.")
    app.run_polling() 


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("🛑 S.A.M. detenido manualmente.")
