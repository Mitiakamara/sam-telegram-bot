"""
Process Player Action Use Case
-------------------------------
Caso de uso: Procesar acción de jugador.
Separa la lógica de negocio del handler de Telegram.
"""

import logging
from typing import Dict, Any

from core.interfaces import IGameService, IStoryDirector
from core.story_director.director_link import DirectorLink
from core.exceptions import PlayerNotFoundError, GameAPIError

logger = logging.getLogger(__name__)


class ProcessPlayerActionUseCase:
    """
    Caso de uso: Procesar acción de jugador.
    
    Coordina:
    1. Validación del jugador
    2. Procesamiento de acción a través de GameAPI
    3. Procesamiento narrativo a través de DirectorLink
    4. Actualización de estado emocional y temas
    """

    def __init__(
        self,
        game_service: IGameService,
        story_director: IStoryDirector,
        director_link: DirectorLink,
    ):
        """
        Inicializa el caso de uso.
        
        Args:
            game_service: Servicio para procesar acciones del juego
            story_director: Director narrativo
            director_link: Enlace para procesar resultados narrativos
        """
        self.game_service = game_service
        self.story_director = story_director
        self.director_link = director_link

    async def execute(
        self, player_id: int, action_text: str
    ) -> Dict[str, Any]:
        """
        Ejecuta el caso de uso completo.
        
        Args:
            player_id: ID de Telegram del jugador
            action_text: Acción en lenguaje natural
        
        Returns:
            Dict con:
                - narrative: Texto narrativo procesado
                - player_name: Nombre del jugador
                - event: Evento dinámico si se generó (opcional)
        
        Raises:
            PlayerNotFoundError: Si el jugador no existe
            GameAPIError: Si hay error comunicándose con GameAPI
        """
        # 1. Validar jugador
        player = self.story_director.get_player(player_id)
        if not player:
            raise PlayerNotFoundError(
                f"Jugador con ID {player_id} no encontrado"
            )

        player_name = player.get("name", "Unknown")

        # 2. Procesar acción a través de GameAPI
        result = await self.game_service.process_action(
            player_name=player_name, action_text=action_text
        )

        if not result.get("success"):
            error_msg = result.get("error", "Error desconocido")
            raise GameAPIError(f"Error del GameAPI: {error_msg}")

        # 3. Obtener respuesta narrativa
        narrative_raw = result.get("result", "")
        event = result.get("event")

        # 4. Procesar resultado narrativo a través de DirectorLink
        game_result = {
            "action": action_text,
            "outcome": "success" if result.get("success") else "failure",
            "emotion": "neutral",  # Se puede extraer del resultado si está disponible
            "description": narrative_raw,
            "event": event,
        }

        narrative = await self.director_link.process_game_result(game_result)

        # 5. Actualizar estado emocional si hay evento (si está disponible)
        if event and hasattr(self.story_director, "emotion_tracker"):
            event_type = event.get("event_type", "")
            emotion_tracker = self.story_director.emotion_tracker
            
            if event_type in ["combat_victory", "triumph"]:
                if hasattr(emotion_tracker, "record_emotion"):
                    emotion_tracker.record_emotion("triumph", 0.8)
                elif hasattr(emotion_tracker, "set_emotion"):
                    emotion_tracker.set_emotion("triumph")
            elif event_type in ["setback", "loss"]:
                if hasattr(emotion_tracker, "record_emotion"):
                    emotion_tracker.record_emotion("setback", 0.7)
                elif hasattr(emotion_tracker, "set_emotion"):
                    emotion_tracker.set_emotion("setback")

            # 6. Detectar tema narrativo del evento (si está disponible)
            if hasattr(self.story_director, "theme_tracker"):
                event_narration = event.get("event_narration", "")
                if event_narration:
                    game_state = {"description": event_narration}
                    theme = self.story_director.theme_tracker.detect_theme(game_state)
                    logger.debug(
                        f"[ProcessPlayerActionUseCase] Tema detectado: {theme}"
                    )

        return {
            "narrative": narrative,
            "player_name": player_name,
            "event": event,
        }
