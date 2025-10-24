# main.py
import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from core.narrator import SAMNarrator
from core.party_events import PartyEventSystem

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
ADMIN_IDS = os.getenv("BOT_ADMINS", "")  # Lista separada por comas de IDs permitidos

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SAM.Bot")

# ================================================================
# 🧙‍♂️ SISTEMAS PRINCIPALES
# ================================================================
narrator = SAMNarrator()
party_events = PartyEventSystem(narrator=narrator)

# ================================================================
# 🧩 FUNCIONES AUXILIARES
# ================================================================
def is_admin(user_id: int) -> bool:
    if not ADMIN_IDS:
        return False
    allowed = [int(x.strip()) for x in ADMIN_IDS.split(",") if x.strip().isdigit()]
    return user_id in allowed

async def api_request(method: str, endpoint: str, json_data: dict | None = None):
    """Hace peticiones a la Game API y devuelve JSON o None."""
    url = f"{GAME_API_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=10.0) as client:
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
        except httpx.HTTPStatusError as e:
            logger.error(f"API error {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error conectando a Game API: {e}")
            return None

# ================================================================
# 🎲 COMANDOS DE PARTY
# ================================================================
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_name = update.effective_user.first_name
    result = await api_request("POST", "/party/join", {"player": player_name})
    if not result:
        await update.message.reply_text(f"⚠️ No se pudo unir a {player_name}.")
        return

    party_data = await api_request("GET", "/party")
    party_size = len(party_data.get("party", [])) if party_data else 1

    msg = party_events.on_player_join(party_size, player_name)
    await update.message.reply_text(msg or f"{player_name} se unió al grupo.")

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

# ================================================================
# 🧹 COMANDO ADMIN: RESETEAR PARTY
# ================================================================
async def reset_party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 No tienes permiso para usar este comando.")
        return

    # Simulamos un "reset" borrando el archivo party.json desde la API
    result = await api_request("POST", "/party/reset", {})
    if result:
        await update.message.reply_text("🧹 El grupo ha sido limpiado. ¡S.A.M. espera nuevos aventureros!")
    else:
        await update.message.reply_text("⚠️ No se pudo limpiar el grupo.")

# ================================================================
# 🚀 INICIO DEL BOT
# ================================================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # comandos
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("leave", leave))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("party", list_party))
    app.add_handler(CommandHandler("resetparty", reset_party))

    logger.info("🤖 S.A.M. conectado con la Game API y listo para narrar...")
    app.run_polling()

if __name__ == "__main__":
    main()
