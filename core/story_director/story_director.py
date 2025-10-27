# sam-telegram-bot/core/story_director/story_director.py
"""
StoryDirector
-------------
Motor de decisiones narrativas adaptativas con:
- Memoria dramática persistente (MemoryManager)
- Reforzamiento temático adaptativo
- Voz de narrador emergente (NarratorPersona)

S.A.M. ya no es un narrador neutro: ahora adopta un estilo propio
según las emociones, los temas recurrentes y la progresión dramática
de la campaña.
"""

import random
import json
from datetime import datetime

from core.scene_manager.tone_adapter import ToneAdapter
from core.services.state_service import StateService
from core.story_director.theme_tracker import ThemeTracker
from core.story_director.dramatic_curve import DramaticCurve
from core.story_director.memory_manager import MemoryManager
from core.story_director.narrator_persona import NarratorPersona


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
        """Carga la base de nodos narrativos desde JSON."""
        try:
            with open("core/story_director/narrative_nodes.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    # ==========================================================
    # 🔹 ANÁLISIS DE CONTEXTO
    # ==========================================================
    def analyze_context(self):
        """
        Analiza el estado actual del juego:
        - Nivel emocional
        - Tema detectado
        - Etapa de la curva dramática
        """
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
        Elige el siguiente nodo narrativo basándose en emoción, tema y curva dramática.
        Integra la memoria para reforzar o romper temas recurrentes.
        """
        emotion_level, theme, stage = self.analyze_context()
        recurrent_theme = self.memory_manager.get_recurrent_theme()
        avg_emotion = self.memory_manager.get_average_emotion()

        # Filtrar nodos compatibles
        candidates = [
            n for n in self.narrative_nodes
            if stage in n.get("stages", [])
            and emotion_level in n.get("emotion_range", [])
        ]

        if not candidates:
            return None

        # Reforzamiento temático adaptativo
        weighted_nodes = []
        for node in candidates:
            weight = 1.0
            node_theme = node.get("theme")
            tone = node.get("tone", "neutral")

            # 🔹 Reforzar temas dominantes
            if recurrent_theme and node_theme == recurrent_theme:
                weight *= 2.0

            # 🔹 Equilibrar emoción global
            if avg_emotion >= 4 and tone == "dark":
                weight *= 0.8  # evita excesiva tensión
            elif avg_emotion <= 2 and tone == "hopeful":
                weight *= 1.5  # refuerza alivio o esperanza

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
    # 🔹 GENERACIÓN DE TRANSICIÓN NARRATIVA
    # ==========================================================
    def generate_transition(self):
        """
        Crea una transición narrativa adaptativa hacia el siguiente nodo.
        Ajusta tono y emoción, registra el evento en la memoria dramática
        y aplica la voz emergente del narrador.
        """
        node = self.select_next_node()

        if not node:
            return "El silencio del mundo es momentáneo; el destino aún no ha decidido su próximo paso."

        # Adaptar descripción al nivel emocional
        description = self.tone_adapter.adapt_description(
            node["description"],
            emotion_intensity=node.get("default_emotion", 3)
        )

        # Registrar transición en el estado general
        transition = {
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": node.get("id", "unknown"),
            "scene_transition": node.get("type", "narrative"),
            "description": description,
            "theme": node.get("theme", "indefinido")
        }
        self.state_service.update_story_flow(transition)

        # Registrar en memoria dramática
        try:
            self.memory_manager.record_event(
                description=description,
                theme=node.get("theme", "indefinido"),
                emotion_level=node.get("default_emotion", 3),
                stage=self.dramatic_curve.get_stage()
            )
        except Exception as e:
            print(f"[WARN] Error registrando evento en memoria: {e}")

        # Aplicar estilo narrativo emergente
        try:
            persona = NarratorPersona()
            description = persona.apply_persona(description)
        except Exception as e:
            print(f"[WARN] Error aplicando estilo narrativo: {e}")

        return description
