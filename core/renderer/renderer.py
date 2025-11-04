# ================================================================
# 🎨 SAM RENDERER ENGINE – Fase 7.3+
# ================================================================
# Función de salida narrativa simplificada.
# Es el último paso del pipeline narrativo:
# SceneAdapter ➜ ToneAdapter ➜ EmotionalTracker ➜ Renderer
# ================================================================


def render(text: str) -> str:
    """
    Produce la versión final del texto narrativo que se enviará al jugador.
    En la Fase 7.3+ no altera el contenido —solo garantiza un punto de salida estable.
    """
    if not text:
        return ""
    return text.strip()


# =========================================================
# DEMO LOCAL
# =========================================================
if __name__ == "__main__":
    sample = "El grupo avanza entre las ruinas antiguas, decidido a enfrentar su destino."
    print(render(sample))
