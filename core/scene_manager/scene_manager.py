import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from core.utils.logger import safe_logger
from core.tone_adapter import apply_tone
from core.emotion.emotion_logic import EmotionLogic  # 🎭 integración emocional

logger = safe_logger(__name__)


class SceneManager:
    """
    Administra la carga, guardado y transición de escenas en una sesión activa.
    Integra tono narrativo adaptativo (Fase 5.2) y persistencia emocional (Fase 5.3).
    """

    def __init__(self, base_path: str = "core/data/sessions/"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        logger.info(f"SceneManager inicializado en ruta: {self.base_path}")

    # ============================================================
    # Utilidades internas
    # ============================================================
    def _session_file(self, session_id: str) -> str:
        return os.path.join(self.base_path, f"session_{session_id}.json")

    def _load_json(self, path: str) -> Dict[str, Any]:
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
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Guardado exitoso: {path}")
        except Exception as e:
            logger.exception(f"Error al guardar {path}: {e}")

    # ============================================================
    # Sesiones
    # ============================================================

    def create_session(self, campaign_id: str, party_id: str, dm_mode: str = "auto") -> Dict[str, Any]:
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
        path = self._session_file(session_id)
        session = self._load_json(path)
        if session:
            logger.info(f"Sesión {session_id} cargada correctamente.")
        else:
            logger.warning(f"No se pudo cargar la sesión {session_id}.")
        return session or None

    def save_progress(self, session_data: Dict[str, Any]):
        session_id = session_data.get("session_id")
        if not session_id:
            logger.error("No se puede guardar: session_id ausente.")
            return
        self._save_json(self._session_file(session_id), session_data)

    # ============================================================
    # Escenas
    # ============================================================

    def load_scene(self, scene_id: str) -> Dict[str, Any]:
        template_path = "core/models/SceneState.json"
        data = self._load_json(template_path)
        if not data:
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
        base_desc = data.get("description", "")
        if base_desc:
            data["description_adapted"] = apply_tone(
                data.get("scene_type", "neutral"),
                base_desc,
                int(data.get("emotion_intensity", 3))
            )
        return data

    def trigger_event(self, session_data: Dict[str, Any], scene: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Ejecuta un evento aleatorio y actualiza emoción según el resultado."""
        found = next((e for e in scene.get("random_events", []) if e["id"] == event_id), None)
        if not found:
            logger.warning(f"Evento {event_id} no encontrado en escena {scene.get('scene_id')}")
            return scene

        logger.info(f"🎬 Evento disparado [{event_id}]: {found.get('event')}")
        event_text = found.get("description", "")
        if event_text:
            found["description_adapted"] = apply_tone(
                scene.get("scene_type", "neutral"),
                event_text,
                int(scene.get("emotion_intensity", 3))
            )

        # 🧠 Evaluar el evento como trigger emocional
        emotion_engine = EmotionLogic(session_data)
        emotion_engine.evaluate_trigger(found.get("event", ""))
        session_data = emotion_engine.export_state()

        self.save_progress(session_data)
        return scene

    def transition_scene(self, session_data: Dict[str, Any], trigger: str) -> Optional[str]:
        """Cambia a la siguiente escena y ajusta el estado emocional automáticamente."""
        current_id = session_data.get("current_scene_id")
        scene = self.load_scene(current_id)
        match = next((t for t in scene.get("transitions", []) if t["trigger"] == trigger), None)

        if not match:
            logger.warning(f"Sin transición válida para trigger '{trigger}' en escena {current_id}")
            return None

        next_scene_id = match["next_scene"]
        session_data["scene_history"].append(current_id)
        session_data["current_scene_id"] = next_scene_id

        # Cargar próxima escena
        next_scene = self.load_scene(next_scene_id)

        # 🧠 Evaluar transición como trigger emocional
        emotion_engine = EmotionLogic(session_data)
        emotion_engine.evaluate_trigger(trigger)
        session_data = emotion_engine.export_state()

        # Aplicar tono adaptativo a la descripción
        next_scene["description_adapted"] = apply_tone(
            next_scene.get("scene_type", "neutral"),
            next_scene.get("description", ""),
            int(next_scene.get("emotion_intensity", 3))
        )

        self.save_progress(session_data)
        logger.info(f"Transición emocional: {current_id} → {next_scene_id}")
        return next_scene_id
