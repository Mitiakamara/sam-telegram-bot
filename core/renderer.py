# ================================================================
# 🪄 SAM – Renderer (Modo Campaña Pre-Creada)
# ================================================================
# Convierte los datos narrativos generados por el Orchestrator
# en texto limpio y presentable para el usuario (Telegram).
# ================================================================

import textwrap
import logging

logger = logging.getLogger(__name__)

# ------------------------------------------------
# 🔧 Función principal
# ------------------------------------------------
def render(scene_description: str, tone: str = "neutral", emotion: str = "neutral") -> str:
    """
    Recibe un bloque narrativo y lo adapta a formato jugable.
    Ajusta estilo y tono según la emoción dominante.
    """

    if not scene_description:
        return "Silencio… (no hay descripción disponible)."

    # Normalizar texto
    scene_description = scene_description.strip()
    scene_description = textwrap.fill(scene_description, width=100)

    # Adaptar según tono o emoción global
    tone_prefix = {
        "hopeful": "✨ Con un aire de esperanza,",
        "dark": "🌒 La atmósfera se vuelve sombría:",
        "tense": "⚡ Una tensión invisible recorre el ambiente:",
        "calm": "🌿 En calma y silencio,",
        "neutral": ""
    }.get(tone, "")

    emotion_suffix = {
        "joy": "😊 Un leve optimismo se percibe entre los aventureros.",
        "fear": "😨 Un escalofrío recorre sus espaldas.",
        "anger": "🔥 La frustración late en cada respiración.",
        "sadness": "😔 El silencio pesa sobre sus corazones.",
        "surprise": "😲 Todo ocurre más rápido de lo esperado.",
        "neutral": ""
    }.get(emotion, "")

    output = f"{tone_prefix} {scene_description} {emotion_suffix}".strip()
    logger.info(f"[Renderer] Escena renderizada con tono='{tone}', emoción='{emotion}'")
    return output


# ------------------------------------------------
# 🧩 Compatibilidad con Orchestrator
# ------------------------------------------------
def render_message(scene_data: dict) -> str:
    """
    Renderiza una escena completa a texto jugable.
    """
    description = scene_data.get("description", "")
    tone = scene_data.get("tone", "neutral")
    emotion = scene_data.get("dominant_emotion", "neutral")

    return render(description, tone=tone, emotion=emotion)
