import json
import os
import logging
from typing import Dict, Any, Optional

from core.campaign.campaign_manager import CampaignManager
from core.auto_narrator import AutoNarrator
from core.character_builder import CharacterBuilder

logger = logging.getLogger(__name__)


class EmotionalTracker:
    """
    Versión mínima para no romper cuando el handler llama a get_current_emotion().
    """
    def __init__(self) -> None:
        self.current_emotion = "neutral"
        logger.info("[EmotionalTracker] Inicializado correctamente.")

    def get_current_emotion(self) -> str:
        return self.current_emotion

    def set_emotion(self, emotion: str) -> None:
        self.current_emotion = emotion


class StoryDirector:
    """
    Orquesta la historia, los jugadores y la campaña.
    """

    STATE_PATH = "data/story_director_state.json"

    def __init__(self) -> None:
        self.emotion_tracker = EmotionalTracker()
        self.campaign_manager = CampaignManager()
        self.auto_narrator = AutoNarrator()
        self.character_builder = CharacterBuilder()
        self.players: Dict[int, Dict[str, Any]] = {}

        # intentar cargar estado previo
        self._ensure_data_dir()
        self._load_state()

    # ------------------------------------------------------------------
    # Persistencia básica
    # ------------------------------------------------------------------
    def _ensure_data_dir(self) -> None:
        os.makedirs("data", exist_ok=True)

    def _load_state(self) -> None:
        if os.path.exists(self.STATE_PATH):
            try:
                with open(self.STATE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.players = data.get("players", {})
                self.campaign_manager.load_from_dict(data.get("campaign", {}))
                logger.info("[StoryDirector] Estado cargado correctamente.")
            except Exception as e:
                logger.warning(f"[StoryDirector] No se pudo cargar el estado: {e}")

    def _save_state(self) -> None:
        data = {
            "players": self.players,
            "campaign": self.campaign_manager.to_dict(),
        }
        try:
            with open(self.STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("[StoryDirector] Estado guardado.")
        except Exception as e:
            logger.warning(f"[StoryDirector] No se pudo guardar el estado: {e}")

    # ------------------------------------------------------------------
    # Gestión de jugadores
    # ------------------------------------------------------------------
    def create_player_character(self, user_id: int, name: str) -> Dict[str, Any]:
        """
        Crea un PJ con el CharacterBuilder y lo asocia al user_id.
        """
        character = self.character_builder.create_character(name)
        self.players[user_id] = character
        # lo añadimos a la campaña
        self.campaign_manager.add_player(user_id, name)
        self._save_state()
        logger.info(f"[StoryDirector] Personaje creado para {user_id}: {name}")
        return character

    def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.players.get(user_id)

    def get_player_status(self, user_id: int) -> Dict[str, Any]:
        """
        Devuelve algo seguro aunque no exista el jugador.
        """
        player = self.players.get(user_id)
        emotion = self.emotion_tracker.get_current_emotion()
        if not player:
            return {
                "found": False,
                "message": "No se encontró al jugador en la campaña.",
                "emotion": emotion,
            }
        return {
            "found": True,
            "player": player,
            "emotion": emotion,
        }

    # ------------------------------------------------------------------
    # Narrativa / campaña
    # ------------------------------------------------------------------
    def get_current_scene(self) -> Dict[str, Any]:
        scene = self.campaign_manager.get_active_scene()
        if not scene:
            return {
                "found": False,
                "message": "No hay ninguna escena activa.",
            }
        # Podríamos pasarla por el auto narrador
        narrated = self.auto_narrator.narrate_scene(scene)
        return {
            "found": True,
            "scene": scene,
            "narrated": narrated,
        }

    def get_campaign_progress(self) -> Dict[str, Any]:
        return self.campaign_manager.get_progress()

    # ------------------------------------------------------------------
    # Utilidades llamadas por handlers
    # ------------------------------------------------------------------
    def ensure_player(self, user_id: int, username: str) -> Dict[str, Any]:
        """
        Si el jugador no existe, se crea rápido con su username.
        Útil para /join.
        """
        if user_id not in self.players:
            self.create_player_character(user_id, username)
        return self.players[user_id]

