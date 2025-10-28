import random
from datetime import datetime
from core.emotion import emotional_analytics as analytics
from core.emotion.emotional_tracker import get_emotional_summary
from core.emotion.tone_blender import ToneBlender

# ================================================================
# 💫 EMOTIONAL FEEDBACK LOOP (actualizado con Tone Blending)
# ================================================================
# Orquesta el ciclo de retroalimentación emocional entre:
# Tone Adapter → Emotional Tracker → Emotional Analytics →
# Story Director → Mood Manager.
#
# Ahora incluye Fase 6.19: mezcla de tonos (Tone Blending)
# para transiciones más naturales entre estados emocionales.
# ================================================================


class EmotionalFeedbackLoop:
    def __init__(self, tone_adapter, mood_manager, story_director):
        self.tone_adapter = tone_adapter
        self.mood_manager = mood_manager
        self.story_director = story_director
        self.last_update = None
        self.last_adjustment = {}
        self.blender = ToneBlender()
        self.previous_tone = getattr(mood_manager, "current_tone", "neutral")

    # ------------------------------------------------------------
    # 🔄 Procesa la retroalimentación emocional global
    # ------------------------------------------------------------
    def process_feedback(self):
        """
        Lee los datos agregados de emociones, tendencias y tono,
        y ajusta los parámetros de tono global y narrativa.
        """
        curve = analytics.build_emotional_curve()
        tone_score = analytics.compute_tone_score()
        trend = analytics.emotional_trend_score(window=5)
        summary = get_emotional_summary()

        self.last_update = datetime.utcnow().isoformat()
        adjustment = {"tone": None, "style_bias": None, "narrative_pace": None, "blend": None}

        # Guardar tono anterior antes de modificar
        prev_tone = self.mood_manager.current_tone
        new_tone = tone_score["label"]

        # --- Ajuste del tono narrativo global ---
        if new_tone in ["dark", "melancholic"]:
            self.mood_manager.current_tone = "hopeful"
            adjustment["tone"] = "Elevando tono (neutralizar oscuridad)"
            adjustment["style_bias"] = "poético pero optimista"
        elif new_tone in ["bright", "hopeful"]:
            self.mood_manager.current_tone = "tense"
            adjustment["tone"] = "Inyectando tensión para equilibrio"
            adjustment["style_bias"] = "más sombrío y reflexivo"
        else:
            self.mood_manager.current_tone = "neutral"
            adjustment["tone"] = "Estabilizando tono narrativo"
            adjustment["style_bias"] = "balanceado"

        # --- Mezcla de tonos (Tone Blending) ---
        blended = self.blender.blend(prev_tone, self.mood_manager.current_tone)
        adjustment["blend"] = blended
        self.mood_manager.last_blend = blended  # guardar referencia en mood_manager

        # --- Ajuste del ritmo narrativo ---
        if trend["direction"] == "rising":
            adjustment["narrative_pace"] = "reduce tempo"  # muchas emociones → pausa narrativa
        elif trend["direction"] == "falling":
            adjustment["narrative_pace"] = "increase tempo"  # historia plana → más acción
        else:
            adjustment["narrative_pace"] = "steady"

        self.last_adjustment = adjustment

        # --- Influencia en el Story Director ---
        next_scene_type = self.story_director.decide_next_scene_type()

        print("\n💫 [EmotionalFeedbackLoop] Ciclo procesado:")
        print(f"   → Tono global detectado: {tone_score['label']}")
        print(f"   → Tendencia emocional: {trend['direction']}")
        print(f"   → Ajuste aplicado: {adjustment['tone']}")
        print(f"   → Mezcla de tonos: {blended['label']} ({blended['description']})")
        print(f"   → Próxima escena sugerida: {next_scene_type}\n")

        return {
            "timestamp": self.last_update,
            "tone_score": tone_score,
            "trend": trend,
            "summary": summary,
            "adjustment": adjustment,
            "next_scene_type": next_scene_type,
        }

    # ------------------------------------------------------------
    # 🧠 Genera un mensaje narrativo adaptado para la IA
    # ------------------------------------------------------------
    def build_adaptive_prompt(self):
        """
        Construye un prompt con el tono y ritmo adaptado
        para el generador de texto (renderer / GPT).
        """
        decision = self.story_director.last_decision or {}
        tone_label = decision.get("tone", {}).get("label", "neutral")
        emotion = decision.get("dominant_emotion", "neutral")
        next_scene = decision.get("next_scene_type", "progress")
        style_bias = self.last_adjustment.get("style_bias", "neutral")

        blend_info = self.last_adjustment.get("blend", {})
        blend_label = blend_info.get("label", "none")
        blend_description = blend_info.get("description", "")

        prompt = (
            f"El tono actual de la campaña es '{tone_label}', con una emoción dominante de '{emotion}'. "
            f"El sistema recomienda que la siguiente escena sea de tipo '{next_scene}'. "
            f"Adopta un estilo {style_bias}, integrando el matiz '{blend_label}' "
            f"({blend_description.lower()}) para una transición emocional fluida."
        )
        return prompt
