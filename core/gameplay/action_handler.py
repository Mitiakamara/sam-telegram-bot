# sam-telegram-bot/core/gameplay/action_handler.py
"""
Módulo central de enrutamiento de acciones de jugador.
Decide dinámicamente qué sistema debe procesar el input:
- Character Builder
- Tiradas automáticas (roll_resolver)
- Narrativa libre (Orchestrator)
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from core.character_builder.builder import handle_response, builder_state
from core.gameplay.roll_resolver import resolve_action
from core.narrator import SAMNarrator

logger = logging.getLogger("SAM.ActionHandler")


# ================================================================
# 🔄 FUNCIÓN PRINCIPAL DE ENRUTAMIENTO
# ================================================================
async def handle_player_input(update: Update, context: ContextTypes.DEFAULT_TYPE, orchestrator, api_request, maybe_reply_mood):
    """
    Decide si el texto pertenece al flujo de creación de personaje,
    a una acción con tirada, o a la narrativa general.
    """
    try:
        user_id = update.effective_user.id
        player_name = update.effective_user.first_name
        text = update.message.text.strip()

        # 1️⃣ Builder activo → delegar
        if user_id in builder_state:
            processed = await handle_response(update, context)
            if processed:
                return  # detener flujo (no continuar al narrador)

        # 2️⃣ Intentar resolver acción (tirada + escena)
        result_msg = await resolve_action(update, player_name, text, orchestrator)
        if result_msg:
            await update.message.reply_markdown(result_msg)
            return

        # 3️⃣ Comandos de historia: continuar, recap, etc.
        if text.lower() in ["continuar", "seguir", "avanzar"]:
            msg = await orchestrator.handle_continue(user_id)
            await update.message.reply_text(msg, parse_mode="Markdown")
            await maybe_reply_mood(update, "")
            return

        # 4️⃣ Acción libre → modo narrativo
        result = await api_request("POST", "/game/action", {"player": player_name, "action": text, "mode": "action"})
        narration = result.get("result", "S.A.M. no entiende lo que intentas hacer.")
        await update.message.reply_text(narration)

        # 5️⃣ Ajustar emoción global según mensaje
        emo = detect_player_emotion(text)
        if emo:
            orchestrator.apply_feedback(*emo)
            await maybe_reply_mood(update, "")

    except Exception as e:
        logger.error(f"Error en handle_player_input: {e}")
        await update.message.reply_text("⚠️ Ocurrió un error procesando tu acción. Intenta nuevamente.")


# ================================================================
# 💬 DETECCIÓN SIMPLE DE EMOCIONES DEL JUGADOR
# ================================================================
def detect_player_emotion(text: str):
    """Heurística ligera de emociones en texto libre."""
    t = text.lower()
    if any(w in t for w in ["aburrido", "meh", "soso"]):
        return ("bored", -0.2)
    if any(w in t for w in ["wow", "épico", "genial", "impresionante"]):
        return ("excited", +0.3)
    if any(w in t for w in ["miedo", "tenso", "asustado"]):
        return ("fear", +0.2)
    if any(w in t for w in ["triste", "melancólico", "deprimido"]):
        return ("sad", -0.1)
    return None
