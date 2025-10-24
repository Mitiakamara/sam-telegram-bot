import math
from datetime import datetime
from typing import Dict, Any, List
from core.utils.logger import safe_logger

logger = safe_logger(__name__)

# ============================================================
# 🎢 DRAMATIC CURVE 5.5a
# ------------------------------------------------------------
# Calcula la curva emocional global de una sesión combinando
# emoción + intensidad + tiempo.
# ============================================================


class DramaticCurve:
    def __init__(self, session_data: Dict[str, Any]):
        self.session = session_data
        self.state = self.session.get("emotional_state", {})
        self.history = self.state.get("emotion_history", [])
        self.curve_points: List[Dict[str, Any]] = []

    # ============================================================
    # 🔢 Asignar valor numérico a cada emoción
    # ============================================================
    EMOTION_WEIGHTS = {
        "neutral": 0,
        "hope": +2,
        "epic": +3,
        "comic": +1,
        "melancholy": -2,
        "fear": -3,
        "tension": -1,
        "horror": -3
    }

    # ============================================================
    # 📈 Generar curva dramática
    # ============================================================

    def calculate_curve(self):
        """
        Genera puntos (time, value) representando la evolución emocional.
        Combina el peso de la emoción y la intensidad (1–5).
        """
        if not self.history:
            logger.warning("No hay historial emocional suficiente para generar la curva.")
            return []

        curve = []
        for i, item in enumerate(self.history):
            emotion = item.get("emotion", "neutral")
            intensity = int(item.get("intensity", self.state.get("emotion_intensity", 3)))
            weight = self.EMOTION_WEIGHTS.get(emotion, 0)

            # Valor dramático: emoción + curva de intensidad normalizada
            value = weight + (intensity - 3) * 0.8
            curve.append({
                "index": i,
                "emotion": emotion,
                "intensity": intensity,
                "value": round(value, 2),
                "timestamp": item.get("timestamp", datetime.utcnow().isoformat())
            })

        self.curve_points = curve
        logger.info(f"🎢 Curva dramática generada con {len(curve)} puntos.")
        return curve

    # ============================================================
    # 🎭 Análisis de tono global
    # ============================================================

    def summarize_tone(self) -> str:
        """
        Analiza la curva para determinar el tono narrativo global de la sesión.
        """
        if not self.curve_points:
            self.calculate_curve()

        values = [p["value"] for p in self.curve_points]
        if not values:
            return "neutral"

        avg_value = sum(values) / len(values)

        # Determinar tono general
        if avg_value >= 2:
            tone = "heroico"
        elif avg_value >= 0.5:
            tone = "esperanzador"
        elif avg_value <= -2:
            tone = "trágico"
        elif avg_value < -0.5:
            tone = "tenso u oscuro"
        else:
            tone = "neutral"

        logger.info(f"🎬 Tono narrativo global: {tone} (valor medio {avg_value:.2f})")
        return tone

    # ============================================================
    # 📊 Exportar datos
    # ============================================================

    def export_curve_summary(self) -> Dict[str, Any]:
        """
        Devuelve un resumen con la curva completa y el tono global.
        """
        tone = self.summarize_tone()
        return {
            "curve_points": self.curve_points,
            "tone_summary": tone,
            "average_intensity": sum(p["intensity"] for p in self.curve_points) / len(self.curve_points),
            "created": datetime.utcnow().isoformat()
        }

