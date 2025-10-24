import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from core.utils.logger import safe_logger
from core.tone_adapter import apply_tone  # ← integración de tono narrativo adaptativo

logger = safe_logger(__name__)


class SceneManager:
    """
    Administra la carga, guardado y transición de escenas en una sesión activa.
    Compatible con estructura JSON definida en Fase 5.0 (GameSession / SceneState).
    """

    def __init__(self, base_path: str = "core/data/sessions/"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        logger.info(f"SceneManager inicializado en ruta: {self.base_path}")

    # ============================================================
    # Utilidades internas
    # ============================================================
    def _session_file(self, session_id: str) -> str:
        """Ruta completa del archivo de sesión."""
        return os.path.join(self.base_path, f"session_{session_id}.json")

    def _load_json(self, path: str) -> Dict[str, Any]:
        """Carga un archivo JSON en memoria."""
        if not os.path.exists(path):
            logger.warning(f"No existe el archivo: {path}")
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON {path}: {e}")
            return {}

    def _save_json(self, path: str, data: Dict[str, Any]):
        """Guarda un diccionario como JSON."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Guardado exitoso: {path}")
        except Exception as e:
            logger.exception(f"Error al guardar {path}: {e}")

    # ============================================================
    # Métodos principales
    # ============================================================

    def create_session(self, campaign_id: str, party_id: str, dm_mode: str = "auto") -> Dict[str, Any]:
        """
        Crea una nueva sesión basada en la plantilla game_session.json.
        """
        session_id = str(uuid.uuid4())
        template_path = "core/models/GameSession.json"
        data = self._load_json(template_path)

        if not data:
            logger.warning("Plantilla de sesión vacía. Se inicializa con estructura mínima.")
            data = {
                "session_id": session_id,
                "campaign_id": campaign_id,
                "party_id": party_id,
                "dm_mode": dm_mode,
                "scene_history": [],
                "story_flags": {},
                "party_state": {"members": [], "inventory": [], "gold": 0},
                "encounter_log": [],
                "emotional_state": {
                    "current_emotion": "neutral",
                    "emotion_intensity": 3,
                    "emotion_history": [],
                    "emotion_lock": False
                }
            }

        data.update({
            "session_id": session_id,
            "campaign_id": campaign_id,
            "party_id": party_id,
            "dm_mode": dm_mode,
            "timestamp": datetime.utcnow().isoformat()
        })

        self._save_json(self._session_file(session_id), data)
        logger.info(f"Sesión creada con ID: {session_id}")
        return data

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Carga una sesión existente desde disco."""
        path = self._session_file(session_id)
        session = self._load_json(path)
        if session:
            logger.info(f"Sesión {session_id} cargada correctamente.")
        else:
            logger.warning(f"No se pudo cargar la sesión {session_id}.")
        return session or None

    def save_progress(self, session_data: Dict[str, Any]):
        """Guarda los cambios actuales en el archivo correspondiente."""
        session_id = session_data.get("session_id")
        if not session_id:
            logger.error("No se puede guardar: session_id ausente.")
            return
        self._save_json(self._session_file(session_id), session_data)

    def autosave(self, session_data: Dict[str, Any]):
        """Crea una copia de seguridad automática del estado actual."""
        try:
            sid = session_data.get("session_id", "unknown")
            auto_path = os.path.join(self.base_path, f"autosave_{sid}.json")
            session_data["timestamp"] = datetime.utcnow().isoformat()
            self._save_json(auto_path, session_data)
            logger.info(f"Autosave completado para sesión {sid}")
        except Exception as e:
            logger.exception(f"Error en autosave: {e}")

    def load_scene(self, scene_id: str) -> Dict[str, Any]:
        """Carga la plantilla de escena y aplica tono adaptativo."""
        template_path = "core/models/SceneState.json"
        data = self._load_json(template_path)
        if not data:
            logger.warning("Plantilla de escena vacía. Se genera estructura mínima.")
            data = {
                "scene_id": scene_id,
                "title": "",
                "description": "",
                "description_adapted": "",
                "scene_type": "neutral",
                "emotion_intensity": 3,
                "status": "active",
                "objectives": [],
                "npcs": [],
                "environment": {},
                "available_actions": [],
                "transitions": [],
                "random_events": []
            }

        data["scene_id"] = scene_id

        # Aplicar tono narrativo adaptativo si hay descripción
        base_desc = data.get("description", "")
        if base_desc:
            data["description_adapted"] = apply_tone(
                scene_type=data.get("scene_type", "neutral"),
                text=base_desc,
                intensity=int(data.get("emotion_intensity", 3))
            )
        return data

    def trigger_event(self, scene: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Ejecuta un evento aleatorio o programado en la escena."""
        found = next((e for e in scene.get("random_events", []) if e["id"] == event_id), None)
        if not found:
            logger.warning(f"Evento {event_id} no encontrado en escena {scene.get('scene_id')}")
            return scene
        logger.info(f"Evento disparado [{event_id}]: {found.get('event')}")
        if found.get("description"):
            found["description_adapted"] = apply_tone(
                scene_type=scene.get("scene_type", "neutral"),
                text=found["description"],
                intensity=scene.get("emotion_intensity", 3)
            )
        return scene

    def transition_scene(self, session_data: Dict[str, Any], trigger: str) -> Optional[str]:
        """Evalúa las transiciones y cambia a la siguiente escena."""
        current_id = session_data.get("current_scene_id")
        scene = self.load_scene(current_id)
        match = next((t for t in scene.get("transitions", []) if t["trigger"] == trigger), None)

        if not match:
            logger.warning(f"Sin transición válida para trigger '{trigger}' en escena {current_id}")
            return None

        next_scene = match["next_scene"]
        session_data["scene_history"].append(current_id)
        session_data["current_scene_id"] = next_scene

        # Actualizar estado emocional global
        emo_state = session_data.get("emotional_state", {})
        emo_state["current_emotion"] = scene.get("scene_type", "neutral")
        emo_state["emotion_intensity"] = scene.get("emotion_intensity", 3)
        emo_state.setdefault("emotion_history", []).append({
            "scene_id": current_id,
            "emotion": emo_state["current_emotion"],
            "timestamp": datetime.utcnow().isoformat()
        })
        session_data["emotional_state"] = emo_state

        self.save_progress(session_data)
        logger.info(f"Transición: {current_id} → {next_scene}")
        return next_scene
