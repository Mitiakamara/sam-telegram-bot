# sam-telegram-bot/core/story_director/story_director.py
"""
StoryDirector
-------------
Motor de decisiones narrativas adaptativas con memoria dramática y
reforzamiento temático.

Ahora S.A.M. puede detectar los temas recurrentes de la historia
y decidir si desea reforzarlos o romperlos para mantener la tensión narrativa.
"""

import random
import json
from datetime import datetime

from core.scene_manager.tone_adapter import ToneAdapter
from core.services.state_service import StateService
from core.story_director.theme_tracker import ThemeTracker
from core.story_director.dramatic_curve import DramaticCurve
from core.story_director.memory_manager import MemoryManager


class StoryDirector:
    def __init__(self, scene_manager, tone_adapter: ToneAdapter):
        self.scene_manager = scene_manager
        self.tone_adapter = tone_adapter
        self.state_service = StateService()
        self.theme_tracker = ThemeTracker()
        self.dramatic_curve = DramaticCurve()
        self.memory_manager = MemoryManager()
        self.narrative_nodes = self._load_narrative_nodes()

    # ==========================================================
    # 🔹 CARGA DE NODOS NARRATIVOS
    # ==========================================================
    def _load_narrative_nodes(self):
        try:
            with open("core/story_director/narrative_nodes.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    # ==========================================================
    # 🔹 ANÁLISIS DE CONTEXTO
    # ==========================================================
    def analyze_context(self):
        game_state = self.state_service.load_state()
        emotion_level = game_state.get("emotion_intensity", 3)
        current_theme = self.theme_tracker.detect_theme(game_state)
        curve_stage = self.dramatic_curve.get_stage()
        return emotion_level, current_theme, curve_stage

    # ==========================================================
    # 🔹 SELECCIÓN DE NODO SIGUIENTE (con reforzamiento temático)
    # ==========================================================
    def select_next_node(self):
        """
        Elige el siguiente nodo narrativo basado en emoción, tema y curva,
        con influencia del tema recurrente guardado en memoria.
        """
        emotion_level, theme, stage = self.analyze_context()
        recurrent_theme = self.memory_manager.get_recurrent_theme()
        avg_emotion = self.memory_manager.get_average_emotion()

        # Filtrar por etapa dramática y emoción
        candidates = [
            n for n in self.narrative_nodes
            if stage in n.get("stages", [])
            and emotion_level in n.get("emotion_range", [])
        ]

        if not candidates:
            return None

        # 🔹 Reforzamiento temático adaptativo
        weighted_nodes = []
        for node in candidates:
            weight = 1.0
            node_theme = node.get("theme")

            # Si el tema coincide con el recurrente → mayor peso (reforzar)
            if recurrent_theme and node_theme == recurrent_theme:
                weight *= 2.0

            # Si el tema es opuesto (según curva emocional) → menor o mayor peso
            if avg_emotion >= 4 and node.get("tone") == "dark":
                weight *= 0.8  # Evitar excesiva tensión
            elif avg_emotion <= 2 and node.get("tone") == "hopeful":
                weight *= 1.5  # Reforzar alivio

            weighted_nodes.append((node, weight))

        # Selección ponderada
        total_weight = sum(w for _, w in weighted_nodes)
        rand = random.uniform(0, total_weight)
        cumulative = 0
        for node, weight in weighted_nodes:
            cumulative += weight
            if rand <= cumulative:
                return node

        return random.choice(candidates)

    # ==========================================================
    # 🔹 GENERACIÓN DE TRANSICIÓN NARRATIVA (con registro en memoria)
    # ==========================================================
    def generate_transition(self):
        node = self.select_next_node()

        if not node:
            return "El silencio del mundo es momentáneo; el destino aún no ha decidido su próximo paso."

        # Adaptar descripción según emoción
        description = self.tone_adapter.adapt_description(
            node["description"], emotion_intensity=node["default_emotion"]
        )

        transition = {
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": node["id"],
            "scene_transition": node["type"],
            "description": description,
            "theme": node["theme"]
        }

        self.state_service.update_story_flow(transition)

        # Registrar en memoria narrativa
        try:
            self.memory_manager.record_event(
                description=description,
                theme=node["theme"],
                emotion_level=node["default_emotion"],
                stage=self.dramatic_curve.get_stage()
            )
        except Exception as e:
            print(f"[WARN] Error registrando evento en memoria: {e}")

        return description
