import os
import json
from datetime import datetime
from core.emotion.narrative_memory import NarrativeMemory

# ================================================================
# 🧠 EMOTIONAL CONTINUITY (Fase 6.15)
# ================================================================
# Gestiona la persistencia de la memoria emocional a largo plazo,
# garantizando coherencia entre sesiones del bot.
# ================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")
STATE_FILE = os.path.join(BASE_DIR, "emotional_state.json")


class EmotionalContinuity:
    def __init__(self):
        self.memory = NarrativeMemory()
        self.state = {}
        self._ensure_storage()

    # ------------------------------------------------------------
    # 🔧 Utilidades básicas
    # ------------------------------------------------------------
    def _ensure_storage(self):
        os.makedirs(BASE_DIR, exist_ok=True)
        if not os.path.exists(STATE_FILE):
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump({"last_update": None, "state": {}}, f, indent=4, ensure_ascii=False)

    def _load_state(self):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"last_update": None, "state": {}}

    def _save_state(self):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    # ------------------------------------------------------------
    # 💾 Guardar memoria emocional global
    # ------------------------------------------------------------
    def save_emotional_state(self):
        """Persiste el estado emocional actual en disco."""
        summary = self.memory.get_summary()
        export = self.memory.export_vector()
        self.state = {
            "last_update": datetime.utcnow().isoformat(),
            "summary": summary,
            "vector": export,
        }
        self._save_state()
        return self.state

    # ------------------------------------------------------------
    # 🔄 Cargar memoria previa al iniciar sesión
    # ------------------------------------------------------------
    def load_previous_state(self):
        """Restaura el estado emocional previo, si existe."""
        data = self._load_state()
        self.state = data
        if data.get("vector"):
            print(f"🧠 [EmotionalContinuity] Estado cargado — tono {data['vector'].get('tone_label')}")
        else:
            print("🧠 [EmotionalContinuity] Sin estado previo encontrado.")
        return data

    # ------------------------------------------------------------
    # 🧩 Obtener vector resumido para inicializar MoodManager
    # ------------------------------------------------------------
    def get_emotional_baseline(self):
        """Devuelve valores útiles para inicializar tono y ritmo."""
        vector = self.state.get("vector", {})
        return {
            "tone": vector.get("tone_label", "neutral"),
            "trend": vector.get("trend", 0.0),
            "intensity": vector.get("emotion_mean", 0.0),
            "state": vector.get("state", "stable"),
        }


# ------------------------------------------------------------
# 🧪 DEMO LOCAL
# ------------------------------------------------------------
if __name__ == "__main__":
    continuity = EmotionalContinuity()
    continuity.memory.update_memory()
    continuity.save_emotional_state()

    print("\n💾 Estado emocional guardado:")
    print(json.dumps(continuity.state, indent=4, ensure_ascii=False))

    print("\n🔄 Cargando estado previo...")
    data = continuity.load_previous_state()
    print(json.dumps(data, indent=4, ensure_ascii=False))
