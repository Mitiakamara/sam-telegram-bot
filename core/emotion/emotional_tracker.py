import os
import json
import uuid
from datetime import datetime
from statistics import mean

# ================================================================
# 🎭 EMOTIONAL TRACKER – Clase unificada
# ================================================================
BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")
HISTORY_FILE = os.path.join(BASE_DIR, "scene_history.json")


class EmotionalTracker:
    """
    Rastrea y resume el estado emocional del mundo y las escenas.
    Adaptado para integrarse con el Orchestrator.
    """

    # ------------------------------------------------
    # 🔧 Internos
    # ------------------------------------------------
    @staticmethod
    def _ensure_history_file():
        if not os.path.exists(BASE_DIR):
            os.makedirs(BASE_DIR, exist_ok=True)
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({"history": []}, f, indent=4, ensure_ascii=False)

    @staticmethod
    def _load_history():
        EmotionalTracker._ensure_history_file()
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"history": []}

    @staticmethod
    def _save_history(data):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ------------------------------------------------
    # 🧩 Funciones principales
    # ------------------------------------------------
    @staticmethod
    def log_scene(scene_data: dict):
        data = EmotionalTracker._load_history()
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
        data["history"].append(entry)
        EmotionalTracker._save_history(data)
        return entry

    @staticmethod
    def get_last_scene():
        data = EmotionalTracker._load_history()
        if not data["history"]:
            return None
        return data["history"][-1]

    @staticmethod
    def get_emotional_summary():
        data = EmotionalTracker._load_history()
        history = data.get("history", [])
        if not history:
            return {
                "total_scenes": 0,
                "dominant_emotion": None,
                "tone_trend": None,
                "emotion_balance": {},
            }

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
        recent_tones = [s.get("tone", "neutral") for s in history[-5:]]
        tone_trend = max(set(recent_tones), key=recent_tones.count)

        return {
            "total_scenes": len(history),
            "dominant_emotion": dominant,
            "tone_trend": tone_trend,
            "emotion_balance": emotion_balance,
        }

    @staticmethod
    def get_emotional_trend(window: int = 5):
        data = EmotionalTracker._load_history()
        history = data.get("history", [])
        if not history:
            return {}

        recent = history[-window:]
        combined = {}
        for scene in recent:
            vec = scene.get("emotion_vector", {})
            for k, v in vec.items():
                combined.setdefault(k, []).append(v)
        return {k: round(mean(vals), 3) for k, vals in combined.items()}

    @staticmethod
    def reset_history(confirm=False):
        if confirm:
            EmotionalTracker._save_history({"history": []})
            return True
        return False
