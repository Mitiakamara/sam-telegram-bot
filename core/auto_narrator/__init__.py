"""
Módulo Auto Narrator
====================

Contiene la clase AutoNarrator, responsable de generar descripciones narrativas
adaptadas al tono emocional actual del juego.

Ejemplo de uso:
    from core.auto_narrator import AutoNarrator

    narrator = AutoNarrator()
    text = narrator.generate_description("El grupo entra a una caverna", "tensa")
    print(text)
"""

from .auto_narrator import AutoNarrator

__all__ = ["AutoNarrator"]
