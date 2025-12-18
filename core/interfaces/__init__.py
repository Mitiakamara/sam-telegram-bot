"""
Interfaces Module
-----------------
Define protocols/interfaces para servicios principales.
Facilita testing y permite intercambiar implementaciones.
"""

from typing import Protocol, Dict, Any, Optional, List

__all__ = [
    "IGameService",
    "ICampaignManager",
    "IStoryDirector",
]


class IGameService(Protocol):
    """
    Protocolo para GameService.
    Define la interfaz que debe cumplir cualquier implementación de GameService.
    """

    async def process_action(
        self, player_name: str, action_text: str, mode: str = "action"
    ) -> Dict[str, Any]:
        """
        Procesa una acción del jugador.
        
        Args:
            player_name: Nombre del jugador
            action_text: Acción en lenguaje natural
            mode: "action" o "dialogue"
        
        Returns:
            Dict con "success", "result", y opcionalmente "event"
        """
        ...

    async def start_game(
        self, party_levels: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Inicia una nueva partida.
        
        Args:
            party_levels: Lista de niveles de los jugadores
        
        Returns:
            Dict con el estado inicial del juego
        """
        ...

    async def get_game_state(self) -> Dict[str, Any]:
        """Obtiene el estado actual del juego."""
        ...

    async def join_party(self, player_name: str) -> Dict[str, Any]:
        """Agrega un jugador al grupo."""
        ...

    async def get_party(self) -> Dict[str, Any]:
        """Obtiene la lista de jugadores en el grupo."""
        ...


class ICampaignManager(Protocol):
    """
    Protocolo para CampaignManager.
    Define la interfaz que debe cumplir cualquier implementación de CampaignManager.
    """

    def get_player_by_telegram_id(
        self, telegram_id: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene un jugador por su ID de Telegram."""
        ...

    def add_player(
        self,
        telegram_id: Optional[int] = None,
        player_name: Optional[str] = None,
        player_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Agrega un jugador a la campaña.
        
        Args:
            telegram_id: ID de Telegram del jugador
            player_name: Nombre del jugador
            player_data: Datos del personaje
        
        Returns:
            Clave del jugador en el diccionario
        """
        ...

    def get_active_party(self) -> List[int]:
        """Obtiene la lista de IDs de Telegram de la party activa."""
        ...

    def get_active_scene(self) -> Optional[Dict[str, Any]]:
        """Obtiene la escena activa actual."""
        ...

    def set_current_scene(self, scene_name: str) -> None:
        """Establece la escena actual."""
        ...

    def get_progress(self) -> Dict[str, Any]:
        """Obtiene el progreso de la campaña."""
        ...


class IStoryDirector(Protocol):
    """
    Protocolo para StoryDirector.
    Define la interfaz que debe cumplir cualquier implementación de StoryDirector.
    """

    def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un jugador por su ID de usuario."""
        ...

    def create_player_character(
        self, user_id: int, name: str
    ) -> Dict[str, Any]:
        """Crea un personaje de jugador."""
        ...

    def render_current_scene(self) -> str:
        """Renderiza la escena actual como texto."""
        ...

    def trigger_event(self, event_type: str) -> str:
        """Dispara un evento narrativo."""
        ...

    def get_campaign_progress(self) -> Dict[str, Any]:
        """Obtiene el progreso de la campaña."""
        ...
