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
        # Para que falle rápido si no hay token
        raise RuntimeError("TELEGRAM_BOT_TOKEN no está definido en las variables de entorno.")
    return token


def main() -> None:
    """
    Punto de entrada del bot.
    IMPORTANTE: versión síncrona, sin asyncio.run(), para que en Render
    no nos dé 'This event loop is already running'.
    """
    logger.info("🤖 Iniciando SAM The Dungeon Bot...")

    token = get_bot_token()

    # Instanciamos el StoryDirector global (lo usan los handlers)
    story_director = StoryDirector()

    # Construimos la app de telegram
    application = (
        ApplicationBuilder()
        .token(token)
        # pasamos el director por context.bot_data para que los handlers lo tengan
        .post_init(lambda app: app.bot_data.update({"story_director": story_director}))
        .build()
    )

    # Registramos los comandos de jugador
    register_player_handlers(application)
    logger.info("[PlayerHandler] Comandos /status, /progress y /scene registrados.")

    logger.info("🤖 SAM The Dungeon Bot iniciado correctamente.")
    logger.info("Esperando comandos en Telegram...")

    # Esto BLOQUEA el hilo y es lo que queremos en Render.
    application.run_polling(allowed_updates=application.resolve_used_update_types())


if __name__ == "__main__":
    main()
