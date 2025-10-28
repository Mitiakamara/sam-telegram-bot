"""
ToneAdapter
------------
Módulo responsable de adaptar el tono narrativo de los textos según:
- La emoción dominante de la escena.
- El estado tonal global (mood) de la campaña.
- El género narrativo definido en el Mood Manager.
"""

import json
import os
import random
from textwrap import shorten


class ToneAdapter:
    """
    Ajusta la narrativa textual a un tono coherente con el mood global.
    """

    def __init__(self, emotional_scale_path: str | None = None):
        """
        Carga (opcionalmente) una escala emocional de referencia desde JSON.
        Si no se proporciona, usa un conjunto de intensificadores por defecto.
        """
        self.emotional_scale_path = emotional_scale_path or "data/emotion/emotional_scale.json"
        self.scale = self._load_emotional_scale()

    # ==========================================================
    # 📚 CARGA DE ESCALA EMOCIONAL
    # ==========================================================
    def _load_emotional_scale(self):
        """Carga una escala emocional personalizada desde JSON (opcional)."""
        try:
            if not os.path.exists(self.emotional_scale_path):
                return self._default_scale()
            with open(self.emotional_scale_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self._default_scale()

    def _default_scale(self):
        """Escala base de referencia en caso de no encontrar el archivo."""
        return {
            "hopeful": ["luminoso", "inspirador", "heroico"],
            "tense": ["tenso", "suspenso", "precario"],
            "melancholic": ["triste", "nostálgico", "lento"],
            "grim": ["oscuro", "sombrío", "opresivo"],
            "serene": ["calmo", "tranquilo", "armonioso"],
            "mystical": ["enigmático", "etéreo", "misterioso"],
            "chaotic": ["violento", "confuso", "impredecible"],
            "triumphant": ["victorioso", "glorioso", "enérgico"]
        }

    # ==========================================================
    # 🎨 FUNCIÓN PRINCIPAL
    # ==========================================================
    def adapt_tone(
        self,
        description: str,
        emotion: str = "neutral",
        intensity: float = 0.5,
        genre: str = "heroic"
    ) -> str:
        """
        Adapta la descripción textual según el estado emocional y el género.
        - emotion: emoción base de la escena.
        - intensity: nivel de impacto emocional (0.0–1.0).
        - genre: género narrativo global ("heroic", "dark_fantasy", "mystery", etc.).
        """

        base_text = description.strip()
        if not base_text:
            return ""

        # Truncar descripciones demasiado largas (por seguridad)
        base_text = shorten(base_text, width=900, placeholder="...")

        mood_word = self._pick_mood_word(emotion)
        tone_suffix = self._genre_suffix(genre, intensity)

        # Aplicar estilo tonal según intensidad emocional
        adapted = self._tone_transform(base_text, emotion, intensity)
        adapted = f"{adapted} {tone_suffix}".strip()

        # Ajustar puntuación y formato final
        if not adapted.endswith(('.', '!', '?')):
            adapted += "."

        # Enriquecer con matices de mood
        if random.random() < 0.6:
            adapted = adapted.replace(".", f", en un ambiente {mood_word}.")

        return adapted

    # ==========================================================
    # 🔹 UTILIDADES INTERNAS DE TONO
    # ==========================================================
    def _pick_mood_word(self, emotion: str) -> str:
        """
        Devuelve una palabra descriptiva coherente con la emoción dada.
        """
        emotion = emotion.lower()
        if emotion in self.scale:
            return random.choice(self.scale[emotion])

        # fallback simples
        if emotion in ["fear", "terror"]:
            return "tenso"
        if emotion in ["joy", "hope"]:
            return "luminoso"
        if emotion in ["sadness", "melancholy"]:
            return "melancólico"
        if emotion in ["anger", "rage"]:
            return "intenso"
        return "neutral"

    def _tone_transform(self, text: str, emotion: str, intensity: float) -> str:
        """
        Aplica modificaciones ligeras al texto según intensidad emocional.
        """
        emotion = emotion.lower()
        if intensity < 0.3:
            # tono más descriptivo y pausado
            return f"{text} El aire se siente calmado, las emociones contenidas."
        elif intensity < 0.6:
            # tono equilibrado
            return f"{text} Una tensión sutil recorre el ambiente."
        else:
            # tono intenso o dramático
            if emotion in ["fear", "anger", "chaotic"]:
                return f"{text} El pulso de la escena late con fuerza y peligro."
            elif emotion in ["hope", "joy", "triumph"]:
                return f"{text} El espíritu del grupo se enciende con energía y valor."
            else:
                return f"{text} La atmósfera vibra con emoción contenida."

    def _genre_suffix(self, genre: str, intensity: float) -> str:
        """
        Añade un matiz final según el género narrativo y la intensidad.
        """
        genre = genre.lower()
        if genre == "heroic":
            return "Los espíritus de la aventura arden en sus corazones."
        elif genre == "dark_fantasy":
            return "Sombras antiguas parecen observar cada paso del grupo."
        elif genre == "mystery":
            return "Un velo de secretos flota en el aire."
        elif genre == "exploration":
            return "El mundo se despliega ante ellos, vasto e indómito."
        elif genre == "horror":
            return "Un escalofrío invisible se arrastra entre las sombras."
        elif genre == "romantic":
            return "Los latidos del destino se entrelazan con los del corazón."
        else:
            return "El destino parece escribir sus líneas con cautela."
