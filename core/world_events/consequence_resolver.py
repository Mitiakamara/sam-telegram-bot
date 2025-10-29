# ==========================================================
# 📘 SAM – Consequence Resolver (Modo Campaña Pre-Creada)
# ==========================================================
import logging

logger = logging.getLogger(__name__)

class ConsequenceResolver:
    """
    Aplica consecuencias narrativas y emocionales sin modificar facciones ni economía.
    Optimizado para campañas pre-creadas.
    """

    def apply_consequences(self, event: dict, world_state: dict, emotional_state: dict, party_state: dict):
        if not event or event.get("event_id") is None:
            logger.info("[ConsequenceResolver] No hay evento para aplicar consecuencias.")
            return world_state, emotional_state, party_state

        cons = event.get("consequence", {})
        logger.info(f"[ConsequenceResolver] Aplicando consecuencias del evento: {event.get('title')}")

        world_state = self._update_world(world_state, cons.get("world", {}))
        emotional_state = self._update_emotions(emotional_state, cons.get("emotion", {}))
        party_state = self._update_party(party_state, cons.get("party", {}))

        return world_state, emotional_state, party_state

    def _update_world(self, world_state, changes):
        for key, value in changes.items():
            if isinstance(value, (int, float)):
                world_state[key] = world_state.get(key, 0) + value
            elif isinstance(value, str) and value.startswith("+"):
                try:
                    world_state[key] = world_state.get(key, 0) + float(value[1:])
                except ValueError:
                    world_state[key] = value
            else:
                world_state[key] = value
        return world_state

    def _update_emotions(self, emotional_state, changes):
        for emotion, delta in changes.items():
            try:
                change_value = float(delta) if not isinstance(delta, str) else float(delta.replace("+", ""))
                emotional_state[emotion] = round(emotional_state.get(emotion, 0.0) + change_value, 2)
            except Exception:
                pass
        return emotional_state

    def _update_party(self, party_state, changes):
        for key, value in changes.items():
            if isinstance(value, (int, float)):
                party_state[key] = party_state.get(key, 0) + value
            elif isinstance(value, str) and value.startswith("+"):
                try:
                    party_state[key] = party_state.get(key, 0) + float(value[1:])
                except ValueError:
                    party_state[key] = value
            else:
                party_state[key] = value
        return party_state
