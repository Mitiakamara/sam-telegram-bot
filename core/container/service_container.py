"""
Service Container
-----------------
Contenedor de servicios con inyección de dependencias.
Centraliza la creación y gestión de todas las instancias de servicios.
"""

import logging
from typing import Optional

from core.campaign.campaign_manager import CampaignManager
from core.story_director.story_director import StoryDirector
from core.services.game_service import GameService

logger = logging.getLogger(__name__)


class ServiceContainer:
    """
    Contenedor de servicios con inyección de dependencias.
    Gestiona el ciclo de vida de todos los servicios principales.
    """

    def __init__(self):
        """Inicializa el contenedor con servicios None (lazy initialization)."""
        self._campaign_manager: Optional[CampaignManager] = None
        self._story_director: Optional[StoryDirector] = None
        self._game_service: Optional[GameService] = None
        logger.info("[ServiceContainer] Contenedor inicializado.")

    @property
    def campaign_manager(self) -> CampaignManager:
        """
        Obtiene o crea la instancia de CampaignManager.
        Lazy initialization: solo se crea cuando se accede por primera vez.
        """
        if self._campaign_manager is None:
            self._campaign_manager = CampaignManager()
            logger.info("[ServiceContainer] CampaignManager creado.")
        return self._campaign_manager

    @property
    def story_director(self) -> StoryDirector:
        """
        Obtiene o crea la instancia de StoryDirector.
        Inyecta automáticamente CampaignManager para evitar duplicación.
        Compatible con versiones que aceptan y no aceptan campaign_manager.
        """
        if self._story_director is None:
            # Intentar crear con campaign_manager (Fase 1)
            # Si falla, crear sin parámetros (versión antigua)
            import inspect
            sig = inspect.signature(StoryDirector.__init__)
            
            if 'campaign_manager' in sig.parameters:
                # Versión que acepta campaign_manager
                self._story_director = StoryDirector(
                    campaign_manager=self.campaign_manager
                )
                logger.info("[ServiceContainer] StoryDirector creado con CampaignManager inyectado.")
            else:
                # Versión antigua - crear sin parámetros
                # IMPORTANTE: Reemplazar el CampaignManager interno con el del container
                # para evitar duplicación de estado
                self._story_director = StoryDirector()
                # Reemplazar el campaign_manager interno con el compartido
                self._story_director.campaign_manager = self.campaign_manager
                logger.info("[ServiceContainer] StoryDirector creado y CampaignManager compartido asignado.")
        return self._story_director

    @property
    def game_service(self) -> GameService:
        """
        Obtiene o crea la instancia de GameService.
        Lazy initialization: solo se crea cuando se accede por primera vez.
        """
        if self._game_service is None:
            self._game_service = GameService()
            logger.info("[ServiceContainer] GameService creado.")
        return self._game_service

    def reset(self) -> None:
        """
        Resetea todas las instancias de servicios.
        Útil para testing o reinicio completo.
        """
        self._campaign_manager = None
        self._story_director = None
        self._game_service = None
        logger.info("[ServiceContainer] Todos los servicios reseteados.")
