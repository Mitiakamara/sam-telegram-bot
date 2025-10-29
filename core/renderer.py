import logging
from core.models.telegram_msg import TelegramMessage

logger = logging.getLogger(__name__)

# ================================================================
# 🎨 RENDERER – Adaptador de salida narrativa para Telegram
# ================================================================

def render(scene_description):
    """
    Convierte la salida narrativa o estructurada en un mensaje TelegramMessage.
    Acepta tanto strings como diccionarios estructurados.
    """

    # 1️⃣ Manejar dict o string
    if isinstance(scene_description, dict):
        text = scene_description.get("description", "")
        next_type = scene_description.get("next_scene_type", "")
        tone = scene_description.get("tone", "")
        emotion = scene_description.get("dominant_emotion", "")
        outcome = scene_description.get("outcome", "")
    else:
        text = str(scene_description)
        next_type = tone = emotion = outcome = ""

    # 2️⃣ Asegurar que sea texto limpio
    text = text.strip() if isinstance(text, str) else str(text)

    # 3️⃣ Construir mensaje Telegram
    message_text = f"{text}\n\n"
    if next_type:
        message_text += f"🧭 Tipo de próxima escena: *{next_type}*\n"
    if tone:
        message_text += f"🎭 Tono: *{tone}*\n"
    if emotion:
        message_text += f"💫 Emoción dominante: *{emotion}*\n"
    if outcome:
        message_text += f"⚖️ Resultado: *{outcome}*"

    logger.info(f"[Renderer] Mensaje final renderizado:\n{message_text}")

    return TelegramMessage(text=message_text)
