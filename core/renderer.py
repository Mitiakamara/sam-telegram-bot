# ================================================================
# 🎨 RENDERER
# ================================================================
# Convierte la salida narrativa en un formato de mensaje
# listo para enviarse por Telegram.
#
# Compatible con:
# - Emotional Feedback Loop (Fase 6.x)
# - StoryDirector (Fase 6.12+)
# - Consequence Resolver y Campañas pre-creadas (Fase 7.x)
# ================================================================

import logging
from core.models.telegram_msg import TelegramMessage, MessageBlock

logger = logging.getLogger(__name__)


def render(narrative_output: dict) -> TelegramMessage:
    """
    Transforma una salida narrativa en un mensaje TelegramMessage.

    narrative_output puede contener:
        - text: narrativa completa (str)
        - tone, emotion, scene_type, outcome: metadatos narrativos opcionales
    """

    # Si el sistema entrega texto puro
    if isinstance(narrative_output, str):
        message_text = narrative_output

        msg = TelegramMessage(
            text=message_text,
            blocks=[MessageBlock(type="text", content=message_text)]
        )

        logger.info("[Renderer] Mensaje renderizado (texto plano).")
        return msg

    # Si la salida viene en formato estructurado (dict)
    message_text = narrative_output.get("text", "")
    tone = narrative_output.get("tone", None)
    emotion = narrative_output.get("emotion", None)
    scene_type = narrative_output.get("scene_type", None)
    outcome = narrative_output.get("outcome", None)

    # Armar los bloques si existen descripciones adicionales
    blocks_data = narrative_output.get("blocks", [])
    blocks = []

    if isinstance(blocks_data, list):
        for b in blocks_data:
            if isinstance(b, dict):
                blocks.append(MessageBlock(**b))
            elif isinstance(b, str):
                blocks.append(MessageBlock(content=b))

    # Crear mensaje final
    msg = TelegramMessage(
        text=message_text,
        tone=tone,
        emotion=emotion,
        scene_type=scene_type,
        outcome=outcome,
        blocks=blocks
    )

    # Registro para depuración
    logger.info("[Renderer] Mensaje final renderizado:")
    logger.info(f"{msg.text}\n")
    if tone or emotion or outcome:
        logger.info(f"🧭 Tipo de próxima escena: *{scene_type or 'N/A'}*")
        logger.info(f"🎭 Tono: *{tone or 'neutral'}*")
        logger.info(f"💫 Emoción dominante: *{emotion or 'neutral'}*")
        logger.info(f"⚖️ Resultado: *{outcome or 'mixed'}*")

    return msg
