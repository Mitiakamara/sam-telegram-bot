from uuid import uuid4
from core.models.telegram_msg import TelegramMessage, MessageBlock


def escape_markdown_v2(text: str) -> str:
    """
    Escapa caracteres especiales de MarkdownV2.
    (Evita errores de formato en Telegram)
    """
    if not text:
        return text
    escape_chars = "_*[]()~`>#+-=|{}.!"
    for ch in escape_chars:
        text = text.replace(ch, f"\\{ch}")
    return text


def render(resolution, intent, action):
    """
    Genera el mensaje final Telegram-ready (MarkdownV2).
    Combina acción, resolución y resultados de tiradas.
    """
    pc_name = action.scene_context.party[0]["name"]
    intent_type = str(intent.intent)

    # --- Plantillas básicas según intent ---
    if intent_type == "cast_spell":
        spell_name = intent.entities.get("spell_name", "hechizo")
        roll_sum = None
        for s in resolution.steps:
            if s.result_total:
                roll_sum = s.result_total
                break
        text = (
            f"*{pc_name}* pronuncia un encantamiento y lanza *{spell_name}*.\n"
            f"✨ Una onda mágica se expande por la zona.\n"
        )
        if roll_sum:
            text += f"_Energía total:_ `{roll_sum}`"
        rolls_inline = [f"{r['expr']} → {r['total']}" for r in resolution.dice_log]

    elif intent_type == "skill_check":
        total = resolution.dice_log[0]["total"] if resolution.dice_log else "—"
        text = f"*{pc_name}* intenta una acción cuidadosa.\n🎲 Resultado: `{total}`"
        rolls_inline = [f"{r['expr']} → {r['total']}" for r in resolution.dice_log]

    elif intent_type == "talk":
        text = f"*{pc_name}* entabla conversación con un NPC.\n"
        text += "_La charla fluye con naturalidad._"
        rolls_inline = []

    elif intent_type == "investigate":
        text = f"*{pc_name}* examina el entorno con atención.\n"
        text += "👁️ Encuentra rastros sutiles en la piedra."
        rolls_inline = []

    elif intent_type == "attack":
        text = f"⚔️ *{pc_name}* ataca con determinación.\n"
        if resolution.outcome == "success":
            text += "✅ El golpe impacta de lleno."
        elif resolution.outcome == "failure":
            text += "❌ El ataque falla por poco."
        else:
            text += "⚖️ El resultado es incierto."
        rolls_inline = [f"{r['expr']} → {r['total']}" for r in resolution.dice_log]

    else:
        text = f"*{pc_name}* actúa instintivamente."
        rolls_inline = []

    # --- Escapar MarkdownV2 ---
    safe_text = escape_markdown_v2(text)

    # --- Crear mensaje Telegram-ready ---
    msg = TelegramMessage(
        message_id=uuid4(),
        action_id=action.action_id,
        lang=action.lang,
        blocks=[MessageBlock(text=safe_text, rolls_inline=rolls_inline)],
        mode="MarkdownV2",
        safe_len=min(len(safe_text), 1200),
    )

    return msg
