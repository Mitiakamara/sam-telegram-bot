import re
import unicodedata
from uuid import uuid4
from core.models.intent import Intent, IntentType
from core.models.base import ErrorModel


def normalize_text(text: str) -> str:
    """Normaliza texto eliminando tildes, puntuación y dejando minúsculas."""
    text = text.lower()
    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


async def parse_intent(text: str, action_id):
    """
    Analiza el texto del jugador y determina el intent principal.
    Incluye variantes con tildes y sinónimos comunes.
    """
    try:
        lower = normalize_text(text)

        # --- Hechizos / Conjuros ---
        if any(word in lower for word in ["lanzo", "lanzar", "conjuro", "invoco", "hechizo", "magia", "conjurar"]):
            intent = IntentType.cast_spell
            requires_srd = True

        # --- Investigación / Percepción ---
        elif any(word in lower for word in ["investigo", "examino", "busco", "reviso", "observo", "miro", "analizo"]):
            intent = IntentType.investigate
            requires_srd = False

        # --- Interacción social ---
        elif any(word in lower for word in ["hablo", "digo", "pregunto", "saludo", "charlo", "converso", "grito"]):
            intent = IntentType.talk
            requires_srd = False

        # --- Ataques / Combate ---
        elif any(word in lower for word in ["ataco", "golpeo", "disparo", "arremeto", "pego", "apuñalo", "blando"]):
            intent = IntentType.attack
            requires_srd = True

        # --- Movimiento ---
        elif any(word in lower for word in ["camino", "avanzo", "corro", "muevo", "retrocedo", "me acerco"]):
            intent = IntentType.move
            requires_srd = False

        # --- Interacción / Uso ---
        elif any(word in lower for word in ["uso", "tomo", "abro", "cierro", "activo", "agarro", "manipulo"]):
            intent = IntentType.interact
            requires_srd = False

        # --- Fallback ---
        else:
            intent = IntentType.interact
            requires_srd = False

        # --- Extracción de entidades básicas ---
        entities = {}
        # Hechizos conocidos (Sleep / Dormir / Luz / Light)
        if intent == IntentType.cast_spell:
            if "dormir" in lower or "sleep" in lower:
                entities["spell_name"] = "Sleep"
            elif "luz" in lower or "light" in lower:
                entities["spell_name"] = "Light"

        if intent == IntentType.attack and "arco" in lower:
            entities["attack_weapon"] = "arco"

        if intent == IntentType.investigate and "puerta" in lower:
            entities["target"] = "puerta"

        return Intent(
            action_id=action_id,
            intent=intent,
            confidence=0.9,
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
