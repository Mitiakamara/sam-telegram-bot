import random
from datetime import datetime
from typing import Dict, Any
from core.utils.logger import safe_logger

logger = safe_logger(__name__)

# ============================================================
# 💓 INTENSITY ADAPTER 5.4a
# ------------------------------------------------------------
# Ajusta automáticamente la intensidad emocional (1–5)
# según tipo de escena, ritmo narrativo y frecuencia de eventos.
# ============================================================


class IntensityAdapter:
    def __init__(self, session_data: Dict[str, Any]):
        self.session = session_data
        self.state = self.session.get("emotional_state", {})
        self.history = self.state.get("emotion_history", [])

    # ============================================================
    # 🔢 Escala base según tipo de escena
    # ============================================================
    BASE_LEVELS = {
        "exploration": 2,
        "dialogue": 2,
        "rest": 1,
        "revelation": 3,
        "combat": 4,
        "victory": 5,
        "defeat": 4,
        "comic_relief": 2,
        "horror": 4
    }

    # ============================================================
    # 🔄 Ajuste dinámico
    # ============================================================

    def adapt_intensity(self, scene_type: str, recent_events: int = 0) -> int:
        """
        Calcula una nueva intensidad emocional basada en:
        - tipo de escena
        - cantidad de eventos recientes
        """
        base = self.BASE_LEVELS.get(scene_type, 3)
        delta = 0

        # Más eventos recientes = aumento emocional
        if recent_events >= 3:
            delta += 1
        elif recent_events == 0 and base > 1:
            delta -= 1

        # Aleatoriedad ligera para evitar monotonía
        delta += random.choice([-1, 0, 0, 1])

        new_intensity = max(1, min(5, base + delta))
        logger.info(f"🎚️ Ajuste emocional: base {base} → final {new_intensity} ({scene_type})")
        return new_intensity

    # ============================================================
    # 🧠 Aplicar y registrar
    # ============================================================

    def update_session_intensity(self, scene_type: str, recent_events: int = 0):
        """
        Aplica el nuevo valor de intensidad a la sesión
        y lo guarda en el historial emocional.
        """
        new_intensity = self.adapt_intensity(scene_type, recent_events)
        self.state["emotion_intensity"] = new_intensity
        self.state.setdefault("emotion_history", []).append({
            "emotion": self.state.get("current_emotion", "neutral"),
            "intensity": new_intensity,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.session["emotional_state"] = self.state
        return self.session
