# sam-telegram-bot/core/scene_manager/tone_adapter.py
"""
ToneAdapter
-----------
Módulo responsable de ajustar el tono narrativo de las descripciones
en función de la intensidad emocional y del contexto narrativo.

Escala emocional (1–5):
1: Sereno / Tranquilo
2: Reflexivo / Melancólico
3: Neutral / Aventurero
4: Intenso / Heroico
5: Desesperado / Épico
"""

import re


class ToneAdapter:
    def __init__(self):
        # Paletas de vocabulario para modificar el tono narrativo
        self.tone_map = {
            1: {
                "prefix": "La calma del entorno parece envolverlo todo. ",
                "adjectives": ["sereno", "tranquilo", "apacible", "templado"],
            },
            2: {
                "prefix": "Una sensación melancólica se filtra en el aire. ",
                "adjectives": ["nostálgico", "sombrío", "reflexivo", "apagado"],
            },
            3: {
                "prefix": "",
                "adjectives": ["curioso", "decidido", "atento", "determinado"],
            },
            4: {
                "prefix": "La tensión es palpable, los corazones laten con fuerza. ",
                "adjectives": ["enérgico", "urgente", "ardiente", "temerario"],
            },
            5: {
                "prefix": "El destino pende de un hilo, y cada respiración es un desafío. ",
                "adjectives": ["desesperado", "épico", "heroico", "trágico"],
            },
        }

    # ==========================================================
    # 🔹 FUNCIÓN PRINCIPAL
    # ==========================================================
    def adapt_description(self, text: str, emotion_intensity: int = 3) -> str:
        """
        Adapta el texto original según la emoción (1–5).
        Reemplaza adjetivos genéricos y añade un prefacio narrativo.
        """
        if not text:
            return ""

        tone = self.tone_map.get(emotion_intensity, self.tone_map[3])
        adapted_text = text.strip()

        # Añadir prefijo si existe
        if tone["prefix"]:
            adapted_text = f"{tone['prefix']}{adapted_text}"

        # Sustituciones leves para el tono
        adapted_text = self._adjust_words(adapted_text, tone["adjectives"])
        adapted_text = self._normalize_spacing(adapted_text)
        return adapted_text

    # ==========================================================
    # 🔹 MÉTODOS AUXILIARES
    # ==========================================================
    def _adjust_words(self, text: str, adjectives: list[str]) -> str:
        """
        Realiza ligeros ajustes léxicos para reflejar el tono.
        No altera la estructura, solo pequeños matices descriptivos.
        """
        replacements = {
            "oscuro": adjectives[0],
            "frío": adjectives[1],
            "silencioso": adjectives[2],
            "violento": adjectives[3],
        }

        for word, new_word in replacements.items():
            pattern = rf"\b{re.escape(word)}\b"
            text = re.sub(pattern, new_word, text, flags=re.IGNORECASE)
        return text

    def _normalize_spacing(self, text: str) -> str:
        """Limpia espacios duplicados y mejora la puntuación."""
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"\s+([.,!?])", r"\1", text)
        return text.strip()
