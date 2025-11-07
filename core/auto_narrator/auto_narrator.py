import logging

logger = logging.getLogger("AutoNarrator")

class AutoNarrator:
    """
    Versión mínima del narrador automático.
    Genera descripciones simples según la emoción del estado.
    """

    def __init__(self):
        logger.info("[AutoNarrator] Inicializado correctamente.")

    def generate_description(self, scene_text: str, emotion: str = "neutral") -> str:
        """Devuelve una descripción simple combinando escena + tono emocional."""
        tone_map = {
            "neutral": "El ambiente permanece equilibrado y sin tensiones.",
            "tensa": "Una sensación de tensión recorre el aire.",
            "triste": "Una sombra melancólica cubre el entorno.",
            "triunfante": "El ánimo del grupo se eleva con orgullo y determinación.",
            "oscura": "La atmósfera se vuelve densa y opresiva.",
        }
        tone = tone_map.get(emotion.lower(), tone_map["neutral"])
        return f"{scene_text}\n\n🎭 *Tono narrativo:* {tone}"
