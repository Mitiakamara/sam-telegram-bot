# ================================================================
# 🧠 ORCHESTRATOR (SAM Core)
# ================================================================
# Controlador central del flujo narrativo.
# Coordina el SceneManager, StoryDirector, EmotionalTracker y Renderer.
#
# Funciones principales:
#   - Recibir entradas del jugador
#   - Procesar el estado de la escena
#   - Generar una nueva respuesta narrativa coherente
# ================================================================

import logging
from datetime import datetime

# Core components
from core.scene_manager.scene_manager import SceneManager
from core.emotion.emotional_tracker import EmotionalTracker
from core.story_director.story_director import StoryDirector  # ✅ FIXED import
from core.renderer import render

# Persistence
from core.persistence.state_persistence import StatePersistence

# Models
from core.models.telegram_msg import TelegramMessage

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Coordina los módulos narrativos y maneja el ciclo principal de SAM.
    """

    def __init__(self):
        logger.info("[Orchestrator] Inicializando módulos narrativos...")
        self.scene_manager = SceneManager()
        self.story_director = StoryDirector()
        self.emotional_tracker = EmotionalTracker()
        self.persistence = StatePersistence()

        # Estado base
        self.current_scene = None
        self.last_response = None

        logger.info("[Orchestrator] Iniciando nuevo mundo narrativo.")
        self.reset_world()

    # ------------------------------------------------------------
    # 🌍 Reinicio del mundo narrativo
    # ------------------------------------------------------------
    def reset_world(self):
        logger.warning("[Orchestrator] Reiniciando mundo narrativo.")
        self.scene_manager.reset_scenes()
        self.current_scene = self.scene_manager.create_initial_scene()
        self.emotional_tracker.reset()
        self.persistence.save_state({"scene": self.current_scene})
        self.last_response = None

    # ------------------------------------------------------------
    # 💬 Procesamiento de entrada del jugador
    # ------------------------------------------------------------
    def process_scene(self, player_input: str) -> TelegramMessage:
        """
        Procesa una acción o diálogo del jugador.
        Devuelve un objeto TelegramMessage renderizado.
        """

        logger.info(f"[Orchestrator] Entrada del jugador: {player_input}")

        # 1. Registrar emoción derivada de la acción
        self.emotional_tracker.track_emotion_from_input(player_input)

        # 2. Evaluar tipo de próxima escena
        next_scene_type = self.story_director.decide_next_scene_type()

        # 3. Generar salida narrativa (placeholder básico)
        narrative_output = self.scene_manager.generate_scene_description(
            player_input=player_input,
            scene_type=next_scene_type
        )

        # 4. Evaluar resultado narrativo (éxito / fracaso / mixto)
        player_success = self.scene_manager.estimate_player_success(player_input)
        outcome = self.story_director.evaluate_scene_outcome(player_success)
        narrative_output["outcome"] = outcome

        # 5. Guardar estado actualizado
        self.persistence.save_state({
            "last_input": player_input,
            "scene_type": next_scene_type,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat()
        })

        # 6. Renderizar salida final (TelegramMessage)
        rendered_output = render(narrative_output)
        self.last_response = rendered_output

        return rendered_output

    # ------------------------------------------------------------
    # 🧩 Integración con comandos especiales (/createcharacter, etc.)
    # ------------------------------------------------------------
    def handle_command(self, command: str, args=None) -> str:
        """
        Procesa comandos específicos del sistema (join, reset, etc.)
        """
        if command == "/reset":
            self.reset_world()
            return "🌍 El mundo ha sido reiniciado. La historia comienza de nuevo..."
        elif command == "/join":
            return "🧙‍♂️ Te unes a la campaña. Prepara tu hoja de personaje."
        elif command == "/createcharacter":
            return (
                "📜 Para crear tu personaje, describe su nombre, raza y clase. "
                "Por ejemplo: 'Mi personaje es un elfo mago llamado Aerendir'."
            )
        else:
            return "🤔 No reconozco ese comando. Usa /reset, /join o /createcharacter."


# ------------------------------------------------------------
# 🧪 DEMO LOCAL
# ------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sam = Orchestrator()

    print("\n🎮 SAM Demo:")
    print("-------------")
    response = sam.process_scene("Corro hacia la puerta")
    print(f"\n🧾 Mensaje renderizado:\n{response.text}\n")
