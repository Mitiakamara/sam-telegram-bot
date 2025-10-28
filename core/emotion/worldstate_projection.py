import os
import json
from datetime import datetime
from statistics import mean

from core.emotion.collective_memory import CollectiveEmotionalMemory

# ================================================================
# 🔮 EMOTIONAL WORLDSTATE PROJECTION (Fase 6.25)
# ================================================================
# Predice el clima emocional futuro del mundo según las memorias
# colectivas y el estado emocional actual. Permite ajustar eventos
# narrativos proactivos (presagios, tensiones, alivios, etc.)
# ================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")
PROJECTION_FILE = os.path.join(BASE_DIR, "worldstate_projection.json")


class EmotionalWorldstateProjection:
    def __init__(self):
        os.makedirs(BASE_DIR, exist_ok=True)
        self.collective_memory = CollectiveEmotionalMemory()
        self.state = self._load_projection()
        self.last_projection = None

    # ------------------------------------------------------------
    # 📖 Cargar / guardar predicciones
    # ------------------------------------------------------------
    def _load_projection(self):
        if not os.path.exists(PROJECTION_FILE):
            return {"history": []}
        try:
            with open(PROJECTION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"history": []}

    def _save_projection(self):
        with open(PROJECTION_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    # ------------------------------------------------------------
    # 🔮 Calcular proyección emocional
    # ------------------------------------------------------------
    def project_future_state(self):
        """
        Calcula hacia dónde se dirige el mundo emocionalmente,
        en función de los patrones de la memoria colectiva.
        """
        patterns = self.collective_memory.get_collective_summary()
        dominant = patterns.get("dominant_emotion", "neutral")
        trend = patterns.get("trend", "neutral")
        avg_cohesion = patterns.get("avg_cohesion", 0.7)

        # Lógica básica de proyección
        if trend == "positive" and avg_cohesion >= 0.7:
            projection = {
                "predicted_trend": "hopeful",
                "tone_shift": "bright",
                "event_bias": "rewards",
                "description": "El mundo parece prepararse para una fase de renovación y esperanza."
            }
        elif trend == "negative" and avg_cohesion >= 0.7:
            projection = {
                "predicted_trend": "darkening",
                "tone_shift": "melancholic",
                "event_bias": "conflict",
                "description": "Una tensión invisible recorre el mundo, presagiando sombras venideras."
            }
        elif avg_cohesion < 0.5:
            projection = {
                "predicted_trend": "chaotic",
                "tone_shift": "neutral",
                "event_bias": "instability",
                "description": "Las emociones del grupo están fragmentadas; el destino se vuelve incierto."
            }
        else:
            projection = {
                "predicted_trend": "steady",
                "tone_shift": "neutral",
                "event_bias": "balance",
                "description": "El mundo mantiene un frágil equilibrio emocional."
            }

        projection["timestamp"] = datetime.utcnow().isoformat()
        projection["source_dominant"] = dominant
        self.last_projection = projection

        self.state["history"].append(projection)
        self._save_projection()

        print(f"🔮 [WorldstateProjection] Tendencia futura: {projection['predicted_trend']} → {projection['event_bias']}")
        return projection

    # ------------------------------------------------------------
    # 🌍 Aplicar la proyección al MoodManager
    # ------------------------------------------------------------
    def apply_projection(self, mood_manager):
        """Ajusta el tono global según la proyección futura."""
        if not self.last_projection:
            self.project_future_state()

        tone_shift = self.last_projection["tone_shift"]
        if tone_shift in ["bright", "hopeful"]:
            mood_manager.adjust_intensity(+0.05)
        elif tone_shift in ["dark", "melancholic"]:
            mood_manager.adjust_intensity(-0.05)

        mood_manager.current_tone = tone_shift
        print(f"🌅 [WorldstateProjection] Tono global anticipado → {tone_shift}")
        return tone_shift

    # ------------------------------------------------------------
    # 📜 Generar resumen para narrativa
    # ------------------------------------------------------------
    def get_projection_summary(self):
        """Devuelve el texto descriptivo de la proyección actual."""
        if not self.last_projection:
            self.project_future_state()
        p = self.last_projection
        return (
            f"📜 *Proyección emocional del mundo:*\n"
            f"- Tendencia prevista: {p['predicted_trend']}\n"
            f"- Matiz tonal: {p['tone_shift']}\n"
            f"- Sesgo narrativo: {p['event_bias']}\n"
            f"- Descripción: {p['description']}"
        )
