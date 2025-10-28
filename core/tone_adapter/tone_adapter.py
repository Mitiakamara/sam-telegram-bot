import re
import random
import json
from pathlib import Path


class ToneAdapter:
    """
    Ajusta el tono narrativo según emoción, intensidad y género.
    Evita repetir frases como 'en un ambiente neutral'.
    """

    def __init__(self, emotional_scale_path: str | None = None):
        self.emotional_scale = {}
        if emotional_scale_path and Path(emotional_scale_path).exists():
            with open(emotional_scale_path, "r", encoding="utf-8") as f:
                try:
                    self.emotional_scale = json.load(f)
                except Exception:
                    self.emotional_scale = {}

    # ================================================================
    # 🎭 ADAPTACIÓN DE TONO NARRATIVO
    # ================================================================
    def adapt_tone(self, description: str, emotion: str = "neutral",
                   intensity: float = 0.5, genre: str = "heroic") -> str:
        """
        Ajusta el texto según el tono emocional actual y la intensidad global.
        """

        if not description:
            return ""

        # Evita duplicaciones tipo "en un ambiente X"
        clean_desc = re.sub(r"(,?\s*en un ambiente\s+\w+)", "", description.strip(), flags=re.IGNORECASE)

        tone_variants = {
            "neutral": [
                "El aire se mantiene equilibrado.",
                "Una calma serena domina el ambiente.",
                "El momento parece suspendido en quietud."
            ],
            "hopeful": [
                "Una chispa de esperanza ilumina los corazones.",
                "La luz del amanecer parece prometer nuevos comienzos.",
                "El ánimo del grupo se eleva con optimismo."
            ],
            "fearful": [
                "Una tensión sutil recorre el ambiente.",
                "El silencio pesa, como si algo acechara en las sombras.",
                "El miedo se siente en el aire, denso e invisible."
            ],
            "melancholic": [
                "El aire trae recuerdos del pasado, cargados de nostalgia.",
                "Una brisa fría parece murmurar viejas historias.",
                "La tristeza impregna el ambiente con un eco suave."
            ],
            "triumphant": [
                "El aire vibra con energía victoriosa.",
                "Los corazones laten con orgullo tras la hazaña.",
                "Un brillo de triunfo se refleja en sus miradas."
            ],
            "grim": [
                "El entorno parece teñido por una sombra ominosa.",
                "Todo se siente más pesado, como si el destino observara.",
                "Una sensación de fatalidad flota sobre ellos."
            ],
            "mystical": [
                "Energías invisibles parecen fluir alrededor.",
                "El mundo vibra con una magia antigua y poderosa.",
                "Sombras y luces danzan en armonía inexplicable."
            ],
            "serene": [
                "El ambiente irradia calma y equilibrio.",
                "Una brisa suave acaricia los rostros.",
                "El entorno respira paz natural."
            ]
        }

        # Escoge una frase según emoción
        tone_suffix = random.choice(tone_variants.get(emotion, tone_variants["neutral"]))

        # Integra la emoción como matiz, no como repetición
        final = f"{clean_desc} {tone_suffix}"

        # Ajuste leve por intensidad (más dramático o más suave)
        if intensity >= 0.8:
            final += " La tensión es palpable, cada detalle parece más vívido."
        elif intensity <= 0.3:
            final += " Todo se siente más distante, como si el mundo respirara lentamente."

        return final.strip()
