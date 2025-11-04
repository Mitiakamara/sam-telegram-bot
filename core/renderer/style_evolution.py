# ================================================================
# 🖋️ STYLE EVOLUTION MODULE
# ================================================================
# Ajusta el estilo narrativo según el modo seleccionado.
# Permite variar el ritmo, la cadencia o el dramatismo del texto.
# ================================================================

import random


def evolve_style(text: str, mode: str = "default") -> str:
    """
    Aplica variaciones estilísticas al texto según el modo.
    Modos disponibles:
      - "default": mantiene el texto original.
      - "dynamic": acorta o enfatiza frases para ritmo rápido.
      - "calm": introduce pausas suaves y alarga la cadencia.
      - "poetic": añade resonancia lírica y fluidez.
    """
    if not text:
        return ""

    mode = mode.lower()

    if mode == "default":
        return text

    elif mode == "dynamic":
        # frases cortas, energía, ritmo veloz
        parts = text.split(".")
        short = [p.strip() for p in parts if p.strip()]
        return "! ".join(short) + "!"

    elif mode == "calm":
        # cadencia suave, pausas prolongadas
        return text.replace(".", "...").replace(",", ", ")

    elif mode == "poetic":
        endings = ["~", "⋆", "❧"]
        return text.replace(".", random.choice(endings)).replace(",", ", ")

    return text
