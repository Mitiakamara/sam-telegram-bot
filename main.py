import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from bot_service import send_action, get_state, BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================================================================
# 🧙‍♀️ Funciones narrativas y formateo
# ================================================================

def format_encounter(data: dict) -> str:
    """Convierte un encuentro de combate en texto legible."""
    try:
        encounter = data.get("encounter", {})
        difficulty = encounter.get("difficulty", "desconocida").capitalize()
        xp_target = encounter.get("xp_target", 0)
        xp_total = encounter.get("xp_total", 0)
        avg_lvl = encounter.get("party_avg_lvl", "?")

        monsters = encounter.get("monsters", [])
        monster_lines = []
        for m in monsters:
            line = f"- {m.get('name', '¿?')} (HP: {m.get('hp', '?')}, CA: {m.get('ac', '?')}, ATK: {m.get('attack', '?')})"
            traits = m.get("traits")
            if traits:
                line += f" 🧩 Rasgos: {', '.join(traits)}"
            monster_lines.append(line)

        return (
            f"🎲 *Encuentro generado*\n"
            f"Dificultad: *{difficulty}*\n"
            f"XP objetivo: {xp_target}\n"
            f"XP total: {xp_total}\n"
            f"Nivel promedio del grupo: {avg_lvl}\n\n"
            f"👾 *Monstruos:*\n" + "\n".join(monster_lines)
        )
    except Exception as e:
        logging.error(f"Error al formatear encuentro: {e}")
        return str(data)


def format_narrative(data: dict) -> str:
    """Formatea texto narrativo o de exploración."""
    story = data.get("story_state", {})
    scene = story.get("scene", "??").capitalize().replace("_", " ")
    objective = story.get("objective", "")
    narrative = data.get("narrative", data.get("echo", ""))

    msg = f"📜 *Escena:* {scene}\n🎯 *Objetivo:* {objective}\n\n{narrative}"
    return msg


def format_resume(state: dict) -> str:
    """Muestra un resumen de partida al retomar una sesión."""
    scene = state.get("story_state", {}).get("scene", "intro")
    objective = state.get("story_state", {}).get("objective", "")
    events = state.get("story_state", {}).get("events_completed", 0)
    msg = (
        "🕯 *Reanudando tu aventura...*\n\n"
        f"Escena actual: *{scene}*\n"
        f"Objetivo: {objective}\n"
        f"Eventos completados: {events}\n\n"
        "✨ Estás de vuelta en el mundo de S.A.M."
    )
    return msg


# ================================================================
# 🔹 Comandos base del bot
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de bienvenida."""
    await update.message.reply_text(
        "🌟 Bienvenido a *S.A.M.*, tu Dungeon Master virtual.\n"
        "Usa /join para unirte a la aventura o escribe directamente tus acciones.\n\n"
        "Por ejemplo:\n"
        "👉 *combat medium*\n"
        "👉 *explore dungeon*\n"
        "👉 *rest junto a la fogata*",
        parse_mode="Markdown"
    )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Une al jugador a la partida."""
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"🧙‍♂️ {user}, te has unido a la partida. ¡Que comience la aventura!"
    )


async def state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta el estado actual del juego."""
    state_data = await get_state()
    await update.message.reply_text(format_resume(state_data), parse_mode="Markdown")


# ================================================================
# 🔸 Núcleo del sistema de mensajes
# ================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = update.effective_user.first_name
    action = update.message.text.strip()
    logging.info(f"[{player}] Acción recibida: {action}")

    # Enviar acción al GameAPI
    result = await send_action(player, action)

    # Si no hay partida, crear una nueva automáticamente
    if "error" in result and "No hay partida en curso" in result["error"]:
        await update.message.reply_text("🕹 No hay partida activa. Iniciando una nueva...")
        from bot_service import start_game
        start_result = await start_game()
        if "error" in start_result:
            await update.message.reply_text(f"⚠️ Error al iniciar partida: {start_result['error']}")
            return
        await update.message.reply_text("✅ Nueva partida creada. Reintentando acción...")
        result = await send_action(player, action)

    # Interpretar el tipo de respuesta
    if "error" in result:
        await update.message.reply_text(f"⚠️ Error: {result['error']}")
        return

    # Combate
    if "encounter" in result:
        msg = format_encounter(result)
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # Narrativa / exploración / descanso
    if "narrative" in result or "story_state" in result:
        msg = format_narrative(result)
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # Eco o respuesta genérica
    msg = result.get("message") or result.get("echo") or str(result)
    await update.message.reply_text(f"💬 {msg}")


# ================================================================
# 🚀 Ejecución del bot
# ================================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("state", state))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("🤖 S.A.M. Bot iniciado y escuchando mensajes...")
    app.run_polling()


if __name__ == "__main__":
    main()
