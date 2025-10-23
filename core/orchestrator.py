import asyncio
from .nlp_intent import parse_intent
from .srd_client import lookup
from .rules_engine import resolve
from .renderer import render


async def run_pipeline(action):
    """
    Orquesta el flujo:
    1. NLP → Intent
    2. (Opcional) SRD Lookup
    3. Rules Engine (tiradas y resolución)
    4. Renderer (narrativa Telegram)
    """
    # 1️⃣ Interpretar la acción libre
    intent = await parse_intent(action.text, action.action_id)

    # 2️⃣ Consultar SRD si aplica
    srd = None
    if intent.requires_srd:
        try:
            q = intent.entities.get("spell_name", "Sleep")
            srd = await lookup("spell", q, action.action_id)
        except Exception as e:
            print(f"[SRD Lookup Error] {e}")

    # 3️⃣ Resolver reglas
    resolution = await resolve(intent, srd, action.scene_context)

    # 4️⃣ Generar mensaje Telegram-ready
    message = render(resolution, intent, action)
    return message
