import os
import json
from statistics import mean
from typing import Dict, List, Any
import math

# ================================================================
# 📊 EMOTIONAL ANALYTICS
# ================================================================
# Extrae métricas, tendencias y curvas de emoción del historial
# guardado en scene_history.json (Fase 6.11)
# ================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")
HISTORY_FILE = os.path.join(BASE_DIR, "scene_history.json")


# ------------------------------------------------
# 🔧 UTILIDADES
# ------------------------------------------------
def _load_history() -> Dict[str, Any]:
    if not os.path.exists(HISTORY_FILE):
        return {"history": []}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"history": []}


def _normalize(value: float) -> float:
    """Normaliza un valor entre 0 y 1."""
    return max(0.0, min(1.0, round(value, 3)))


# ------------------------------------------------
# 🎭 FUNCIONES PRINCIPALES
# ------------------------------------------------
def build_emotional_curve() -> List[Dict[str, Any]]:
    """
    Devuelve una lista ordenada con la evolución emocional escena por escena.
    Cada punto incluye la intensidad promedio (promedio de todos los valores del vector)
    y la emoción dominante.
    """
    data = _load_history()
    curve = []

    for idx, scene in enumerate(data.get("history", []), start=1):
        vector = scene.get("emotion_vector", {})
        if not vector:
            continue

        intensity = mean(vector.values())
        curve.append({
            "index": idx,
            "scene_id": scene.get("scene_id"),
            "title": scene.get("title"),
            "intensity": _normalize(intensity),
            "dominant_emotion": scene.get("dominant_emotion", "neutral"),
            "tone": scene.get("tone", "neutral"),
            "timestamp": scene.get("timestamp"),
        })

    return curve


def compute_tone_score() -> Dict[str, float]:
    """
    Calcula una puntuación global del tono de campaña.
    Asigna valores numéricos a cada tono y promedia.
    """
    tone_scale = {
        "dark": -1.0,
        "melancholic": -0.5,
        "neutral": 0.0,
        "hopeful": 0.5,
        "bright": 1.0
    }

    data = _load_history()
    tones = [tone_scale.get(s.get("tone", "neutral"), 0.0) for s in data.get("history", [])]
    if not tones:
        return {"average_tone": 0.0, "label": "neutral"}

    avg = mean(tones)
    if avg >= 0.4:
        label = "bright"
    elif avg >= 0.1:
        label = "hopeful"
    elif avg <= -0.4:
        label = "dark"
    elif avg <= -0.1:
        label = "melancholic"
    else:
        label = "neutral"

    return {"average_tone": round(avg, 3), "label": label}


def emotion_frequency() -> Dict[str, float]:
    """
    Retorna la frecuencia de emociones dominantes (proporcional).
    """
    data = _load_history()
    history = data.get("history", [])
    if not history:
        return {}

    freq = {}
    for s in history:
        e = s.get("dominant_emotion", "neutral")
        freq[e] = freq.get(e, 0) + 1

    total = sum(freq.values())
    return {k: round(v / total, 2) for k, v in freq.items()}


def emotion_by_scene_type() -> Dict[str, Dict[str, float]]:
    """
    Retorna el promedio emocional agrupado por tipo de escena.
    Ejemplo: {"progress": {"joy": 0.5, "fear": 0.2, ...}, "tension": {...}}
    """
    data = _load_history()
    grouped = {}

    for s in data.get("history", []):
        stype = s.get("scene_type", "unknown")
        vector = s.get("emotion_vector", {})
        if not vector:
            continue

        grouped.setdefault(stype, {}).setdefault("values", {})
        for k, v in vector.items():
            grouped[stype]["values"].setdefault(k, []).append(v)

    result = {}
    for stype, info in grouped.items():
        result[stype] = {k: round(mean(v), 3) for k, v in info["values"].items()}

    return result


def emotional_trend_score(window: int = 5) -> Dict[str, float]:
    """
    Analiza las últimas N escenas y retorna una “puntuación de cambio emocional”.
    Si el promedio de intensidad sube → tendencia positiva.
    Si baja → tendencia negativa.
    """
    curve = build_emotional_curve()
    if len(curve) < 2:
        return {"trend_score": 0.0, "direction": "neutral"}

    recent = curve[-window:]
    intensities = [p["intensity"] for p in recent]

    if len(intensities) < 2:
        return {"trend_score": 0.0, "direction": "neutral"}

    # Diferencia entre primera y última intensidad
    delta = intensities[-1] - intensities[0]
    direction = "rising" if delta > 0.05 else "falling" if delta < -0.05 else "stable"

    return {"trend_score": round(delta, 3), "direction": direction}


# ------------------------------------------------
# 🧠 DEMO LOCAL
# ------------------------------------------------
if __name__ == "__main__":
    print("📊 Ejecutando demo de Emotional Analytics...\n")

    curve = build_emotional_curve()
    tone = compute_tone_score()
    freq = emotion_frequency()
    group = emotion_by_scene_type()
    trend = emotional_trend_score()

    print(f"🌀 Curva emocional ({len(curve)} puntos):")
    for c in curve:
        print(f"  {c['index']:>2}. {c['title'][:25]:<25} → {c['dominant_emotion']} ({c['intensity']}) [{c['tone']}]")

    print("\n🎨 Tono global:", tone)
    print("📈 Frecuencia emocional:", freq)
    print("🏷️  Promedio por tipo de escena:", group)
    print("📉 Tendencia:", trend)
