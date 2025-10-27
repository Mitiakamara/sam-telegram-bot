import re

class EmotionService:
    """
    Servicio que evalúa la intensidad emocional de un texto narrativo
    según palabras clave y tono general (muy simple pero eficaz).
    """

    def evaluate_emotion(self, text: str) -> int:
        if not text:
            return 3

        text = text.lower()
        emotion_score = 3

        positive = ["esperanza", "valentía", "luz", "alegría", "paz"]
        negative = ["miedo", "oscuridad", "dolor", "muerte", "odio"]
        intense = ["batalla", "grito", "fuego", "sangre", "furia"]

        if any(word in text for word in intense):
            emotion_score = 5
        elif any(word in text for word in negative):
            emotion_score = 4
        elif any(word in text for word in positive):
            emotion_score = 2

        # Rango entre 1–5
        return max(1, min(emotion_score, 5))
