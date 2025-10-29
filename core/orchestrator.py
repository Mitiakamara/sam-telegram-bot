# ================================================================
# 🧠 ORCHESTRATOR
# ================================================================
# Núcleo maestro de SAM: coordina los subsistemas narrativos.
# Se encarga de:
#  - Inicializar los módulos del motor narrativo
#  - Gestionar el flujo de escenas
#  - Monitorear el estado emocional y de campaña
#  - Guardar y restaurar el estado global del mundo
#
# Compatible con: Fase 7.0 – Dynamic World Events & Consequences
# ================================================================

import logging
from datetime import datetime

# ------------------------------------------------------------
# Importación de módulos principales
# ------------------------------------------------------------
from core.scene_manager.scene_manager import SceneManager
from core.emotion.emotional_tracker import EmotionalTracker
from core.story_director.story_director import StoryDirector
from core.persistence.state_persistence import StatePersistence

logger = logging.getLogger(__name__)


# ================================================================
# 🧩 CLASE PRINCIPAL
# ================================================================
class Orchestrator:
    def __init__(self):
        logger.info("[Orchestrator] Inicializando módulos narrativos...")

        # Inicialización de subsistemas
        self.scene_manager = SceneManager()
        self.emotional_tracker = EmotionalTracker()
        self.story_director = StoryDirector()
        self.persistence = StatePersistence()

        # Estado actual
        self.current_scene = None
        self.current_state = {}

        logger.info("[Orchestrator] Iniciando nuevo mundo narrativo.")
        self.reset_world()

    # ------------------------------------------------------------
    # 🌍 Reinicio total del mundo narrativo
    # ------------------------------------------------------------
    def reset_world(self):
        """
        Reinicia completamente el mundo narrativo y guarda su estado inicial.
        """
        logger.warning("[Orchestrator] Reiniciando mundo narrativo.")

        # Reinicio de módulos
        self.scene_manager.reset_scenes()
        self.emotional_tracker.reset()

        # Estado inicial
        self.current_scene = self.scene_manager.get_current_scene()

        scene_state = {"scene": self.current_scene.to_dict()}
        emotional_state = self.emotional_tracker.get_current_state()
        party_state = {"members": []}  # aún no hay jugadores al iniciar

        # Persistir estado inicial
        self.persistence.save_state(scene_state, emotional_state, party_state)
        logger.info("[Orchestrator] Mundo narrativo reiniciado y persistido correctamente.")

    # ------------------------------------------------------------
    # 🎭 Procesar acción del jugador
    # ------------------------------------------------------------
    def process_player_action(self, player_input: str):
        """
        Procesa la acción del jugador, genera la siguiente escena
        y actualiza las emociones globales.
        """
        logger.info(f"[Orchestrator] Acción del jugador: {player_input}")

        # Evaluar éxito aproximado
        success_score = self.scene_manager.estimate_player_success(player_input)

        # Evaluar resultado emocional y narrativo
        outcome = self.story_director.evaluate_scene_outcome(success_score)
        next_scene_type = self.story_director.decide_next_scene_type()

        # Actualizar emociones según resultado
        if outcome == "success":
            self.emotional_tracker.record_emotion("joy", 0.8)
        elif outcome == "failure":
            self.emotional_tracker.record_emotion("fear", 0.6)
        else:
            self.emotional_tracker.record_emotion("tension", 0.5)

        # Crear siguiente escena
        next_scene_data = self.scene_manager.generate_scene_description(player_input, next_scene_type)
        self.current_scene = self.scene_manager.get_current_scene()

        # Guardar nuevo estado
        scene_state = {"scene": self.current_scene.to_dict()}
        emotional_state = self.emotional_tracker.get_current_state()
        party_state = {"members": []}  # temporal hasta integrar party_manager

        self.persistence.save_state(scene_state, emotional_state, party_state)

        logger.info(f"[Orchestrator] Nueva escena generada: {next_scene_data['title']}")
        return {
            "scene": next_scene_data,
            "emotion": emotional_state,
            "outcome": outcome,
        }

    # ------------------------------------------------------------
    # 📖 Obtener estado global
    # ------------------------------------------------------------
    def get_state(self):
        """
        Devuelve un resumen del estado global actual.
        """
        return {
            "scene": self.current_scene.to_dict() if self.current_scene else None,
            "emotion": self.emotional_tracker.get_current_state(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ------------------------------------------------------------
    # 💾 Guardar estado manualmente
    # ------------------------------------------------------------
    def save(self):
        """
        Guarda manualmente el estado actual del mundo.
        """
        scene_state = {"scene": self.current_scene.to_dict()}
        emotional_state = self.emotional_tracker.get_current_state()
        party_state = {"members": []}

        self.persistence.save_state(scene_state, emotional_state, party_state)
        logger.info("[Orchestrator] Estado del mundo guardado manualmente.")


# ------------------------------------------------------------
# 🧪 DEMO LOCAL
# ------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sam = Orchestrator()
    print("🎬 Mundo narrativo inicializado correctamente.\n")

    # Simular acción del jugador
    result = sam.process_player_action("Observo las ruinas y preparo mi arco.")
    print("\nResultado de acción:")
    print(result)
