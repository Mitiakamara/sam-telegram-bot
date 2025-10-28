import random
from datetime import datetime

# ================================================================
# 💞 MOOD MANAGER (actualizado con Tone Blending)
# ================================================================
# Gestiona el tono emocional global de la narrativa.
# Ahora incorpora la mezcla de tonos (Tone Blending)
# y el concepto de “matiz emocional activo”.
# ================================================================


class MoodManager:
    def __init__(self):
        self.current_tone = "neutral"
        self.last_tone = "neutral"
        self.last_blend = None
        self.tone_history = []
        self.intensity = 0.5
        self.timestamp = datetime.utcnow().isoformat()

    # ------------------------------------------------------------
    # 🎭 Actualizar el tono global
    # ------------------------------------------------------------
    def set_tone(self, tone_label: str, blend: dict = None):
        """
        Cambia el tono global de la narrativa. Si se proporciona un blend,
        se integra como matiz emocional.
        """
        self.last_tone = self.current_tone
        self.current_tone = tone_label
        self.timestamp = datetime.utcnow().isoformat()

        if blend:
            self.last_blend = blend

        # Guardar registro histórico
        self.tone_history.append({
            "timestamp": self.timestamp,
            "tone": self.current_tone,
            "blend": self.last_blend
        })

        print(f"🎭 [MoodManager] Tono actualizado → {self.current_tone} ({self.describe_tone()})")

    # ------------------------------------------------------------
    # 💫 Obtener descripción del tono activo
    # ------------------------------------------------------------
    def describe_tone(self) -> str:
        """Devuelve una descripción textual del tono actual, incluyendo blend activo."""
        base_desc = {
            "dark": "sombrío, introspectivo",
            "melancholic": "triste, reflexivo",
            "neutral": "equilibrado, observador",
            "hopeful": "luminoso, optimista",
            "bright": "energético, expresivo",
            "tense": "intenso, expectante",
        }

        desc = base_desc.get(self.current_tone, "indefinido")
        if self.last_blend:
            desc += f" con matiz '{self.last_blend['label']}' ({self.last_blend['description']})"
        return desc

    # ------------------------------------------------------------
    # 🔊 Ajustar intensidad emocional
    # ------------------------------------------------------------
    def adjust_intensity(self, delta: float):
        """Incrementa o reduce la intensidad emocional global."""
        self.intensity = max(0.0, min(1.0, self.intensity + delta))
        print(f"🔥 [MoodManager] Intensidad emocional ajustada a {self.intensity}")

    # ------------------------------------------------------------
    # 🧩 Obtener estado completo del mood
    # ------------------------------------------------------------
    def get_state(self):
        """Devuelve un snapshot del estado emocional global."""
        return {
            "tone": self.current_tone,
            "last_tone": self.last_tone,
            "blend": self.last_blend,
            "intensity": self.intensity,
            "timestamp": self.timestamp,
            "history": self.tone_history[-5:],  # últimas 5 entradas
        }

    # ------------------------------------------------------------
    # 🧠 Generar prompt descriptivo para narrador o IA
    # ------------------------------------------------------------
    def build_mood_prompt(self) -> str:
        """
        Devuelve una cadena de texto que describe el tono e intensidad actuales,
        para alimentar al narrador IA (renderer / GPT).
        """
        blend_text = ""
        if self.last_blend:
            blend_text = f" con un matiz de '{self.last_blend['label']}' ({self.last_blend['description'].lower()})"

        return (
            f"El tono global actual es '{self.current_tone}'{blend_text}. "
            f"La intensidad emocional se encuentra en {self.intensity:.2f}. "
            f"El estilo narrativo debería reflejar este equilibrio tonal."
        )
