# ==========================================================
# 📘 SAM – Dynamic World Events: Consequence Resolver
# Fase 7.3 – Incluye integración con FactionManager
# ==========================================================
import logging
from core.world_events.faction_manager import FactionManager

logger = logging.getLogger(__name__)

class ConsequenceResolver:
    """
    Aplica las consecuencias de un evento dinámico al estado del mundo,
    las emociones globales, el grupo del jugador y las facciones activas.
    """

    def __init__(self):
        # Módulo de facciones: se carga una única instancia
        self.faction_manager = FactionManager()

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================
    def apply_consequences(self, event: dict, world_state: dict, emotional_state: dict, party_state: dict):
        """
        Aplica los efectos del evento al mundo, emociones, grupo y facciones.
        Devuelve las estructuras actualizadas.
        """
        if not event or event.get("event_id") is None:
            logger.info("[ConsequenceResolver] No hay evento para aplicar consecuencias.")
            return world_state, emotional_state, party_state

        cons = event.get("consequence", {})
        logger.info(f"[ConsequenceResolver] Aplicando consecuencias del evento: {event.get('title')}")

        # --- Efectos sobre el mundo ---
        world_state = self._update_world(world_state, cons.get("world", {}))

        # --- Efectos emocionales ---
        emotional_state = self._update_emotions(emotional_state, cons.get("emotion", {}))

        # --- Efectos sobre el grupo ---
        party_state = self._update_party(party_state, cons.get("party", {}))

        # --- Efectos sobre las facciones ---
        try:
            self.faction_manager.apply_event_effect(event)
        except Exception as e:
            logger.error(f"[ConsequenceResolver] Error al aplicar efecto de facciones: {e}")

        return world_state, emotional_state, party_state

    # ==========================================================
    # SUBMÓDULOS DE ACTUALIZACIÓN
    # ==========================================================
    def _update_world(self, world_state, changes):
        """
        Actualiza el estado del mundo con los cambios indicados en 'world'.
        Admite valores numéricos o cadenas tipo '+1'.
        """
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
        """
        Modifica la escala emocional global según las variaciones indicadas.
        Admite valores '+0.2' o numéricos directos.
        """
        for emotion, delta in changes.items():
            try:
                change_value = float(delta) if not isinstance(delta, str) else float(delta.replace("+", ""))
                emotional_state[emotion] = round(emotional_state.get(emotion, 0.0) + change_value, 2)
            except Exception:
                logger.warning(f"[ConsequenceResolver] Valor emocional inválido para '{emotion}': {delta}")
        return emotional_state

    def _update_party(self, party_state, changes):
        """
        Aplica cambios al grupo del jugador (moral, recursos, XP, etc.).
        """
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
