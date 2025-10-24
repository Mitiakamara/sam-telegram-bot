import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from core.utils.logger import safe_logger

logger = safe_logger(__name__)

# ============================================================
# 💾 SESSION EMOTION EVALUATOR 5.7a
# ------------------------------------------------------------
# Carga, evalúa y transfiere el estado emocional entre sesiones.
# ============================================================


class SessionEmotionEvaluator:
    def __init__(self, base_path: str = "core/data/sessions/"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    # ============================================================
    # 📂 Utilidades de carga y guardado
    # ============================================================

    def _load_json(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error al cargar JSON {path}: {e}")
            return {}

    def _save_json(self, path: str, data: Dict[str, Any]):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Guardado emocional intersesión: {path}")
        except Exception as e:
            logger.error(f"Error al guardar JSON {path}: {e}")

    # ============================================================
    # 🧠 Heredar emoción anterior
    # ============================================================

    def inherit_emotional_state(self, previous_session_path: str, new_session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Carga la última emoción, intensidad y tono de la sesión anterior
        y los establece como punto de partida para la nueva sesión.
        """
        previous = self._load_json(previous_session_path)
        prev_state = previous.get("emotional_state", {})
        new_state = new_session_data.get("emotional_state", {})

        if not prev_state:
            logger.warning("⚠️ No se encontró estado emocional previo. Se inicia desde 'neutral'.")
            new_state.update({
                "current_emotion": "neutral",
                "emotion_intensity": 3,
                "emotion_history": [],
                "emotion_lock": False
            })
        else:
            logger.info(f"♻️ Heredando emoción desde sesión previa: {prev_state.get('session_tone', 'neutral')}")
            new_state.update({
                "current_emotion": prev_state.get("session_tone", prev_state.get("current_emotion", "neutral")),
                "emotion_intensity": int(prev_state.get("emotion_intensity", 3)),
                "emotion_history": [],
                "emotion_lock": False,
                "previous_session_ref": os.path.basename(previous_session_path)
            })

        new_session_data["emotional_state"] = new_state
        return new_session_data

    # ============================================================
    # 🧾 Exportar resumen emocional intersesión
    # ============================================================

    def generate_carryover_report(self, previous_session_path: str) -> Optional[Dict[str, Any]]:
        """
        Devuelve un resumen breve de la emoción heredada.
        """
        previous = self._load_json(previous_session_path)
        if not previous:
            return None

        emo = previous.get("emotional_state", {})
        tone = emo.get("session_tone", "neutral")
        intensity = emo.get("emotion_intensity", 3)

        report = {
            "previous_session": os.path.basename(previous_session_path),
            "tone_carried": tone,
            "intensity_start": intensity,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"🧾 Resumen emocional heredado: {tone} (intensidad {intensity})")
        return report
