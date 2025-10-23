import random
from uuid import uuid4
from core.models.telegram_msg import TelegramMessage, MessageBlock


def escape_markdown_v2(text: str) -> str:
    """Escapa caracteres especiales de MarkdownV2."""
    if not text:
        return text
    escape_chars = "_*[]()~`>#+-=|{}.!"
    for ch in escape_chars:
        text = text.replace(ch, f"\\{ch}")
    return text


def render(resolution, intent, action):
    """
    Genera el mensaje final Telegram-ready con narrativa dinámica.
    """
    pc_name = action.scene_context.party[0]["name"]
    intent_type = str(intent.intent)
    outcome = str(resolution.outcome)

    # 🎭 Plantillas de frases según tipo de acción
    phrases = {
        "cast_spell": [
            f"*{pc_name}* murmura palabras arcanas y libera un destello de energía mágica.",
            f"✨ *{pc_name}* concentra su poder interior y lanza un hechizo brillante.",
            f"*{pc_name}* alza la mano y el aire vibra con energía arcana.",
        ],
        "attack": [
            f"⚔️ *{pc_name}* ataca con determinación.",
            f"💥 *{pc_name}* se lanza al combate, decidido a golpear.",
            f"*{pc_name}* blande su arma con fuerza y precisión.",
        ],
        "investigate": [
            f"🔍 *{pc_name}* examina con atención cada detalle del entorno.",
            f"👁️ *{pc_name}* observa cuidadosamente buscando pistas ocultas.",
            f"*{pc_name}* recorre el lugar con la mirada, en busca de algo inusual.",
        ],
        "talk": [
            f"💬 *{pc_name}* inicia una conversación con un tono curioso.",
            f"*{pc_name}* se dirige con calma al interlocutor, buscando respuestas.",
            f"🗣️ *{pc_name}* habla con voz firme, intentando obtener información.",
        ],
        "move": [
            f"🚶 *{pc_name}* avanza con pasos cautelosos.",
            f"🏃 *{pc_name}* se mueve rápidamente por el terreno.",
            f"*{pc_name}* cambia de posición evaluando el entorno.",
        ],
        "interact": [
            f"✋ *{pc_name}* actúa con decisión.",
            f"🧩 *{pc_name}* interactúa con su entorno de forma instintiva.",
            f"*{pc_name}* realiza una acción rápida e improvisada.",
        ],
    }

    # 🧠 Frases según resultado
    outcomes = {
        "success": [
            "✅ El resultado es favorable.",
            "🌟 ¡Éxito rotundo!",
            "👏 Todo sale como esperaba.",
        ],
        "failure": [
            "❌ El intento falla por poco.",
            "💀 Algo sale mal en el último momento.",
            "😓 No logra lo que pretendía.",
        ],
        "mixed": [
            "⚖️ Logra parte de su objetivo, pero con consecuencias.",
            "🤔 No está claro si fue buena idea.",
            "💫 El resultado es incierto.",
        ],
    }

    # Selecciona frases aleatorias
    base_text = random.choice(phrases.get(intent_type, phrases["interact"]))
    outcome_text = random.choice(outcomes.get(outcome, [""]))

    # 🧾 Tiradas
    rolls_inline = [f"{r['expr']} → {r['total']}" for r in resolution.dice_log] if resolution.dice_log else []

    # Arma el texto final
    text = f"{base_text}\n{outcome_text}"
    if rolls_inline:
        rolls_summary = "🎲 " + ", ".join(rolls_inline)
        text += f"\n{rolls_summary}"

    # Escapa Markdown y crea bloque Telegram
    safe_text = escape_markdown_v2(text)
    msg = TelegramMessage(
        message_id=uuid4(),
        action_id=action.action_id,
        lang=action.lang,
        blocks=[MessageBlock(text=safe_text, rolls_inline=rolls_inline)],
        mode="MarkdownV2",
        safe_len=min(len(safe_text), 1200),
    )

    return msg
