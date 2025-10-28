# sam-telegram-bot/main.py
import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from core.narrator import SAMNarrator
from core.party_events import PartyEventSystem
from core.orchestrator import Orchestrator
from core.story_director.recap_manager import RecapManager
# 🧩 NUEVO: Character Builder guiado (con 27 point buy)
from core.character_builder import start_character_creation, handle_response, handle_callback

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
ADMIN_IDS = os.getenv("BOT_ADMINS", "")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SAM.Bot")

# ================================================================
# 🧙‍♂️ SISTEMAS PRINCIPALES
# ================================================================
narrator = SAMNarrator()
party_events = PartyEventSystem(narrator=narrator)
orchestrator = Orchestrator()

# ================================================================
# 🧩 UTILIDADES
# ================================================================
def is_admin(user_id: int) -> bool:
    if not ADMIN_IDS:
        return False
    allowed = [int(x.strip()) for x in ADMIN_IDS.split(",") if x.strip().isdigit()]
    return user_id in allowed


async def api_request(method: str, endpoint: str, json_data: dict | None = None):
    url = f"{GAME_API_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            if method == "GET":
                r = await client.get(url)
            elif method == "POST":
                r = await client.post(url, json=json_data)
            elif method == "DELETE":
                r = await client.delete(url)
            else:
                raise ValueError("Método HTTP no soportado.")
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"❌ Error en request {endpoint}: {e}")
            return None


async def maybe_reply_mood(update: Update, prefix: str = ""):
    try:
        if hasattr(orchestrator, "get_current_mood"):
            mood = orchestrator.get_current_mood()
            if isinstance(mood, dict) and mood.get("mood_state"):
                txt = (
                    f"{prefix}🌡️ *Estado tonal:* `{mood['mood_state']}` "
                    f"(intensidad {mood.get('mood_intensity', '?')}) · "
                    f"género: `{mood.get('genre_profile', '?')}`"
                )
                await update.message.reply_text(txt, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"No se pudo obtener mood actual: {e}")

# ================================================================
# 🧙‍♂️ CREATE CHARACTER – modo GUIADO SRD
# ================================================================
async def create_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Nueva versión: invoca el Character Builder guiado con 27 Point Buy.
    """
    await update.message.reply_text(
        "🧙‍♂️ Iniciando creación de personaje.\n\n"
        "Responde las preguntas paso a paso para definir nombre, raza, clase, atributos, habilidades y hechizos."
    )
    await start_character_creation(update, context)

# ================================================================
# 🎲 PARTY COMMANDS (join/leave/etc.)
# ================================================================
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_name = update.effective_user.first_name
    try:
        result = await api_request("POST", "/party/join", {"player": player_name})
        new_party = not result
        if new_party:
            await update.message.reply_text("⚠️ El grupo parecía vacío... creando uno nuevo.")
            _ = await api_request("POST", "/party/reset", {})
            _ = await api_request("POST", "/party/join", {"player": player_name})
        party_data = await api_request("GET", "/party")
        size = len(party_data.get("party", [])) if party_data else 1
        msg = party_events.on_player_join(size, player_name) or f"{player_name} se une a la aventura."
        await update.message.reply_text(msg)
        if size > 1:
            members = "\n".join(f"• {n}" for n in party_data["party"])
            await update.message.reply_text(f"👥 *Grupo actual:*\n{members}", parse_mode="Markdown")
        if new_party:
            intro = await orchestrator.start_new_session()
            await update.message.reply_text("🌄 *Inicio de la aventura...*", parse_mode="Markdown")
            await update.message.reply_text(intro, parse_mode="Markdown")
            await maybe_reply_mood(update, "")
    except Exception as e:
        await update.message.reply_text(f"⚠️ No se pudo unir a {player_name}: {e}")

async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    result = await api_request("POST", "/party/leave", {"player": name})
    msg = party_events.on_player_leave(0, name, kicked=False)
    await update.message.reply_text(msg or f"{name} dejó el grupo.")

async def list_party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = await api_request("GET", "/party")
    if not result or not result.get("party"):
        await update.message.reply_text("🎲 No hay aventureros en el grupo todavía.")
        return
    members = "\n".join(f"• {n}" for n in result["party"])
    await update.message.reply_text(f"👥 *Grupo actual:*\n{members}", parse_mode="Markdown")

# ================================================================
# 🧹 RESET PARTY / CAMPAÑA
# ================================================================
async def reset_party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 No tienes permiso para usar este comando.")
        return

    result = await api_request("POST", "/party/reset", {})
    api_ok = bool(result)
    base_path = "data/"
    files = ["game_state.json", "scenes_history.json", "scene_state.json"]
    cleared = []
    import json
    for f in files:
        path = os.path.join(base_path, f)
        os.makedirs(base_path, exist_ok=True)
        with open(path, "w", encoding="utf-8") as wf:
            if "game_state" in f:
                json.dump(
                    {"mood_state": "neutral", "mood_intensity": 0.5, "genre_profile": "heroic", "last_update": None},
                    wf, indent=2, ensure_ascii=False)
            elif "scenes_history" in f:
                wf.write("[]")
            else:
                wf.write("{}")
        cleared.append(f)
    if hasattr(orchestrator.story_director, "mood_manager"):
        orchestrator.story_director.mood_manager.__init__(os.path.join(base_path, "game_state.json"))
    msg = "🧹 *Campaña reiniciada completamente.*\n"
    if api_ok:
        msg += "🎲 Grupo en GameAPI limpiado.\n"
    msg += f"📜 Archivos reiniciados: `{', '.join(cleared)}`\n🌄 Nueva historia en preparación..."
    await update.message.reply_text(msg, parse_mode="Markdown")
    intro = await orchestrator.start_new_session()
    await update.message.reply_text(intro, parse_mode="Markdown")
    await maybe_reply_mood(update, "")

# ================================================================
# 🌌 CONTINUE / RECAP / MOOD
# ================================================================
async def continue_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await orchestrator.handle_continue(update.effective_user.id)
    await update.message.reply_text(msg, parse_mode="Markdown")
    await maybe_reply_mood(update, "")

async def recap_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recap = RecapManager().generate_recap()
    await update.message.reply_text(recap, parse_mode="Markdown")

async def show_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mood = orchestrator.get_current_mood()
    await update.message.reply_text(
        f"🌡️ *Estado tonal global:*\n- Mood: `{mood['mood_state']}`\n"
        f"- Intensidad: `{mood['mood_intensity']}`\n- Género: `{mood['genre_profile']}`",
        parse_mode="Markdown")

# ================================================================
# 💬 TEXTO LIBRE
# ================================================================
def detect_player_emotion(text: str):
    t = text.lower()
    if any(w in t for w in ["aburrido", "meh"]): return ("bored", -0.2)
    if any(w in t for w in ["wow", "épico", "genial"]): return ("excited", +0.3)
    if any(w in t for w in ["miedo", "tenso"]): return ("fear", +0.2)
    if any(w in t for w in ["triste", "melancólico"]): return ("sad", -0.1)
    return None

async def handle_free_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    text = update.message.text.strip()
    if text.lower() in ["continuar", "seguir", "avanzar"]:
        msg = await orchestrator.handle_continue(update.effective_user.id)
        await update.message.reply_text(msg, parse_mode="Markdown")
        await maybe_reply_mood(update, "")
        return
    result = await api_request("POST", "/game/action", {"player": name, "action": text, "mode": "action"})
    narration = result.get("result", "S.A.M. no entiende lo que intentas hacer.")
    await update.message.reply_text(narration)
    emo = detect_player_emotion(text)
    if emo: orchestrator.apply_feedback(*emo); await maybe_reply_mood(update, "")

# ================================================================
# 🚀 MAIN
# ================================================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # 🔹 Integración del Character Builder guiado
    app.add_handler(CommandHandler("createcharacter", create_character))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))
    app.add_handler(CallbackQueryHandler(handle_callback))

    # 🔹 Resto del sistema de juego
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("leave", leave))
    app.add_handler(CommandHandler("party", list_party))
    app.add_handler(CommandHandler("resetparty", reset_party))
    app.add_handler(CommandHandler("continue", continue_story))
    app.add_handler(CommandHandler("recap", recap_story))
    app.add_handler(CommandHandler("mood", show_mood))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text))

    logger.info("🤖 S.A.M. listo: modo narrativo + Character Builder SRD activo.")
    app.run_polling()

if __name__ == "__main__":
    main()
