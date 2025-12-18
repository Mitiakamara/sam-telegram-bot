"""
Adventure Loader
Loads pre-existing D&D campaigns from JSON files and initializes game state.
"""
import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class AdventureLoader:
    """
    Loads and parses adventure JSON files.
    Supports the adventure format used in demo_mine_v1.json
    """

    def __init__(self, adventures_dir: str = "adventures"):
        self.adventures_dir = adventures_dir
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Creates adventures directory if it doesn't exist."""
        os.makedirs(self.adventures_dir, exist_ok=True)

    def list_available_adventures(self) -> List[str]:
        """
        Returns list of available adventure slugs (filenames without .json).
        """
        adventures = []
        if not os.path.exists(self.adventures_dir):
            return adventures

        for file in os.listdir(self.adventures_dir):
            if file.endswith(".json"):
                slug = file.replace(".json", "")
                adventures.append(slug)
        
        return adventures

    def load_adventure(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Loads an adventure by slug.
        Returns the adventure data dict or None if not found.
        """
        # Try different filename formats
        possible_names = [
            f"{slug}.json",
            f"{slug}_v1.json",
            f"{slug}_v2.json",
            f"demo_{slug}.json",
        ]

        for filename in possible_names:
            path = os.path.join(self.adventures_dir, filename)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        adventure_data = json.load(f)
                        logger.info(f"[AdventureLoader] Aventura '{slug}' cargada desde {filename}")
                        return adventure_data
                except Exception as e:
                    logger.error(f"[AdventureLoader] Error cargando {filename}: {e}")
                    return None

        logger.warning(f"[AdventureLoader] Aventura '{slug}' no encontrada en {self.adventures_dir}")
        return None

    def validate_adventure(self, adventure_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validates adventure data structure.
        Returns (is_valid, error_message)
        """
        required_keys = ["title", "scenes"]
        
        for key in required_keys:
            if key not in adventure_data:
                return False, f"Falta la clave requerida: {key}"
        
        # Validate scenes
        scenes = adventure_data.get("scenes", [])
        if not isinstance(scenes, list):
            return False, "scenes debe ser una lista"
        
        if len(scenes) == 0:
            return False, "La aventura debe tener al menos una escena"
        
        # Validate each scene has required fields
        for i, scene in enumerate(scenes):
            if "scene_id" not in scene:
                return False, f"Escena {i} no tiene scene_id"
            if "title" not in scene:
                return False, f"Escena {i} no tiene title"
        
        return True, ""

    def get_initial_scene(self, adventure_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Returns the first scene of the adventure (usually the starting scene).
        """
        scenes = adventure_data.get("scenes", [])
        if scenes:
            return scenes[0]
        return None

    def find_scene_by_id(self, adventure_data: Dict[str, Any], scene_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds a scene by its scene_id.
        """
        scenes = adventure_data.get("scenes", [])
        for scene in scenes:
            if scene.get("scene_id") == scene_id:
                return scene
        return None

    def get_adventure_info(self, adventure_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts summary information from adventure data.
        """
        return {
            "title": adventure_data.get("title", "Aventura sin título"),
            "description": adventure_data.get("description", ""),
            "session_id": adventure_data.get("session_id", ""),
            "total_scenes": len(adventure_data.get("scenes", [])),
            "party_info": adventure_data.get("party", {}),
        }
