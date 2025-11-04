# ================================================================
# 🗣️ NARRATOR PERSONA MODULE
# ================================================================
# Define el tono y la personalidad del narrador.
# Se puede ajustar por campaña o escena para variar la voz narrativa.
# ================================================================

import random


def apply_narrator_voice(text: str, persona: str = "neutral") -> str:
    """
    Aplica la voz del narrador según la personalidad seleccionada.
    Las voces posibles son:
      - "neutral": narración descriptiva estándar.
      - "dramatic": más emocional y evocativa.
      - "sarcastic": tono burlón o irónico.
      - "poetic": con metáforas suaves y ritmo lírico.
    """
    if not text:
        return ""

    persona = persona.lower()

    if persona == "neutral":
        return text

    elif persona == "dramatic":
        intros = [
            "Con una tensión que corta el aire, ",
            "El destino se inclina hacia ellos mientras ",
            "En un suspiro de grandeza, "
        ]
        return random.choice(intros) + text.lower()

    elif persona == "sarcastic":
        intros = [
            "Ah, claro, como si fuera tan fácil... ",
            "Porque obviamente todo saldrá bien, ",
            "Qué podría salir mal esta vez, ¿eh? "
        ]
        return random.choice(intros) + text.lower()

    elif persona == "poetic":
        intros = [
            "Como un eco perdido en el tiempo, ",
            "En el murmullo del viento ancestral, ",
            "Bajo un cielo que respira memorias, "
        ]
        return random.choice(intros) + text.lower()

    # fallback
    return text
