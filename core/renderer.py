# sam-telegram-bot/core/renderer.py
"""
Renderer
---------
Normaliza y limpia la salida narrativa para Telegram.
Convierte texto en Markdown seguro y compatible con el motor actual.
"""

import re


def render(text: str = "", intent: str | None = None, action: str | None = None) -> str:
    """
    Recibe texto narrativo (o resultado del StoryDirector) y lo devuelve limpio
    para mostrar en Telegram. Compatible con firmas antiguas.
    """
    if not text:
        return "..."

    try:
        # Si el texto es un objeto complejo, conviértelo a string
        if not isinstance(text, str):
            text = str(text)

        # Limpieza ligera y protección Markdown
        clean_text = text.strip()
        clean_text = re.sub(r"[*_`~>|{}[\]()#+=.!-]", "", clean_text)
        clean_text = re.sub(r"\s{3,}", "  ", clean_text)

        # Capitalizar primera letra si hace falta
        if len(clean_text) > 1 and clean_text[0].islower():
            clean_text = clean_text[0].upper() + clean_text[1:]

        return clean_text

    except Exception as e:
        return f"⚠️ Error al renderizar texto: {e}"
