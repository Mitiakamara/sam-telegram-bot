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
    ContextTypes,
    filters,
)

from core.narrator import SAMNarrator
from core.party_events import PartyEventSystem
from core.orchestrator import Orchestrator  # 🧠 Motor narrativo adaptativo
from core.story_director.recap_manager import RecapManager  # 🧩 Resumen narrativo dinámico

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
ADMIN_IDS = os.getenv("BOT_ADMINS", "")  # IDs separados por comas

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SAM.Bot")

# ================================================================
# 🧙‍♂️ SISTEMAS PRINCIPALES
# ================================================================
narrator = SAMNarrator()
party_events = PartyEventSystem(narrator=narrator)
orchestrator = Orchestrator()  # 🔗 Orquesta GameAPI, SceneManager y StoryDirector

# ================================================================
# 🧩 UTILIDADES
# ================================================================
def is_admin(user_id: int) -> bool:
    """Verifica si un usuario es administrador."""
    if not ADMIN_IDS:
        return False
    allowed = [int(x.strip()) for x in ADMIN_IDS.split(",") if x.strip().isdigit()]
    return user_id in allowed


async def api_request(method: str, endpoint: str, json_data: dict | None = None):
    """Realiza peticiones HTTP a la Game API."""
    url = f"{GAME_API_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=json_data)
            elif method == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError("Método HTTP no soportado.")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error en request {endpoint}: {e}")
            return None

# ================================================================
# 🎲 COMANDOS DE PARTY (con hotfix + narración automática)
# ================================================================
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Permite que un jugador se una al grupo.
    Crea automáticamente la party si no existe o si el GameAPI devuelve error.
    Además, inicia una narración introductoria cuando la party se crea por primera vez.
    """
    player_name = update.effective_user.first_name
    user_id = update.effective_user.id

    try:
        # Intentar unirse a la party vía GameAPI
        result = await api_request("POST", "/party/join", {"player": player_name})
        new_party_created = False

        # Si la API no responde o devuelve error, crear una nueva party
        if not result:
            new_party_created = True
            await update.message.reply_text(
                "⚠️ El grupo parecía vacío... S.A.M. aviva una nueva fogata en medio de la noche."
            )
            _ = await api_request("POST", "/party/reset", {})
            _ = await api_request("POST", "/party/join", {"player": player_name})
            result = {"success": True}

        # Obtener lista de miembros actualizada
        party_data = await api_request("GET", "/party")
        party_size = len(party_data.get("party", [])) if party_data else 1

        # Mensaje narrativo usando PartyEventSystem (si existe)
        msg = party_events.on_player_join(party_size, player_name)
        if not msg:
            msg = f"🧙‍♂️ {player_name} se une a la aventura."

        await update.message.reply_text(msg)

        # Mostrar estado del grupo si hay más miembros
        if party_size > 1:
            members = "\n".join(f"• {name}" for name in party_data["party"])
            await update.message.reply_text(
                f"👥 *Grupo actual:*\n{members}", parse_mode="Markdown"
            )

        # 🌄 Narración de introducción si la party fue creada por primera vez
        if new_party_created:
            await update.message.reply_text("🌄 *Inicio de la aventura...*", parse_mode="Markdown")
            intro_message = await orchestrator.start_new_session()
            await update.message.reply_text(intro_message, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(
            f"⚠️ No se pudo unir a {player_name}. S.A.M. murmura: «{e}»"
        )


async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_name = update.effective_user.first_name
    result = await api_request("POST", "/party/leave", {"player": player_name})
    if not result:
        await update.message.reply_text(f"⚠️ No se pudo remover a {player_name}.")
        return

    party_data = await api_request("GET", "/party")
    party_size = len(party_data.get("party", [])) if party_data else 0
    msg = party_events.on_player_leave(party_size, player_name, kicked=False)
    await update.message.reply_text(msg or f"{player_name} dejó el grupo.")


async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /kick <nombre>")
        return

    target = context.args[0]
    result = await api_request("POST", "/party/kick", {"player": target})
    if not result:
        await update.message.reply_text(f"⚠️ No se pudo expulsar a {target}.")
        return

    party_data = await api_request("GET", "/party")
    party_size = len(party_data.get("party", [])) if party_data else 0
    msg = party_events.on_player_leave(party_size, target, kicked=True)
    await update.message.reply_text(msg or f"{target} fue expulsado del grupo.")


async def list_party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = await api_request("GET", "/party")
    if not result or not result.get("party"):
        await update.message.reply_text("🎲 No hay aventureros en el grupo todavía.")
        return

    members = "\n".join(f"• {name}" for name in result["party"])
    await update.message.reply_text(f"👥 *Grupo actual:*\n{members}", parse_mode="Markdown")


async def reset_party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 No tienes permiso para usar este comando.")
        return

    result = await api_request("POST", "/party/reset", {})
    if result:
        await update.message.reply_text("🧹 El grupo ha sido limpiado. ¡S.A.M. espera nuevos aventureros!")
    else:
        await update.message.reply_text("⚠️ No se pudo limpiar el grupo.")

# ================================================================
# 🌌 COMANDO /CONTINUE (StoryDirector Integration)
# ================================================================
async def continue_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cierra la escena actual y genera automáticamente la siguiente."""
    player_id = update.effective_user.id
    logger.info(f"Comando /continue ejecutado por {update.effective_user.username}")

    try:
        message = await orchestrator.handle_continue(player_id)
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error en /continue: {e}")
        await update.message.reply_text("⚠️ No se pudo continuar la historia en este momento.")

# ================================================================
# 🧠 COMANDO /RECAP – Resumen narrativo dinámico
# ================================================================
async def recap_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera un resumen del viaje usando la memoria narrativa."""
    recap = RecapManager().generate_recap()
    await update.message.reply_text(recap, parse_mode="Markdown")

# ================================================================
# 💬 CONVERSACIÓN NATURAL (acciones y narrativa adaptativa)
# ================================================================
async def handle_free_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Interpreta mensajes sin comando como acciones o diálogos, o los envía al motor narrativo."""
    player_name = update.effective_user.first_name
    text = update.message.text.strip()
    if not text:
        return

    lowered = text.lower()

    # 👉 Integración con StoryDirector: si el jugador escribe "continuar"
    if lowered in ["continuar", "seguir", "avanzar"]:
        message = await orchestrator.handle_continue(update.effective_user.id)
        await update.message.reply_text(message, parse_mode="Markdown")
        return

    # Detección de intención
    if lowered.startswith(("digo", "hablo", "pregunto", "susurro")):
        mode = "dialogue"
    else:
        mode = "action"

    # Enviar acción al motor de juego (GameAPI)
    result = await api_request("POST", "/game/action", {
        "player": player_name,
        "action": text,
        "mode": mode
    })

    if not result or "result" not in result:
        await update.message.reply_text("🤔 S.A.M. no entiende lo que intentas hacer.")
        return

    narration = result["result"]
    await update.message.reply_text(narration)

    if "event" in result:
        event = result["event"]
        event_text = (
            f"\n\n🔮 *Evento: {event['event_title']}*"
            f"\n_Tipo:_ {event['event_type'].capitalize()}"
            f"\n\n{event['event_narration']}"
        )
        await update.message.reply_text(event_text, parse_mode="Markdown")

# ================================================================
# 🚀 INICIO DEL BOT
# ================================================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Comandos de gestión
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("leave", leave))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("party", list_party))
    app.add_handler(CommandHandler("resetparty", reset_party))
    app.add_handler(CommandHandler("continue", continue_story))  # 🧭 Motor narrativo adaptativo
    app.add_handler(CommandHandler("recap", recap_story))        # 🧠 Nueva recapitulación

    # Modo conversacional
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text))

    logger.info("🤖 S.A.M. conectado y escuchando en modo narrativo + eventos + StoryDirector + Memoria.")
    app.run_polling()


if __name__ == "__main__":
    main()
