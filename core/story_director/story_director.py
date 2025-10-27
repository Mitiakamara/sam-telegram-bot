# sam-telegram-bot/core/story_director/story_director.py
"""
StoryDirector
-------------
Motor de decisiones narrativas adaptativas.

Ahora incluye integración con MemoryManager, lo que permite registrar
cada transición narrativa para que S.A.M. recuerde los eventos, temas
y emociones predominantes de la historia.
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
    """
    Motor de decisiones narrativas adaptativas.
    Supervisa la progresión emocional y temática del juego
    para decidir el siguiente tipo de evento o escena.
    """

    def __init__(self, scene_manager, tone_adapter: ToneAdapter):
        """
        scene_manager: referencia dinámica al SceneManager actual.
        tone_adapter: responsable de adaptar el tono emocional del texto.
        """
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
    # 🔹 ANÁLISIS DE CONTEXTO ACTUAL
    # ==========================================================
    def analyze_context(self):
        """
        Analiza el estado actual de la partida:
        - Emoción activa
        - Tema predominante
        - Etapa dramática
        """
        game_state = self.state_service.load_state()
        emotion_level = game_state.get("emotion_intensity", 3)
        current_theme = self.theme_tracker.detect_theme(game_state)
        curve_stage = self.dramatic_curve.get_stage()
        return emotion_level, current_theme, curve_stage

    # ==========================================================
    # 🔹 SELECCIÓN DE NODO SIGUIENTE
    # ==========================================================
    def select_next_node(self):
        """
        Elige el siguiente evento narrativo basado en emoción, tema y curva.
        """
        emotion_level, theme, stage = self.analyze_context()
        candidates = [
            n for n in self.narrative_nodes
            if stage in n.get("stages", [])
            and emotion_level in n.get("emotion_range", [])
        ]
        if not candidates:
            return None
        return random.choice(candidates)

    # ==========================================================
    # 🔹 GENERACIÓN DE TRANSICIÓN NARRATIVA
    # ==========================================================
    def generate_transition(self):
        """
        Crea una transición narrativa hacia el siguiente nodo.
        Integra emoción, tono y coherencia con la historia,
        y registra el evento en la memoria dramática.
        """
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

        # Registrar en el flujo general del estado
        self.state_service.update_story_flow(transition)

        # 🔹 Registrar evento en memoria dramática
        try:
            self.memory_manager.record_event(
                description=description,
                theme=node["theme"],
                emotion_level=node["default_emotion"],
                stage=self.dramatic_curve.get_stage()
            )
        except Exception as e:
            # No interrumpir el flujo narrativo si hay error al guardar
            print(f"[WARN] Error registrando evento en memoria: {e}")

        return description
