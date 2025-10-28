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
# 🔹 Importar Character Builder
from core.character_builder import start_character_creation, handle_response, handle_callback, builder_state

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
# 🔄 HANDLER UNIFICADO DE TEXTO
# ================================================================
async def unified_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Decide si el texto pertenece al flujo de creación de personaje o al modo narrativo.
    """
    user_id = update.effective_user.id
    # 🔸 Si el jugador está en proceso de creación de personaje
    if user_id in builder_state:
        processed = await handle_response(update, context)
        if processed:
            return
    # 🔸 Si no, texto pasa al narrador
    await handle_free_text(update, context)

# ================================================================
# 🎲 PARTY / HISTORIA / EMOCIONES (idénticos a tu versión actual)
# ================================================================
# (se mantiene todo el bloque de funciones join, leave, resetparty, etc.)
# 💬 handle_free_text se mantiene igual

# ================================================================
# 🚀 MAIN
# ================================================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Character Builder
    app.add_handler(CommandHandler("createcharacter", start_character_creation))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unified_text_handler))

    # Sistema de historia (sin cambios)
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("leave", leave))
    app.add_handler(CommandHandler("party", list_party))
    app.add_handler(CommandHandler("resetparty", reset_party))
    app.add_handler(CommandHandler("continue", continue_story))
    app.add_handler(CommandHandler("recap", recap_story))
    app.add_handler(CommandHandler("mood", show_mood))

    logger.info("🤖 S.A.M. listo: modo narrativo + Character Builder SRD activo (con control de contexto).")
    app.run_polling()

if __name__ == "__main__":
    main()
