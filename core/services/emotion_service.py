# sam-telegram-bot/core/services/emotion_service.py
"""
EmotionService
--------------
Analiza descripciones o resultados narrativos y devuelve
una emoción predominante y su intensidad numérica.
Este módulo permite que ToneAdapter y MoodManager
sincronicen el tono narrativo en tiempo real.
"""

import re
import math


class EmotionService:
    """
    Servicio de análisis emocional semántico simple.
    No depende de modelos externos: usa reglas heurísticas
    para detectar emociones comunes en descripciones.
    """

    def __init__(self):
        # Diccionario básico de palabras clave → emoción
        self.emotion_keywords = {
            "fear": ["miedo", "terror", "temor", "horror", "pánico"],
            "anger": ["ira", "furia", "rabia", "odio", "enojo"],
            "sadness": ["triste", "melancol", "soledad", "pena", "llanto", "perdida"],
            "hope": ["esperanza", "confianza", "ánimo", "determinación"],
            "joy": ["alegría", "risa", "felicidad", "placer", "diversión"],
            "tension": ["tenso", "inquietud", "nervios", "incertidumbre"],
            "triumph": ["victoria", "gloria", "éxito", "triunfo"],
            "serenity": ["calma", "paz", "tranquilidad", "descanso"],
            "mystery": ["misterio", "enigma", "oculto", "secreto", "arcano"],
            "neutral": []
        }

    # ==========================================================
    # 🔍 ANÁLISIS PRINCIPAL
    # ==========================================================
    def evaluate_emotion(self, text: str) -> tuple[str, float]:
        """
        Devuelve una tupla (label, intensity) representando
        la emoción dominante y su fuerza (0.0 – 1.0).
        """
        if not text or not isinstance(text, str):
            return ("neutral", 0.5)

        text = text.lower()

        # Contar coincidencias de palabras por emoción
        scores = {emotion: 0 for emotion in self.emotion_keywords}
        for emotion, keywords in self.emotion_keywords.items():
            for kw in keywords:
                if re.search(rf"\b{kw}", text):
                    scores[emotion] += 1

        # Determinar emoción dominante
        dominant = max(scores, key=scores.get)
        max_score = scores[dominant]

        if max_score == 0:
            return ("neutral", 0.5)

        # Calcular intensidad normalizada según cantidad de palabras detectadas
        intensity = min(1.0, 0.3 + math.log1p(max_score) / 3.0)

        return (dominant, round(intensity, 2))

    # ==========================================================
    # 🧮 CONVERSIÓN SIMPLE A NIVEL NUMÉRICO
    # ==========================================================
    def emotion_to_level(self, emotion_label: str) -> float:
        """
        Devuelve un valor numérico base para una emoción textual.
        """
        mapping = {
            "joy": 0.8,
            "hope": 0.7,
            "triumph": 0.9,
            "fear": 0.6,
            "tension": 0.6,
            "anger": 0.7,
            "sadness": 0.4,
            "serenity": 0.5,
            "mystery": 0.5,
            "neutral": 0.5
        }
        return mapping.get(emotion_label.lower(), 0.5)
