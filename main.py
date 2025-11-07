import os
import logging

from telegram.ext import ApplicationBuilder
from core.handlers.player_handler import register_player_handlers
from core.story_director import StoryDirector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("SAM-Bot")


def get_bot_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN no está definido en las variables de entorno.")
    return token


def main() -> None:
    logger.info("🤖 Iniciando SAM The Dungeon Bot...")

    token = get_bot_token()

    # Instancias core
    story_director = StoryDirector()

    # Construir app de Telegram
    application = ApplicationBuilder().token(token).build()

    # Inyectar dependencias en bot_data (aquí, NO en post_init)
    application.bot_data["story_director"] = story_director

    # Registrar handlers
    register_player_handlers(application)
    logger.info("[PlayerHandler] Comandos /status, /progress y /scene registrados.")
    logger.info("🤖 SAM The Dungeon Bot iniciado correctamente.")
    logger.info("Esperando comandos en Telegram...")

    # Ejecutar bot (sin resolve_used_update_types y sin post_init raro)
    application.run_polling()


if __name__ == "__main__":
    main()
