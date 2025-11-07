import os
import logging
from dotenv import load_dotenv

from telegram.ext import ApplicationBuilder

# importa tu campaign manager real
from core.campaign.campaign_manager import CampaignManager
# importa el registro de handlers actualizado
from core.handlers.player_handler import register_player_handlers

# ---------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("SAM-Bot")


def main() -> None:
    """Punto de entrada síncrono, compatible con Render."""
    load_dotenv()

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN no está definido en el entorno.")

    # instancia única del estado de campaña
    campaign_manager = CampaignManager()
    logger.info("🤖 Iniciando SAM The Dungeon Bot...")

    # construimos la aplicación de telegram
    application = ApplicationBuilder().token(bot_token).build()

    # registramos TODOS los comandos de jugador
    register_player_handlers(application, campaign_manager)

    # handler de errores para que no se pierdan en logs
    async def error_handler(update, context) -> None:
        logger.exception(
            "Error manejando update %s: %s", update, context.error, exc_info=context.error
        )

    application.add_error_handler(error_handler)

    logger.info("🤖 SAM The Dungeon Bot iniciado correctamente.")
    logger.info("Esperando comandos en Telegram...")

    # IMPORTANTE: usa polling directo, sin asyncio.run, como ya viste que Render acepta
    # drop_pending_updates=True evita que se procesen updates viejos al reiniciar
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
