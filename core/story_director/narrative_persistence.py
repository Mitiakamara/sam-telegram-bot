import os
import json
from datetime import datetime
from core.emotion.emotional_continuity import EmotionalContinuity
from core.emotion.collective_memory import CollectiveEmotionalMemory
from core.emotion.worldstate_projection import EmotionalWorldstateProjection
from core.renderer.narrator_persona import AdaptiveNarratorPersona
from core.renderer.style_evolution import NarrativeStyleEvolution

# ================================================================
# 🔁 NARRATIVE PERSISTENCE & CONTINUATION (Fase 6.30)
# ================================================================
# Restaura el estado emocional, la proyección del mundo y el estilo
# narrativo, generando una reintroducción coherente con la sesión anterior.
# ================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")
SESSION_FILE = os.path.join(BASE_DIR, "session_state.json")


class NarrativePersistence:
    def __init__(self, mood_manager):
        self.mood_manager = mood_manager
        self.continuity = EmotionalContinuity()
        self.collective_memory = CollectiveEmotionalMemory()
        self.projection = EmotionalWorldstateProjection()
        self.persona = None
        self.style_engine = None
        self.state = self._load_last_session()

    # ------------------------------------------------------------
    # 💾 Cargar última sesión
    # ------------------------------------------------------------
    def _load_last_session(self):
        if not os.path.exists(SESSION_FILE):
            return {"timestamp": None, "tone": "neutral", "blend": None, "projection": None}
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"timestamp": None, "tone": "neutral", "blend": None, "projection": None}

    # ------------------------------------------------------------
    # 🧠 Restaurar estado global
    # ------------------------------------------------------------
    def restore_last_state(self):
        """Recupera el tono, blend y proyección del mundo desde la última sesión."""
        baseline = self.continuity.get_emotional_baseline()
        tone = baseline.get("tone", "neutral")
        blend = baseline.get("trend", "stable")

        proj = self.projection.project_future_state()
        coll = self.collective_memory.get_collective_summary()

        self.mood_manager.current_tone = tone
        self.mood_manager.last_blend = {"label": blend, "description": "restaurado de sesión anterior"}

        self.state = {
            "timestamp": datetime.utcnow().isoformat(),
            "tone": tone,
            "blend": blend,
            "projection": proj.get("predicted_trend", "neutral"),
            "collective_trend": coll.get("trend", "neutral"),
        }

        print(f"🔁 [NarrativePersistence] Estado restaurado → tono {tone}, tendencia {blend}")
        self._save_session_state()
        return self.state

    # ------------------------------------------------------------
    # ✍️ Generar introducción narrativa de continuación
    # ------------------------------------------------------------
    def generate_continuation_intro(self):
        """Crea una introducción narrativa adaptada al estado restaurado."""
        self.persona = AdaptiveNarratorPersona()
        self.style_engine = NarrativeStyleEvolution(self.mood_manager)

        intro = self.persona.narrate_intro()
        styled_intro = self.style_engine.stylize_text(intro)

        summary = (
            f"📜 *Reanudando la campaña...*\n"
            f"Última tendencia emocional: `{self.state['blend']}`\n"
            f"Proyección del mundo: `{self.state['projection']}`\n\n"
            f"{styled_intro}"
        )

        print(f"🪶 [NarrativePersistence] Sesión reanudada con tono '{self.state['tone']}' y proyección '{self.state['projection']}'.")
        return summary

    # ------------------------------------------------------------
    # 💾 Guardar sesión actual
    # ------------------------------------------------------------
    def _save_session_state(self):
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)
        print("💾 [NarrativePersistence] Sesión guardada.")

    def save_current_state(self):
        """Guarda manualmente el estado actual del mundo."""
        self.state.update({
            "timestamp": datetime.utcnow().isoformat(),
            "tone": self.mood_manager.current_tone,
            "blend": self.mood_manager.last_blend,
        })
        self._save_session_state()
