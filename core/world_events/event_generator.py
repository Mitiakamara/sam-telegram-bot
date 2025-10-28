# ==========================================================
# 📘 SAM – Dynamic World Events: Event Generator (Fase 7.0)
# ==========================================================

import random
import json
from pathlib import Path

class EventGenerator:
    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.event_registry = self._load_registry()

    def _load_registry(self):
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Event registry not found: {self.registry_path}")
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_event(self, world_state: dict, emotional_state: dict, party_state: dict) -> dict:
        """
        Genera un evento dinámico basado en el estado actual del mundo y la emoción global.
        """
        possible_events = self._filter_events(world_state, emotional_state, party_state)
        if not possible_events:
            return {"event_id": None, "type": "none", "description": "Nada inusual sucede en este momento."}

        selected = random.choice(possible_events)
        event = self._adapt_event(selected, world_state, emotional_state, party_state)
        return event

    def _filter_events(self, world_state, emotional_state, party_state):
        """
        Filtra el registro según condiciones de entorno, moral, clima y nivel.
        """
        candidates = []
        for e in self.event_registry.get("events", []):
            if self._match_conditions(e.get("conditions", {}), world_state, emotional_state, party_state):
                candidates.append(e)
        return candidates

    def _match_conditions(self, conditions, world_state, emotional_state, party_state):
        # Clima, emoción global y nivel promedio del grupo
        climate = world_state.get("environment", {}).get("weather", "")
        tone = emotional_state.get("tone", "")
        avg_level = party_state.get("average_level", 1)

        # Validaciones básicas
        if "weather" in conditions and climate not in conditions["weather"]:
            return False
        if "tone" in conditions and tone not in conditions["tone"]:
            return False
        if "min_level" in conditions and avg_level < conditions["min_level"]:
            return False
        if "max_level" in conditions and avg_level > conditions["max_level"]:
            return False
        return True

    def _adapt_event(self, event_template, world_state, emotional_state, party_state):
        """
        Inserta contexto dinámico dentro de la descripción del evento.
        """
        description = event_template.get("description", "")
        location = world_state.get("current_location", "un lugar desconocido")
        tone = emotional_state.get("tone", "neutral")
        morale = emotional_state.get("morale", "estable")

        # Personalizar texto
        text = description.replace("{location}", location)
        text = text.replace("{tone}", tone)
        text = text.replace("{morale}", morale)

        return {
            "event_id": event_template.get("id"),
            "type": event_template.get("type"),
            "title": event_template.get("title"),
            "description": text,
            "consequence": event_template.get("consequence", {}),
        }
