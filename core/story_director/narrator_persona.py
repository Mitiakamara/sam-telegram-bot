"""
NarratorPersona
---------------
Define estilos narrativos emergentes para S.A.M.
Cada "voz" tiene un tono, vocabulario y actitud propios,
seleccionados dinámicamente según la memoria dramática.
"""

import random
from core.story_director.memory_manager import MemoryManager


class NarratorPersona:
    def __init__(self):
        self.memory = MemoryManager()
        self.persona = self._determine_persona()

    # ==========================================================
    # 🔹 DETERMINAR PERSONALIDAD ACTUAL
    # ==========================================================
    def _determine_persona(self):
        avg_emotion = self.memory.get_average_emotion()
        theme = self.memory.get_recurrent_theme() or "misterio"

        # Tonos posibles
        if avg_emotion <= 2:
            return "sereno"
        elif avg_emotion >= 4:
            return "dramatico"
        elif theme in ["esperanza", "amistad"]:
            return "heroico"
        elif theme in ["traicion", "muerte"]:
            return "oscuro"
        else:
            return "neutral"

    # ==========================================================
    # 🔹 ADAPTAR NARRACIÓN SEGÚN PERSONALIDAD
    # ==========================================================
    def apply_persona(self, text: str) -> str:
        """
        Modifica el texto según el estilo actual del narrador.
        """
        style = self.persona

        if style == "sereno":
            phrases = [
                "S.A.M. suspira con calma.",
                "Una quietud reconfortante envuelve la escena.",
                "La historia fluye como un río tranquilo."
            ]
            text = f"{text}\n\n🕊️ {random.choice(phrases)}"

        elif style == "dramatico":
            phrases = [
                "S.A.M. declama con intensidad teatral.",
                "El eco de la tragedia resuena en sus palabras.",
                "Cada frase vibra con la tensión del destino."
            ]
            text = f"{text}\n\n🔥 {random.choice(phrases)}"

        elif style == "heroico":
            phrases = [
                "S.A.M. narra con el fervor de un trovador.",
                "Las palabras resplandecen con esperanza.",
                "La luz del coraje guía el relato."
            ]
            text = f"{text}\n\n⚔️ {random.choice(phrases)}"

        elif style == "oscuro":
            phrases = [
                "S.A.M. habla con un susurro cargado de presagio.",
                "Una sombra parece extenderse en su voz.",
                "El aire mismo contiene un sabor metálico a destino."
            ]
            text = f"{text}\n\n🌑 {random.choice(phrases)}"

        else:  # Neutral
            phrases = [
                "S.A.M. observa la escena con curiosidad.",
                "La historia continúa sin grandes sobresaltos.",
                "El narrador parece reflexionar en silencio."
            ]
            text = f"{text}\n\n📜 {random.choice(phrases)}"

        return text

    # ==========================================================
    # 🔹 CONSULTA DE PERFIL
    # ==========================================================
    def get_persona_summary(self):
        labels = {
            "sereno": "S.A.M. el Sereno (calmo y contemplativo)",
            "dramatico": "S.A.M. el Dramático (intenso y fatalista)",
            "heroico": "S.A.M. el Heroico (luminoso y entusiasta)",
            "oscuro": "S.A.M. el Oscuro (melancólico y ominoso)",
            "neutral": "S.A.M. el Crónico (observador y equilibrado)"
        }
        return labels.get(self.persona, "S.A.M. el Narrador")
