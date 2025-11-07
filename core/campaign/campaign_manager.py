import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CampaignManager:
    """
    Administra la campaña activa: nombre, capítulo y escena actual.
    Guarda en data/campaign_state.json
    """

    STATE_PATH = "data/campaign_state.json"

    def __init__(self) -> None:
        self.campaign_slug = "TheGeniesWishes"
        self.chapter = 1
        self.active_scene_id = "intro"
        self.players: Dict[int, str] = {}
        self.scenes: Dict[str, Dict[str, Any]] = self._default_scenes()

        os.makedirs("data", exist_ok=True)
        self._load_state()

    # ------------------------------------------------------------------
    def _default_scenes(self) -> Dict[str, Dict[str, Any]]:
        return {
            "intro": {
                "id": "intro",
                "title": "Oasis perdido",
                "description": (
                    "El sol del desierto cae sin piedad. Ustedes han llegado a un oasis medio abandonado, "
                    "donde se rumorea que alguien vio una lámpara antigua..."
                ),
                "objectives": [
                    "Escape del oasis",
                    "Encontrar la lámpara del genio",
                ],
            }
        }

    # ------------------------------------------------------------------
    def _load_state(self) -> None:
        if os.path.exists(self.STATE_PATH):
            try:
                with open(self.STATE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.campaign_slug = data.get("campaign_slug", self.campaign_slug)
                self.chapter = data.get("chapter", self.chapter)
                self.active_scene_id = data.get("active_scene_id", self.active_scene_id)
                self.players = data.get("players", self.players)
                # permitir que se graben escenas nuevas
                self.scenes.update(data.get("scenes", {}))
                logger.info("[CampaignManager] Estado cargado en data/campaign_state.json")
            except Exception as e:
                logger.warning(f"[CampaignManager] No se pudo cargar el estado: {e}")
        else:
            # guardar default
            self._save_state()

    def _save_state(self) -> None:
        data = self.to_dict()
        try:
            with open(self.STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("[CampaignManager] Estado guardado en data/campaign_state.json")
        except Exception as e:
            logger.warning(f"[CampaignManager] No se pudo guardar el estado: {e}")

    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaign_slug": self.campaign_slug,
            "chapter": self.chapter,
            "active_scene_id": self.active_scene_id,
            "players": self.players,
            "scenes": self.scenes,
        }

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        if not data:
            return
        self.campaign_slug = data.get("campaign_slug", self.campaign_slug)
        self.chapter = data.get("chapter", self.chapter)
        self.active_scene_id = data.get("active_scene_id", self.active_scene_id)
        self.players = data.get("players", self.players)
        self.scenes.update(data.get("scenes", {}))

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def add_player(self, user_id: int, name: str) -> None:
        self.players[str(user_id)] = name
        self._save_state()

    def get_active_scene(self) -> Optional[Dict[str, Any]]:
        return self.scenes.get(self.active_scene_id)

    def set_active_scene(self, scene_id: str) -> None:
        if scene_id in self.scenes:
            self.active_scene_id = scene_id
            self._save_state()

    def get_progress(self) -> Dict[str, Any]:
        active_scene = self.get_active_scene()
        if not active_scene:
            return {
                "campaign": self.campaign_slug,
                "chapter": self.chapter,
                "active_scene": None,
                "players": self.players,
                "completed": [],
                "pending": [],
            }

        objectives = active_scene.get("objectives", [])
        return {
            "campaign": self.campaign_slug,
            "chapter": self.chapter,
            "active_scene": active_scene.get("id"),
            "active_scene_title": active_scene.get("title"),
            "players": self.players,
            "completed": [],
            "pending": objectives,
        }
