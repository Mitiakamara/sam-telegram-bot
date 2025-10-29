# ================================================================
# 💓 EMOTIONAL TRACKER
# ================================================================
# Rastrea el estado emocional global de la narrativa.
# Fase 7.0 — Incluye método reset() para reinicio narrativo.
# ================================================================

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmotionalTracker:
    def __init__(self):
        self.emotion_history = []
        self.current_emotion = "neutral"
        self.intensity = 0.5  # escala 0-1
        logger.info("[EmotionalTracker] Inicializado correctamente.")

    # ------------------------------------------------------------
    # 💾 Registrar emoción
    # ------------------------------------------------------------
    def record_emotion(self, emotion: str, intensity: float):
        """
        Registra una emoción con su intensidad.
        """
        entry = {
            "emotion": emotion,
            "intensity": max(0.0, min(1.0, intensity)),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.emotion_history.append(entry)
        self.current_emotion = emotion
        self.intensity = intensity
        logger.info(f"[EmotionalTracker] Nueva emoción registrada: {emotion} ({intensity:.2f})")

    # ------------------------------------------------------------
    # 📊 Obtener tendencia emocional
    # ------------------------------------------------------------
    def get_trend(self):
        """
        Devuelve la emoción dominante y su promedio de intensidad.
        """
        if not self.emotion_history:
            return {"dominant": "neutral", "average_intensity": 0.5}

        recent = self.emotion_history[-10:]  # últimas 10 entradas
        emotions = {}
        total_intensity = 0

        for e in recent:
            emotions[e["emotion"]] = emotions.get(e["emotion"], 0) + 1
            total_intensity += e["intensity"]

        dominant = max(emotions, key=emotions.get)
        avg_intensity = total_intensity / len(recent)

        logger.debug(f"[EmotionalTracker] Tendencia actual: {dominant}, intensidad media {avg_intensity:.2f}")
        return {"dominant": dominant, "average_intensity": round(avg_intensity, 2)}

    # ------------------------------------------------------------
    # 🧘 Reinicio emocional (llamado desde Orchestrator)
    # ------------------------------------------------------------
    def reset(self):
        """
        Limpia el historial emocional y restablece el estado neutro.
        """
        self.emotion_history = []
        self.current_emotion = "neutral"
        self.intensity = 0.5
        logger.info("[EmotionalTracker] Estado emocional reiniciado.")

    # ------------------------------------------------------------
    # 🔍 Estado actual
    # ------------------------------------------------------------
    def get_current_state(self):
        return {
            "emotion": self.current_emotion,
            "intensity": self.intensity,
            "history_length": len(self.emotion_history),
        }


# ------------------------------------------------------------
# 🧪 DEMO LOCAL
# ------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    et = EmotionalTracker()
    et.record_emotion("hope", 0.7)
    et.record_emotion("fear", 0.3)
    print("Tendencia:", et.get_trend())
    et.reset()
    print("Estado tras reset:", et.get_current_state())
