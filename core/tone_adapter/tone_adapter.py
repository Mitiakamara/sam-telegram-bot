import random

class ToneAdapter:
    """
    Controla el tono narrativo global, mezclando el estado emocional
    y los arquetipos derivados de los atributos del grupo (Fase 7.2).
    """

    def __init__(self):
        # Tonos base por emoción
        self.emotional_tones = {
            "neutral": ["calmo", "sereno", "equilibrado"],
            "tension": ["tenso", "oscuro", "angustioso"],
            "progress": ["determinado", "esperanzador", "dinámico"],
            "triumph": ["heroico", "luminoso", "épico"],
            "setback": ["melancólico", "opresivo", "desalentador"],
            "fear": ["frío", "susurrante", "sombrío"]
        }

        # Paletas de tono narrativo según arquetipos
        self.trait_tone_map = {
            "brute": ["violento", "firme", "impactante"],
            "graceful": ["sutil", "elegante", "preciso"],
            "clever": ["analítico", "ingenioso", "reflexivo"],
            "resilient": ["constante", "duro", "tenaz"],
            "insightful": ["introspectivo", "místico", "poético"],
            "charming": ["persuasivo", "carismático", "cálido"]
        }

    # =========================================================
    # APLICAR TONO SEGÚN PERFIL Y EMOCIÓN
    # =========================================================
    def apply_tone(self, text, emotional_state="neutral", party_profile=None):
        """
        Aplica modificaciones descriptivas al texto según:
        - Estado emocional global del mundo/escena
        - Perfil narrativo del grupo (Fase 7.2)
        """
        if not text:
            return ""

        # Determinar adjetivo emocional
        emotion_tone = random.choice(self.emotional_tones.get(emotional_state, ["neutro"]))

        # Determinar arquetipo dominante del grupo
        if party_profile:
            dominant_trait = max(party_profile, key=party_profile.get)
            trait_tones = self.trait_tone_map.get(dominant_trait, ["neutro"])
            trait_tone = random.choice(trait_tones)
        else:
            trait_tone = "neutro"

        # Mezclar los dos tonos en la narración
        tone_intro = f"En un ambiente {emotion_tone} y {trait_tone}, "
        adapted = f"{tone_intro}{text.strip()}"
        return adapted

    # =========================================================
    # AJUSTE DE RITMO SEGÚN INTENSIDAD
    # =========================================================
    def adjust_sentence_rhythm(self, text, intensity):
        """
        Ajusta la cadencia narrativa en función de la intensidad emocional.
        - > 0.7: ritmo rápido (frases cortas, exclamaciones)
        - < 0.3: ritmo pausado (puntos suspensivos)
        """
        if intensity > 0.7:
            parts = text.split(".")
            shortened = [p.strip() for p in parts if p.strip()]
            return "! ".join(shortened) + "!"
        elif intensity < 0.3:
            return text.replace(".", "...").strip()
        return text


# =========================================================
# DEMO LOCAL
# =========================================================
if __name__ == "__main__":
    adapter = ToneAdapter()
    sample_text = "El grupo avanza entre las ruinas antiguas, observando el horizonte incierto."
    profile = {
        "brute": 0.3, "graceful": 0.8, "clever": 0.6, "resilient": 0.4, "insightful": 0.5, "charming": 0.7
    }
    print(adapter.apply_tone(sample_text, emotional_state="progress", party_profile=profile))
