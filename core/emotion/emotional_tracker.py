import os
import json
import uuid
from datetime import datetime
from statistics import mean

# ================================================================
# 🎭 EMOTIONAL TRACKER
# ================================================================
# Registra el historial emocional de las escenas y provee métricas
# agregadas que el Mood Manager y Story Director pueden consultar.
# ================================================================

# Ruta base (ajustable según tu repo)
BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")
HISTORY_FILE = os.path.join(BASE_DIR, "scene_history.json")


# ------------------------------------------------
# 🔧 UTILIDADES INTERNAS
# ------------------------------------------------
def _ensure_history_file():
    """Crea el archivo scene_history.json si no existe."""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"history": []}, f, indent=4, ensure_ascii=False)


def _load_history():
    _ensure_history_file()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"history": []}


def _save_history(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ------------------------------------------------
# 🧩 FUNCIONES PRINCIPALES
# ------------------------------------------------
def log_scene(scene_data: dict):
    """
    Registra una nueva escena en el historial emocional.
    scene_data debe contener al menos:
        - title
        - scene_type
        - emotion_vector (dict con emociones)
        - dominant_emotion
        - tone
        - summary
        - outcome
    """
    history_data = _load_history()
    entry = {
        "scene_id": scene_data.get("scene_id", str(uuid.uuid4())),
        "title": scene_data.get("title", "Escena sin título"),
        "timestamp": datetime.utcnow().isoformat(),
        "scene_type": scene_data.get("scene_type", "unknown"),
        "emotion_vector": scene_data.get("emotion_vector", {}),
        "dominant_emotion": scene_data.get("dominant_emotion", "neutral"),
        "tone": scene_data.get("tone", "neutral"),
        "summary": scene_data.get("summary", ""),
        "outcome": scene_data.get("outcome", "mixed"),
    }

    history_data["history"].append(entry)
    _save_history(history_data)
    return entry


def get_last_scene():
    """Devuelve la última escena registrada."""
    data = _load_history()
    if not data["history"]:
        return None
    return data["history"][-1]


def get_emotional_summary():
    """
    Devuelve un resumen general del estado emocional del historial:
      - emoción dominante promedio
      - frecuencia de emociones
      - tendencia de tono
    """
    data = _load_history()
    history = data.get("history", [])
    if not history:
        return {
            "total_scenes": 0,
            "dominant_emotion": None,
            "tone_trend": None,
            "emotion_balance": {},
        }

    # Calcular frecuencia de emociones dominantes
    emotion_counts = {}
    tone_counts = {}
    for scene in history:
        e = scene.get("dominant_emotion", "neutral")
        t = scene.get("tone", "neutral")
        emotion_counts[e] = emotion_counts.get(e, 0) + 1
        tone_counts[t] = tone_counts.get(t, 0) + 1

    total = sum(emotion_counts.values())
    emotion_balance = {k: round(v / total, 2) for k, v in emotion_counts.items()}
    dominant = max(emotion_counts, key=emotion_counts.get)

    # Determinar tendencia de tono (últimas 5 escenas)
    recent_tones = [s.get("tone", "neutral") for s in history[-5:]]
    tone_trend = max(set(recent_tones), key=recent_tones.count)

    return {
        "total_scenes": len(history),
        "dominant_emotion": dominant,
        "tone_trend": tone_trend,
        "emotion_balance": emotion_balance,
    }


def get_emotional_trend(window: int = 5):
    """
    Devuelve las emociones promedio de las últimas N escenas (ventana).
    Ejemplo: get_emotional_trend(3) → promedio de los últimos 3 emotion_vectors
    """
    data = _load_history()
    history = data.get("history", [])
    if not history:
        return {}

    recent = history[-window:]
    combined = {}

    for scene in recent:
        vec = scene.get("emotion_vector", {})
        for k, v in vec.items():
            combined.setdefault(k, []).append(v)

    averaged = {k: round(mean(vals), 3) for k, vals in combined.items()}
    return averaged


def reset_history(confirm=False):
    """
    Borra el historial de escenas si confirm=True.
    Útil para reiniciar una campaña.
    """
    if confirm:
        _save_history({"history": []})
        return True
    return False


# ------------------------------------------------
# 🧠 DEMO (solo si se ejecuta directamente)
# ------------------------------------------------
if __name__ == "__main__":
    print("🔧 Inicializando Emotional Tracker Demo...")
    reset_history(confirm=True)

    log_scene({
        "title": "Encuentro en la taberna",
        "scene_type": "progress",
        "emotion_vector": {"joy": 0.6, "fear": 0.1, "anger": 0.0, "sadness": 0.1, "surprise": 0.2},
        "dominant_emotion": "joy",
        "tone": "hopeful",
        "summary": "El grupo conoce a un misterioso mago que les ofrece una misión.",
        "outcome": "success",
    })

    log_scene({
        "title": "Emboscada en el bosque",
        "scene_type": "tension",
        "emotion_vector": {"joy": 0.1, "fear": 0.7, "anger": 0.2, "sadness": 0.1, "surprise": 0.3},
        "dominant_emotion": "fear",
        "tone": "dark",
        "summary": "Los aventureros son atacados por bandidos durante la noche.",
        "outcome": "mixed",
    })

    print("\n📊 Resumen emocional:")
    print(get_emotional_summary())

    print("\n📈 Tendencia última ventana:")
    print(get_emotional_trend(2))
