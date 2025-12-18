import os
import logging
from dotenv import load_dotenv

from telegram.ext import ApplicationBuilder

# importa tu campaign manager real
from core.campaign.campaign_manager import CampaignManager
# importa el registro de handlers actualizado
from core.handlers.player_handler import register_player_handlers
from core.handlers.narrative_handler import register_narrative_handlers
from core.handlers.campaign_handler import register_campaign_handlers
from core.handlers.conversation_handler import register_conversation_handler
# importa StoryDirector
from core.story_director.story_director import StoryDirector
# importa GameService
from core.services.game_service import GameService
# importa ServiceContainer para inyección de dependencias
from core.container.service_container import ServiceContainer

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

    logger.info("🤖 Iniciando SAM The Dungeon Bot...")

    # Crear ServiceContainer para gestión centralizada de servicios
    container = ServiceContainer()
    
    logger.info("✅ ServiceContainer creado - Servicios disponibles bajo demanda")

    # construimos la aplicación de telegram
    application = ApplicationBuilder().token(bot_token).build()
    
    # Guardar container y servicios en bot_data para que los handlers puedan accederlos
    application.bot_data["container"] = container
    application.bot_data["story_director"] = container.story_director
    application.bot_data["game_service"] = container.game_service
    application.bot_data["campaign_manager"] = container.campaign_manager

    # registramos TODOS los comandos de jugador
    register_player_handlers(application, container.campaign_manager)
    
    # registramos handlers narrativos (/scene, /event)
    register_narrative_handlers(application)
    
    # registramos handlers de campaña (/progress, /restart, /loadcampaign)
    register_campaign_handlers(application)
    
    # registramos handler conversacional (procesa mensajes libres)
    # IMPORTANTE: Este debe ir DESPUÉS de los command handlers
    # Ahora usa casos de uso para separar lógica de negocio
    register_conversation_handler(
        application,
        campaign_manager=container.campaign_manager,
        game_service=container.game_service,
        story_director=container.story_director,
    )

    # handler de errores para que no se pierdan en logs
    async def error_handler(update, context) -> None:
        logger.exception(
            "Error manejando update %s: %s", update, context.error, exc_info=context.error
        )

    application.add_error_handler(error_handler)

    logger.info("🤖 SAM The Dungeon Bot iniciado correctamente.")
    logger.info("✅ Modo conversacional activado - Los jugadores pueden usar lenguaje natural.")
    logger.info("Esperando comandos y mensajes en Telegram...")

    # IMPORTANTE: usa polling directo, sin asyncio.run, como ya viste que Render acepta
    # drop_pending_updates=True evita que se procesen updates viejos al reiniciar
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
