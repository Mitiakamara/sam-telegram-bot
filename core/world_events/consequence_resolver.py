# ==========================================================
# 📘 SAM – Dynamic World Events: Consequence Resolver (Fase 7.0)
# ==========================================================

import logging

logger = logging.getLogger(__name__)

class ConsequenceResolver:
    def __init__(self):
        pass

    def apply_consequences(self, event: dict, world_state: dict, emotional_state: dict, party_state: dict):
        """
        Aplica los efectos del evento al mundo, emociones y estado del grupo.
        Devuelve las estructuras actualizadas.
        """
        if not event or event.get("event_id") is None:
            logger.info("No hay evento para aplicar consecuencias.")
            return world_state, emotional_state, party_state

        cons = event.get("consequence", {})
        logger.info(f"Aplicando consecuencias del evento: {event.get('title')}")

        # --- Efectos en el mundo ---
        world_state = self._update_world(world_state, cons.get("world", {}))

        # --- Efectos emocionales ---
        emotional_state = self._update_emotions(emotional_state, cons.get("emotion", {}))

        # --- Efectos en el grupo (opcional) ---
        party_state = self._update_party(party_state, cons.get("party", {}))

        return world_state, emotional_state, party_state

    def _update_world(self, world_state, changes):
        for key, value in changes.items():
            if isinstance(value, (int, float)):
                world_state[key] = world_state.get(key, 0) + value
            elif isinstance(value, str) and value.startswith("+"):
                # incremento numérico en cadena: "+1"
                try:
                    world_state[key] = world_state.get(key, 0) + float(value[1:])
                except ValueError:
                    world_state[key] = value
            else:
                world_state[key] = value
        return world_state

    def _update_emotions(self, emotional_state, changes):
        for emotion, delta in changes.items():
            # Permitir formatos "+0.2" o valores numéricos directos
            change_value = float(delta) if not isinstance(delta, str) else float(delta.replace("+", ""))
            emotional_state[emotion] = round(emotional_state.get(emotion, 0.0) + change_value, 2)
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
