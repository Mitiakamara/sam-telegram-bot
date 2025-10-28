import os
import json
from datetime import datetime
from statistics import mean

# ================================================================
# 🧠 COLLECTIVE EMOTIONAL MEMORY (Fase 6.24)
# ================================================================
# Guarda y analiza la evolución emocional del grupo a lo largo de
# la campaña. Genera un "ADN emocional colectivo" persistente.
# ================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")
MEMORY_FILE = os.path.join(BASE_DIR, "collective_emotional_memory.json")


class CollectiveEmotionalMemory:
    def __init__(self):
        os.makedirs(BASE_DIR, exist_ok=True)
        self.memory = self._load_memory()
        self.last_update = None

    # ------------------------------------------------------------
    # 🔧 Utilidades internas
    # ------------------------------------------------------------
    def _load_memory(self):
        if not os.path.exists(MEMORY_FILE):
            return {"history": [], "patterns": {}}
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"history": [], "patterns": {}}

    def _save_memory(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4, ensure_ascii=False)

    # ------------------------------------------------------------
    # 🧩 Registrar estado grupal
    # ------------------------------------------------------------
    def record_group_state(self, group_result: dict):
        """Guarda un snapshot del estado emocional colectivo."""
        if not group_result:
            return

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "dominant_emotion": group_result.get("dominant_emotion", "neutral"),
            "cohesion": group_result.get("cohesion", 1.0),
            "avg_strength": group_result.get("avg_strength", 0.0),
            "group_state": group_result.get("group_state", "stable"),
        }

        self.memory["history"].append(entry)
        self._update_patterns()
        self._save_memory()

        print(f"🧠 [CollectiveMemory] Estado grupal registrado ({entry['dominant_emotion']} / {entry['group_state']})")

    # ------------------------------------------------------------
    # 🔬 Analizar patrones a largo plazo
    # ------------------------------------------------------------
    def _update_patterns(self):
        """Calcula promedios de cohesión y tendencias emocionales."""
        history = self.memory["history"]
        if not history:
            return

        emotions = [h["dominant_emotion"] for h in history]
        cohesion = [h["cohesion"] for h in history]

        freq = {}
        for e in emotions:
            freq[e] = freq.get(e, 0) + 1

        total = sum(freq.values())
        distribution = {k: round(v / total, 2) for k, v in freq.items()}

        avg_cohesion = round(mean(cohesion), 2)
        dominant = max(freq, key=freq.get)
        trend = "positive" if dominant in ["joy", "hopeful", "surprise"] else "negative" if dominant in ["fear", "anger", "sadness"] else "neutral"

        self.memory["patterns"] = {
            "dominant_emotion": dominant,
            "emotion_distribution": distribution,
            "avg_cohesion": avg_cohesion,
            "trend": trend,
            "last_update": datetime.utcnow().isoformat(),
        }
        self.last_update = self.memory["patterns"]["last_update"]

    # ------------------------------------------------------------
    # 📊 Obtener resumen colectivo
    # ------------------------------------------------------------
    def get_collective_summary(self):
        """Devuelve la firma emocional colectiva actual."""
        if not self.memory["patterns"]:
            self._update_patterns()
        return self.memory["patterns"]

    # ------------------------------------------------------------
    # 💫 Aplicar memoria colectiva al MoodManager
    # ------------------------------------------------------------
    def apply_to_mood(self, mood_manager):
        """Ajusta el tono global según la tendencia emocional colectiva."""
        patterns = self.get_collective_summary()
        trend = patterns.get("trend", "neutral")

        if trend == "positive":
            tone = "bright"
            delta = +0.1
        elif trend == "negative":
            tone = "melancholic"
            delta = -0.1
        else:
            tone = "neutral"
            delta = 0.0

        mood_manager.current_tone = tone
        mood_manager.adjust_intensity(delta)

        print(f"🎨 [CollectiveMemory] Tono global ajustado por memoria colectiva → {tone}")
        return tone
