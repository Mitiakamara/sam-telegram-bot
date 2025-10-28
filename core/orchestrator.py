# ==========================================================
# 🎭 SAM Orchestrator – Fase 7.0: Dynamic World Events & Consequences
# ==========================================================
import logging
from datetime import datetime

# --- Core modules ---
from core.scene_manager.scene_manager import SceneManager
from core.story_director.story_director import StoryDirector
from core.emotion.emotional_tracker import EmotionalTracker
from core.renderer import render

# --- Dynamic world event system ---
from core.world_events.event_generator import EventGenerator
from core.world_events.consequence_resolver import ConsequenceResolver

# ==========================================================
# CONFIGURACIÓN BÁSICA
# ==========================================================
logger = logging.getLogger(__name__)
EVENT_REGISTRY_PATH = "core/world_events/event_registry.json"


class Orchestrator:
    """
    Orquestador principal de SAM: coordina escenas, emociones,
    decisiones narrativas y ahora también eventos dinámicos del mundo.
    """

    def __init__(self):
        # Subsistemas
        self.scene_manager = SceneManager()
        self.story_director = StoryDirector()
        self.emotional_tracker = EmotionalTracker()

        # Sistema de eventos dinámicos
        self.event_generator = EventGenerator(EVENT_REGISTRY_PATH)
        self.consequence_resolver = ConsequenceResolver()

        # Estados de sesión
        self.world_state = {
            "time": "morning",
            "environment": {"weather": "templado", "terrain": "bosque"},
            "factions": {},
            "reputation": 0,
            "danger_zone": False,
            "current_location": "colinas de Faerûn"
        }
        self.emotional_state = {
            "tone": "neutral",
            "morale": "estable",
            "fear": 0.0,
            "hope": 0.0,
            "tension": 0.0
        }
        self.party_state = {
            "average_level": 3,
            "members": [],
            "resources": {},
            "reputation": 0
        }

    # ==========================================================
    # MÉTODO PRINCIPAL DE PROCESO
    # ==========================================================
    def process_scene(self, user_input: str):
        """
        Procesa la entrada del jugador, genera la respuesta narrativa y
        gestiona la escena actual del juego.
        """
        logger.info(f"[Orchestrator] Entrada del jugador: {user_input}")

        # 1️⃣ Actualizar emoción global según entrada
        self.emotional_state = self.emotional_tracker.update_state(user_input)

        # 2️⃣ Obtener o crear escena actual
        current_scene = self.scene_manager.get_active_scene()
        if not current_scene:
            current_scene = self.scene_manager.create_initial_scene()

        # 3️⃣ Usar el Story Director para adaptar la respuesta
        narrative_output = self.story_director.process_input(
            user_input, current_scene, self.emotional_state
        )

        # 4️⃣ Renderizar respuesta narrativa para Telegram o interfaz
        rendered_output = render(narrative_output)

        # 5️⃣ Evaluar cierre o transición de escena
        if self.scene_manager.should_end_scene(narrative_output):
            self._end_scene_hook()

        return rendered_output

    # ==========================================================
    # EVENTO DINÁMICO AL FINAL DE ESCENA
    # ==========================================================
    def _end_scene_hook(self):
        """
        Cuando una escena termina, se dispara un evento mundial dinámico.
        """
        logger.info("[Orchestrator] Cerrando escena actual y generando evento mundial dinámico.")
        self.scene_manager.end_scene()

        # Generar evento
        event = self.event_generator.generate_event(
            self.world_state, self.emotional_state, self.party_state
        )

        # Aplicar consecuencias
        self.world_state, self.emotional_state, self.party_state = self.consequence_resolver.apply_consequences(
            event, self.world_state, self.emotional_state, self.party_state
        )

        # Log narrativo del evento
        summary = (
            f"\n🌍 *Evento Mundial:* {event.get('title','(sin título)')}\n"
            f"{event.get('description','Sin descripción')}"
        )
        logger.info(summary)

        # Registrar evento en histórico de mundo (temporal)
        if "world_history" not in self.world_state:
            self.world_state["world_history"] = []
        self.world_state["world_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event.get("title"),
            "description": event.get("description")
        })

        # Actualizar tono emocional tras evento
        self._update_tone_from_emotion()

    # ==========================================================
    # MÉTODO AUXILIAR
    # ==========================================================
    def _update_tone_from_emotion(self):
        """
        Ajusta el tono global según los valores emocionales acumulados.
        """
        fear = self.emotional_state.get("fear", 0)
        hope = self.emotional_state.get("hope", 0)
        tension = self.emotional_state.get("tension", 0)

        if fear > 0.6 and fear > hope:
            self.emotional_state["tone"] = "tensión"
        elif hope > 0.5:
            self.emotional_state["tone"] = "esperanza"
        elif tension > 0.4:
            self.emotional_state["tone"] = "melancolía"
        else:
            self.emotional_state["tone"] = "neutral"

        logger.info(f"[Orchestrator] Nuevo tono global: {self.emotional_state['tone']}")

    # ==========================================================
    # RESET / UTILIDADES
    # ==========================================================
    def reset_world(self):
        """
        Reinicia el estado del mundo (útil para nuevas campañas o testing).
        """
        logger.warning("[Orchestrator] Reiniciando mundo a estado base.")
        self.__init__()

    def export_state(self) -> dict:
        """
        Devuelve el estado completo del sistema (para persistencia o debugging).
        """
        return {
            "world_state": self.world_state,
            "emotional_state": self.emotional_state,
            "party_state": self.party_state
        }
