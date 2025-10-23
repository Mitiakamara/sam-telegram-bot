from uuid import uuid4
from core.models.intent import Intent, IntentType
from core.models.base import ErrorModel


async def parse_intent(text: str, action_id):
    """
    Analiza el texto del jugador para determinar la intención (Intent).
    Es un NLP ligero basado en reglas, sin dependencias externas.
    """
    try:
        lower = text.lower().strip()

        # --- Clasificación básica ---
        if any(word in lower for word in ["lanzo", "conjuro", "invoco", "hechizo"]):
            intent = IntentType.cast_spell
            requires_srd = True

        elif any(word in lower for word in ["investigo", "busco", "examino", "observo", "reviso"]):
            intent = IntentType.investigate
            requires_srd = False

        elif any(word in lower for word in ["hablo", "digo", "pregunto", "saludo", "charlo"]):
            intent = IntentType.talk
            requires_srd = False

        elif any(word in lower for word in ["golpeo", "ataco", "disparo", "apunto", "arremeto"]):
            intent = IntentType.attack
            requires_srd = True

        elif any(word in lower for word in ["camino", "avanzo", "corro", "me muevo", "retrocedo"]):
            intent = IntentType.move
            requires_srd = False

        elif any(word in lower for word in ["uso", "tomo", "activo", "abro", "cierro", "manipulo"]):
            intent = IntentType.interact
            requires_srd = False

        else:
            # fallback genérico
            intent = IntentType.interact
            requires_srd = False

        # --- Extracción de entidades simples ---
        entities = {}

        # Detectar nombre de hechizo básico (ejemplo: "lanzo dormir")
        if intent == IntentType.cast_spell:
            palabras = lower.split()
            for palabra in palabras:
                if palabra.capitalize() in ["Sleep", "Dormir", "Escudo", "Shield", "Luz", "Luz"]:
                    entities["spell_name"] = palabra.capitalize()
                    break

        # Detectar tipo de habilidad o interacción
        if intent == IntentType.investigate and "puerta" in lower:
            entities["target"] = "puerta"

        if intent == IntentType.attack and "arco" in lower:
            entities["attack_weapon"] = "arco"

        return Intent(
            action_id=action_id,
            intent=intent,
            confidence=0.85,
            requires_srd=requires_srd,
            entities=entities,
        )

    except Exception as e:
        return Intent(
            action_id=action_id,
            intent=IntentType.interact,
            confidence=0.1,
            requires_srd=False,
            errors=[ErrorModel(code="INTENT_FAIL", message=str(e))],
        )
