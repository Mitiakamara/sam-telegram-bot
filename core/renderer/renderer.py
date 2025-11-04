# ================================================================
# 🎨 RENDERER ENGINE – Fase 7.3
# ================================================================
# Genera la salida textual final del motor narrativo de SAM.
# Combina estilo, voz del narrador y formato dinámico.
# ================================================================

from core.renderer.narrator_persona import apply_narrator_voice
from core.renderer.style_evolution import evolve_style


def render(text: str, style: str = "default") -> str:
    """
    Genera la versión final del texto narrativo que se mostrará al jugador.
    Aplica la evolución de estilo y la voz del narrador de forma secuencial.
    """
    if not text:
        return ""

    # 1. Ajustar el estilo narrativo (ritmo, cadencia, etc.)
    styled_text = evolve_style(text, mode=style)

    # 2. Aplicar la voz del narrador / persona narrativa
    narrated_text = apply_narrator_voice(styled_text)

    return narrated_text


# =========================================================
# DEMO LOCAL
# =========================================================
if __name__ == "__main__":
    sample = "El grupo observa las antiguas ruinas mientras el viento sopla entre las columnas rotas."
    print(render(sample, style="poetic"))
