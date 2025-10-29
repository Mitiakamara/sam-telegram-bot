# ==========================================================
# 🎭 SAM Orchestrator – FINAL (Modo Campaña Pre-Creada)
# ==========================================================
import logging
from datetime import datetime

# --- Core SAM modules ---
from core.scene_manager.scene_manager import SceneManager
from core.story_director.story_director import StoryDirector
from core.emotion.emotional_tracker import EmotionalTracker
from core.renderer import render

# --- World systems (lightweight) ---
from core.world_events.event_generator import EventGenerator
from core.world_events.consequence_resolver import ConsequenceResolver
from core.world_events.world_influence import WorldInfluence
from core.persistence.state_persistence import StatePersistence

# ==========================================================
# CONFIGURACIÓN BASE
# ==========================================================
logger = logging.getLogger(__name__)
EVENT_REGISTRY_PATH = "core/world_events/event_registry.json"


class Orchestrator:
    """
    Núcleo coordinador de SAM.
    Gestiona narrativa, emoción, eventos ligeros y persistencia,
    optimizado para campañas pre-creadas (no sandbox procedural).
    """

    def __init__(self):
        # Subsistemas narrativos
        self.scene_manager = SceneManager()
        self.story_director = StoryDirector()
        self.emotional_tracker = EmotionalTracker()

        # Sistemas ligeros de mundo
        self.event_generator = EventGenerator(EVENT_REGISTRY_PATH)
        self.consequence_resolver = ConsequenceResolver()
        self.world_influence = WorldInfluence()

        # Persistencia
        self.persistence = StatePersistence()

        # Cargar estado previo (si existe)
        loaded_world, loaded_emotion, loaded_party = self.persistence.load_state()
        if loaded_world and loaded_emotion and loaded_party:
            logger.info("[Orchestrator] Estado del mundo restaurado desde sesión anterior.")
            self.world_state = loaded_world
            self.emotional_state = loaded_emotion
            self.party_state = loaded_party
        else:
            logger.info("[Orchestrator] Iniciando nuevo mundo narrativo.")
            self._init_default_state()

    # ==========================================================
    # ESTADO BASE
    # ==========================================================
    def _init_default_state(self):
        """Define el estado inicial del mundo, emociones y grupo."""
        self.world_state = {
            "time": "morning",
            "environment": {"weather": "templado", "terrain": "bosque"},
            "reputation": 0,
            "danger_zone": False,
            "current_location": "colinas de Faerûn",
            "world_history": []
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
    # BUCLE NARRATIVO PRINCIPAL
    # ==========================================================
    def process_scene(self, user_input: str):
        """
        Procesa una acción del jugador y devuelve la salida narrativa adaptada.
        """
        logger.info(f"[Orchestrator] Entrada del jugador: {user_input}")

        # 1️⃣ Actualizar estado emocional según entrada
        self.emotional_state = self.emotional_tracker.update_state(user_input)

        # 2️⃣ Obtener o crear escena activa
        current_scene = self.scene_manager.get_active_scene()
        if not current_scene:
            current_scene = self.scene_manager.create_initial_scene()

        # 3️⃣ Generar salida narrativa adaptativa
        narrative_output = self.story_director.process_input(
            user_input, current_scene, self.emotional_state
        )

        # 4️⃣ Renderizar respuesta (texto limpio para interfaz o Telegram)
        rendered_output = render(narrative_output)

        # 5️⃣ Evaluar si la escena termina
        if self.scene_manager.should_end_scene(narrative_output):
            self._end_scene_hook()

        return rendered_output

    # ==========================================================
    # EVENTOS LIGEROS Y PERSISTENCIA
    # ==========================================================
    def _end_scene_hook(self):
        """Ejecuta lógica de fin de escena: evento ligero + guardado."""
        logger.info("[Orchestrator] Fin de escena. Generando evento mundial ligero.")
        self.scene_manager.end_scene()

        # Generar evento contextual
        event = self.event_generator.generate_event(
            self.world_state, self.emotional_state, self.party_state
        )

        # Aplicar consecuencias ligeras
        self.world_state, self.emotional_state, self.party_state = self.consequence_resolver.apply_consequences(
            event, self.world_state, self.emotional_state, self.party_state
        )

        # Registrar evento en histórico
        self.world_state["world_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event.get("title"),
            "description": event.get("description")
        })

        # Ajustar tono global según emociones y eventos
        self.emotional_state = self.world_influence.analyze_history(
            self.world_state, self.emotional_state
        )

        # Guardar estado persistente
        self.persistence.save_state(
            self.world_state, self.emotional_state, self.party_state
        )

        # Log de resumen
        logger.info(f"[Evento Mundial] {event.get('title')} — {event.get('description')}")

    # ==========================================================
    # UTILIDADES
    # ==========================================================
    def reset_world(self):
        """Reinicia el mundo narrativo a su estado base."""
        logger.warning("[Orchestrator] Reiniciando mundo narrativo.")
        self._init_default_state()
        self.persistence.save_state(self.world_state, self.emotional_state, self.party_state)

    def export_state(self) -> dict:
        """Devuelve el estado completo del sistema (para debug o interfaz)."""
        return {
            "world_state": self.world_state,
            "emotional_state": self.emotional_state,
            "party_state": self.party_state
        }
