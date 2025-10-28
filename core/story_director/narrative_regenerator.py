from datetime import datetime
from core.emotion.emotional_continuity import EmotionalContinuity
from core.story_director.story_director import StoryDirector
from core.emotion.mood_manager import MoodManager
from core.emotion.tone_adapter import ToneAdapter
from core.renderer.renderer import Renderer

# ================================================================
# 🔁 NARRATIVE REGENERATOR (Fase 6.16)
# ================================================================
# Usa la memoria emocional persistente para generar una introducción
# coherente cuando S.A.M. reinicia una sesión.
# ================================================================

class NarrativeRegenerator:
    def __init__(self):
        self.continuity = EmotionalContinuity()
        self.story_director = StoryDirector()
        self.mood_manager = MoodManager()
        self.tone_adapter = ToneAdapter()
        self.renderer = Renderer()
        self.last_intro = None

    # ------------------------------------------------------------
    # 🧠 Reconstruir el contexto narrativo
    # ------------------------------------------------------------
    def reconstruct_narrative(self):
        """Restaura el tono emocional y genera una introducción adaptada."""
        data = self.continuity.load_previous_state()
        baseline = self.continuity.get_emotional_baseline()

        tone = baseline["tone"]
        trend = baseline["trend"]
        state = baseline["state"]

        # Aplicar tono inicial
        self.mood_manager.current_tone = tone

        # Determinar tipo de escena inicial
        if state == "ascending":
            next_type = "tension"
        elif state == "descending":
            next_type = "triumph"
        else:
            next_type = self.story_director.decide_next_scene_type()

        # Generar texto de transición
        intro = self._generate_intro_text(tone, trend, state, next_type)
        self.last_intro = intro

        print("\n🌄 [NarrativeRegenerator] Sesión reanudada:")
        print(f"   → Tono previo: {tone} | Tendencia: {state}")
        print(f"   → Nueva escena sugerida: {next_type}")
        print(f"   → Introducción: {intro[:90]}...")

        return {
            "tone": tone,
            "trend": trend,
            "state": state,
            "next_scene_type": next_type,
            "intro_text": intro,
        }

    # ------------------------------------------------------------
    # ✍️ Crear la introducción narrativa adaptada
    # ------------------------------------------------------------
    def _generate_intro_text(self, tone, trend, state, next_type):
        """
        Genera un texto de apertura basado en el tono previo y
        la dirección emocional de la campaña.
        """
        mood = self.mood_manager.current_tone
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        base = {
            "ascending": "La energía del grupo resuena aún con el eco de sus victorias recientes.",
            "descending": "La calma que sigue a la tormenta pesa sobre los corazones del grupo.",
            "stable": "El destino continúa su curso sin sobresaltos visibles, pero algo late bajo la superficie.",
        }

        tone_phrase = {
            "dark": "Sombras persistentes tiñen el aire.",
            "melancholic": "Un dejo de tristeza envuelve el amanecer.",
            "neutral": "El mundo respira con equilibrio.",
            "hopeful": "Una sensación de renovación los acompaña.",
            "bright": "La luz del nuevo día irradia confianza.",
        }

        text = (
            f"📜 {base.get(state, '')} {tone_phrase.get(tone, '')} "
            f"Ahora el viaje retoma su curso en una escena de tipo *{next_type}*.\n\n"
            f"*(Reanudado el {timestamp}, tono emocional '{mood}')*"
        )

        return text
