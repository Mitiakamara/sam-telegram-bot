"""
Process Player Action Use Case
-------------------------------
Caso de uso: Procesar accion de jugador.
Separa la logica de negocio del handler de Telegram.
"""

import logging
from typing import Dict, Any

from core.interfaces import IGameService, IStoryDirector
from core.story_director.director_link import DirectorLink
from core.exceptions import PlayerNotFoundError, GameAPIError

logger = logging.getLogger(__name__)


class ProcessPlayerActionUseCase:
    """
    Caso de uso: Procesar accion de jugador.
    
    Coordina:
    1. Validacion del jugador
    2. Procesamiento de accion a traves de GameAPI
    3. Procesamiento narrativo a traves de DirectorLink
    4. Actualizacion de estado emocional y temas
    """

    def __init__(
        self,
        game_service: IGameService,
        story_director: IStoryDirector,
        director_link: DirectorLink,
    ):
        self.game_service = game_service
        self.story_director = story_director
        self.director_link = director_link

    async def execute(self, player_id: int, action_text: str) -> Dict[str, Any]:
        # 1. Validar jugador
        player = self.story_director.get_player(player_id)
        if not player:
            raise PlayerNotFoundError(f"Jugador con ID {player_id} no encontrado")

        player_name = player.get("name", "Unknown")

        # 2. Obtener contexto de la escena actual
        scene_context = None
        try:
            current_scene_data = self.story_director.get_current_scene()
            if current_scene_data.get("found") and current_scene_data.get("scene"):
                scene = current_scene_data["scene"]
                scene_title = scene.get("title", "")
                
                # Solo usar contexto si es una escena real (no generica)
                if scene_title and scene_title not in ["Escena actual", "Unknown", ""]:
                    scene_context = {
                        "title": scene_title,
                        "description": scene.get("narration", scene.get("description", "")),
                        "location": scene_title,
                        "npcs": [npc.get("name", npc) if isinstance(npc, dict) else npc 
                                 for npc in scene.get("npcs", [])],
                        "options": [opt.get("text", opt) if isinstance(opt, dict) else opt 
                                    for opt in scene.get("options", [])],
                        "mood": scene.get("mood", scene.get("scene_type", "")),
                    }
                    logger.info(f"[ProcessPlayerAction] Contexto de escena: {scene_title}")
                else:
                    logger.warning("[ProcessPlayerAction] Escena generica detectada. Usa /loadcampaign para cargar una aventura.")
        except Exception as e:
            logger.warning(f"[ProcessPlayerAction] No se pudo obtener contexto de escena: {e}")

        # 3. Procesar accion a traves de GameAPI
        result = await self.game_service.process_action(
            player_name=player_name, 
            action_text=action_text,
            character_data=player,
            scene_context=scene_context
        )

        if not result.get("success"):
            error_msg = result.get("error", "Error desconocido")
            raise GameAPIError(f"Error del GameAPI: {error_msg}")

        # 4. Obtener respuesta narrativa
        narrative_raw = result.get("result", "")
        event = result.get("event")

        # 5. Procesar resultado narrativo a traves de DirectorLink
        game_result = {
            "action": action_text,
            "outcome": "success" if result.get("success") else "failure",
            "emotion": "neutral",
            "description": narrative_raw,
            "event": event,
        }

        narrative = await self.director_link.process_game_result(game_result)

        # 6. Actualizar estado emocional si hay evento
        if event and hasattr(self.story_director, "emotion_tracker"):
            event_type = event.get("event_type", "")
            emotion_tracker = self.story_director.emotion_tracker
            
            if event_type in ["combat_victory", "triumph"]:
                if hasattr(emotion_tracker, "record_emotion"):
                    emotion_tracker.record_emotion("triumph", 0.8)
            elif event_type in ["setback", "loss"]:
                if hasattr(emotion_tracker, "record_emotion"):
                    emotion_tracker.record_emotion("setback", 0.7)

            if hasattr(self.story_director, "theme_tracker"):
                event_narration = event.get("event_narration", "")
                if event_narration:
                    game_state = {"description": event_narration}
                    theme = self.story_director.theme_tracker.detect_theme(game_state)
                    logger.debug(f"[ProcessPlayerAction] Tema detectado: {theme}")

        return {
            "narrative": narrative,
            "player_name": player_name,
            "event": event,
        }
