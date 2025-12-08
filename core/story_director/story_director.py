import json
import os
import logging
from typing import Dict, Any, Optional

from core.campaign.campaign_manager import CampaignManager
from core.auto_narrator import AutoNarrator
from core.character_builder import CharacterBuilder
from core.story_director.scene_template_engine import generate_scene_from_template
from core.story_director.transition_engine import TransitionEngine

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
        self.transition_engine = TransitionEngine()
        self.players: Dict[int, Dict[str, Any]] = {}
        self.last_decision: Optional[Dict[str, Any]] = None

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

    # ------------------------------------------------------------------
    # Métodos requeridos por los handlers
    # ------------------------------------------------------------------
    def render_current_scene(self) -> str:
        """
        Renderiza la escena actual como texto para mostrar al usuario.
        Retorna un string formateado.
        """
        scene_data = self.get_current_scene()
        if not scene_data.get("found"):
            return f"🎭 *Escena actual*\n\n{scene_data.get('message', 'No hay escena activa.')}"
        
        narrated = scene_data.get("narrated", "")
        if narrated:
            return narrated
        
        scene = scene_data.get("scene", {})
        title = scene.get("title", "Escena")
        desc = scene.get("description", scene.get("description_adapted", ""))
        return f"🎭 *{title}*\n\n{desc}"

    def trigger_event(self, event_type: str) -> str:
        """
        Dispara un evento narrativo y genera la siguiente escena.
        Retorna un string con la descripción del evento y la nueva escena.
        """
        current_emotion = self.emotion_tracker.get_current_emotion()
        
        # Usar el transition engine para decidir la próxima escena
        next_scene_template = self.transition_engine.get_next_scene(current_emotion, event_type)
        # Remover .json si está presente
        template_name = next_scene_template.replace(".json", "")
        
        # Generar la nueva escena
        mood = {
            "mood_state": current_emotion,
            "mood_intensity": 0.7
        }
        new_scene = generate_scene_from_template(template_name, cause=event_type, mood=mood)
        
        # Actualizar la escena en el campaign manager
        scene_title = new_scene.get("title", "Nueva escena")
        self.campaign_manager.set_current_scene(scene_title)
        
        # Actualizar emoción si es necesario
        if event_type in ["combat_victory", "triumph"]:
            self.emotion_tracker.set_emotion("triumph")
        elif event_type in ["setback", "loss"]:
            self.emotion_tracker.set_emotion("setback")
        elif event_type == "rally":
            self.emotion_tracker.set_emotion("progress")
        
        self._save_state()
        
        # Renderizar la nueva escena
        return self.render_current_scene()

    def restart_campaign(self) -> None:
        """
        Reinicia la campaña desde el inicio.
        """
        self.campaign_manager.state.update({
            "campaign_name": "TheGeniesWishes",
            "chapter": 1,
            "current_scene": "Oasis perdido",
            "active_party": []
        })
        self.emotion_tracker.set_emotion("neutral")
        self._save_state()
        logger.info("[StoryDirector] Campaña reiniciada.")

    def load_campaign(self, slug: str) -> None:
        """
        Carga una campaña por su slug.
        Por ahora solo soporta campañas predefinidas.
        """
        # Por ahora, solo actualizamos el nombre
        # En el futuro, esto podría cargar desde un archivo JSON
        self.campaign_manager.state["campaign_name"] = slug
        self.campaign_manager.state["chapter"] = 1
        self.campaign_manager.state["current_scene"] = "Inicio"
        self._save_state()
        logger.info(f"[StoryDirector] Campaña '{slug}' cargada.")

    def decide_next_scene_type(self) -> str:
        """
        Decide el tipo de la próxima escena basándose en el estado actual.
        Retorna un string con el tipo de escena (ej: "progress_scene", "tension_scene").
        """
        current_emotion = self.emotion_tracker.get_current_emotion()
        # Por defecto, usar progress_scene
        next_type = self.transition_engine.get_next_scene(current_emotion, "neutral")
        # Remover .json si está presente
        return next_type.replace(".json", "")

    def generate_scene(self, template: str, cause: str = "") -> Dict[str, Any]:
        """
        Genera una nueva escena a partir de una plantilla.
        Retorna un diccionario con la escena generada.
        """
        current_emotion = self.emotion_tracker.get_current_emotion()
        mood = {
            "mood_state": current_emotion,
            "mood_intensity": 0.7
        }
        scene = generate_scene_from_template(template, cause=cause, mood=mood)
        
        # Actualizar la escena en el campaign manager
        scene_title = scene.get("title", "Nueva escena")
        self.campaign_manager.set_current_scene(scene_title)
        self._save_state()
        
        return scene

