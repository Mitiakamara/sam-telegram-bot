# sam-telegram-bot/core/dice_roller/narrator.py
"""
Genera mini narraciones contextuales en base a la acción del jugador,
el atributo usado y el resultado de la tirada.
"""

def narrative_reaction(context_text: str, ability: str, total: int, d20: int, outcome: str) -> str:
    t = context_text.lower()

    # Base de tono
    if "crítico" in outcome.lower():
        tone = "✨ Crítico"
    elif "éxito" in outcome.lower():
        tone = "✅ Éxito"
    elif "fallo" in outcome.lower():
        tone = "❌ Fallo"
    else:
        tone = "⚖️ Resultado incierto"

    # Reacciones específicas por atributo
    if ability == "STR":
        if "empujar" in t or "romper" in t or "forzar" in t:
            if "éxito" in outcome.lower():
                return f"{tone}: {context_text.capitalize()} y logras romper el obstáculo con pura fuerza."
            else:
                return f"{tone}: {context_text.capitalize()} pero tus músculos no bastan esta vez."
        return f"{tone}: tu fuerza determina el resultado."

    if ability == "DEX":
        if "sigil" in t or "robar" in t or "mover" in t:
            if "éxito" in outcome.lower():
                return f"{tone}: te mueves con la gracia de una sombra."
            else:
                return f"{tone}: haces ruido y atraes miradas indeseadas."
        return f"{tone}: tu destreza decide el desenlace."

    if ability == "CON":
        if "resist" in t or "soport" in t or "aguant" in t:
            if "éxito" in outcome.lower():
                return f"{tone}: resistes con firmeza, superando el esfuerzo."
            else:
                return f"{tone}: tu cuerpo cede ante la fatiga."
        return f"{tone}: tu constitución pone a prueba tu resistencia."

    if ability == "INT":
        if "analiz" in t or "record" in t or "investig" in t:
            if "éxito" in outcome.lower():
                return f"{tone}: comprendes los detalles ocultos con rapidez."
            else:
                return f"{tone}: pasas por alto un dato crucial."
        return f"{tone}: tu intelecto guía el resultado."

    if ability == "WIS":
        if "percib" in t or "buscar" in t or "detectar" in t:
            if "éxito" in outcome.lower():
                return f"{tone}: notas lo que otros habrían pasado por alto."
            else:
                return f"{tone}: tu atención se distrae justo en el momento clave."
        return f"{tone}: tu instinto dicta el desenlace."

    if ability == "CHA":
        if "convenc" in t or "persuad" in t or "habl" in t:
            if "éxito" in outcome.lower():
                return f"{tone}: tus palabras fluyen con carisma y confianza."
            else:
                return f"{tone}: tus argumentos no logran cambiar su opinión."
        return f"{tone}: tu presencia marca la diferencia."

    # Fallback general
    return f"{tone}: el resultado de tu acción es incierto."
