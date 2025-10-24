import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from core.utils.logger import safe_logger

logger = safe_logger(__name__)

# ============================================================
# 💠 EMOTION LOGIC 5.3b
# ------------------------------------------------------------
# Módulo que ajusta el estado emocional global de la sesión
# según eventos narrativos y reglas de transición (mood_shift_rules)
# ============================================================


class EmotionLogic:
    def __init__(self, session_data: Dict[str, Any]):
        """
        Inicializa el gestor emocional con los datos actuales de sesión.
        """
        self.session = session_data
        self.state = self.session.get("emotional_state", {})
        self.rules = self.state.get("mood_shift_rules", {})

    # ============================================================
    # 🔍 Utilidades internas
    # ============================================================

    def _append_history(self, new_emotion: str):
        """Registra el cambio en el historial emocional."""
        history = self.state.setdefault("emotion_history", [])
        history.append({
            "emotion": new_emotion,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.state["emotion_history"] = history

    def _set_emotion(self, emotion: str, intensity: Optional[int] = None):
        """Aplica el nuevo estado emocional a la sesión."""
        self.state["current_emotion"] = emotion
        if intensity is not None:
            self.state["emotion_intensity"] = intensity
        self._append_history(emotion)
        logger.info(f"🎭 Cambio emocional → {emotion} (intensidad {self.state.get('emotion_intensity')})")

    # ============================================================
    # 🔄 Lógica principal de transición emocional
    # ============================================================

    def evaluate_trigger(self, trigger: str) -> str:
        """
        Evalúa un trigger narrativo (por ejemplo: 'victoria', 'muerte', 'traición')
        y actualiza el estado emocional según las reglas en mood_shift_rules.
        """
        current_emotion = self.state.get("current_emotion", "neutral").lower()

        # Evitar cambios si está bloqueado
        if self.state.get("emotion_lock", False):
            logger.info("🔒 Estado emocional bloqueado. No se aplican cambios.")
            return current_emotion

        # Buscar reglas coincidentes
        for rule_name, rule in self.rules.items():
            if current_emotion in rule.get("from", []):
                keywords = [k.lower() for k in rule.get("trigger_keywords", [])]
                if any(k in trigger.lower() for k in keywords):
                    new_emotion = rule.get("to", [current_emotion])[0]
                    self._set_emotion(new_emotion)
                    return new_emotion

        logger.debug(f"Sin cambio emocional para trigger '{trigger}'")
        return current_emotion

    # ============================================================
    # 🧠 Adaptaciones suaves
    # ============================================================

    def adjust_intensity(self, delta: int):
        """
        Ajusta la intensidad emocional dentro de los límites 1–5.
        """
        current = self.state.get("emotion_intensity", 3)
        new_value = max(1, min(5, current + delta))
        self.state["emotion_intensity"] = new_value
        logger.info(f"🔆 Intensidad emocional ajustada: {current} → {new_value}")

    def decay_emotion(self):
        """
        Disminuye gradualmente la intensidad (por ejemplo tras escenas de descanso).
        """
        self.adjust_intensity(-1)

    # ============================================================
    # 💾 Persistencia
    # ============================================================

    def export_state(self) -> Dict[str, Any]:
        """Devuelve el bloque actualizado del estado emocional."""
        self.session["emotional_state"] = self.state
        return self.session
