import os
import json
from statistics import mean
from typing import Dict, List, Any

from core.emotion.emotional_analytics import build_emotional_curve, compute_tone_score

# ================================================================
# 🧠 NARRATIVE MEMORY (Fase 6.14 - solo para S.A.M.)
# ================================================================
# Provee una “memoria emocional” estructurada basada en los datos
# de scene_history.json. No genera gráficos ni salida visible.
# ================================================================


class NarrativeMemory:
    def __init__(self):
        self.curve_cache: List[Dict[str, Any]] = []
        self.memory_vector: Dict[str, Any] = {}
        self.tone_cache: Dict[str, float] = {}
        self.is_loaded = False

    # ------------------------------------------------------------
    # 🧩 Cargar o actualizar la memoria narrativa
    # ------------------------------------------------------------
    def update_memory(self):
        """
        Lee los datos de emotional_analytics y construye un resumen
        interno de la evolución emocional.
        """
        curve = build_emotional_curve()
        tone_data = compute_tone_score()

        if not curve:
            self.memory_vector = {
                "scene_count": 0,
                "average_intensity": 0.0,
                "emotional_variance": 0.0,
                "emotional_trend": 0.0,
                "tone_label": "neutral",
            }
            return self.memory_vector

        intensities = [p["intensity"] for p in curve]
        avg_intensity = mean(intensities)
        variance = round(sum((x - avg_intensity) ** 2 for x in intensities) / len(intensities), 3)

        # Calcular tendencia simple (última - primera intensidad)
        trend = round(intensities[-1] - intensities[0], 3)

        self.memory_vector = {
            "scene_count": len(curve),
            "average_intensity": round(avg_intensity, 3),
            "emotional_variance": variance,
            "emotional_trend": trend,
            "tone_label": tone_data["label"],
            "tone_value": tone_data["average_tone"],
        }

        self.curve_cache = curve
        self.tone_cache = tone_data
        self.is_loaded = True

        return self.memory_vector

    # ------------------------------------------------------------
    # 🔍 Obtener resumen para uso interno del motor
    # ------------------------------------------------------------
    def get_summary(self) -> Dict[str, Any]:
        """
        Devuelve el último estado cargado de la memoria narrativa.
        Si no hay datos, ejecuta update_memory().
        """
        if not self.is_loaded:
            return self.update_memory()
        return self.memory_vector

    # ------------------------------------------------------------
    # 🧩 Provee datos discretizados para IA (por ejemplo GPT-5)
    # ------------------------------------------------------------
    def export_vector(self) -> Dict[str, Any]:
        """
        Devuelve un vector resumido para alimentar el modelo narrativo.
        Este vector puede ser usado por el generador IA de texto para
        adaptar tono, ritmo o nivel de conflicto.
        """
        summary = self.get_summary()
        export = {
            "emotion_mean": summary["average_intensity"],
            "emotion_var": summary["emotional_variance"],
            "tone_value": summary["tone_value"],
            "trend": summary["emotional_trend"],
            "tone_label": summary["tone_label"],
        }

        # Clasificación de estado emocional global
        if export["trend"] > 0.1:
            export["state"] = "ascending"
        elif export["trend"] < -0.1:
            export["state"] = "descending"
        else:
            export["state"] = "stable"

        return export


# ------------------------------------------------------------
# 🧪 DEMO LOCAL (solo para pruebas internas)
# ------------------------------------------------------------
if __name__ == "__main__":
    mem = NarrativeMemory()
    data = mem.update_memory()
    print("🧠 Memoria narrativa actualizada:")
    print(json.dumps(data, indent=4, ensure_ascii=False))

    vec = mem.export_vector()
    print("\n🔢 Vector exportado para IA:")
    print(json.dumps(vec, indent=4, ensure_ascii=False))
