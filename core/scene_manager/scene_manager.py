# ================================================================
# 🎬 SCENE MANAGER
# ================================================================
# Gestiona las escenas activas de la historia, sus transiciones,
# y las descripciones narrativas asociadas.
#
# Fase 6.30 compatible con el nuevo Orchestrator (Fase 7.x)
# ================================================================

import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)


class Scene:
    """
    Representa una escena narrativa en curso.
    """

    def __init__(self, title: str, description: str, scene_type: str = "progress"):
        self.scene_id = f"scene_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        self.title = title
        self.description = description
        self.scene_type = scene_type
        self.status = "active"
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "scene_id": self.scene_id,
            "title": self.title,
            "description": self.description,
            "scene_type": self.scene_type,
            "status": self.status,
            "created_at": self.created_at,
        }


# ================================================================
# 🧩 SCENE MANAGER CORE
# ================================================================
class SceneManager:
    def __init__(self):
        self.scenes = []
        self.current_scene = None
        logger.info("[SceneManager] Inicializado correctamente.")

    # ------------------------------------------------------------
    # 🔄 Reinicio de escenas
    # ------------------------------------------------------------
    def reset_scenes(self):
        """
        Restablece todas las escenas y crea la inicial.
        """
        self.scenes = []
        self.current_scene = None
        initial_scene = self.create_initial_scene()
        logger.info("[SceneManager] Escenas reiniciadas correctamente.")
        return initial_scene

    # ------------------------------------------------------------
    # 🏁 Escena inicial
    # ------------------------------------------------------------
    def create_initial_scene(self) -> Scene:
        """
        Crea la escena inicial de la aventura.
        """
        initial_scene = Scene(
            title="Inicio de la aventura",
            description="Una brisa fría atraviesa el valle silencioso. "
                        "El grupo observa las ruinas antiguas a lo lejos.",
            scene_type="progress"
        )
        self.scenes.append(initial_scene)
        self.current_scene = initial_scene
        logger.info("[SceneManager] Escena inicial creada.")
        return initial_scene

    # ------------------------------------------------------------
    # 🧭 Generación de nuevas escenas
    # ------------------------------------------------------------
    def generate_scene_description(self, player_input: str, scene_type: str) -> dict:
        """
        Genera una descripción narrativa básica según la acción del jugador
        y el tipo de escena decidido por el StoryDirector.
        """
        tone_descriptions = {
            "progress": "El camino se aclara, y una sensación de avance recorre el ambiente.",
            "tension": "La atmósfera se vuelve densa, como si algo oculto observara desde la penumbra.",
            "triumph": "Una sensación de victoria y alivio llena el aire.",
            "setback": "Un giro inesperado complica los planes del grupo.",
            "complication": "Algo fuera de lo previsto surge, poniendo a prueba su determinación.",
        }

        desc = tone_descriptions.get(scene_type, tone_descriptions["progress"])

        description = (
            f"{desc} Tras tu acción ('{player_input}'), "
            f"la historia toma un nuevo rumbo de tipo '{scene_type}'."
        )

        scene = Scene(
            title=f"Escena de tipo {scene_type}",
            description=description,
            scene_type=scene_type
        )

        self.scenes.append(scene)
        self.current_scene = scene

        logger.info(f"[SceneManager] Nueva escena generada ({scene_type}).")
        return {
            "title": scene.title,
            "description": scene.description,
            "scene_type": scene_type,
        }

    # ------------------------------------------------------------
    # 🎯 Estimación de éxito del jugador
    # ------------------------------------------------------------
    def estimate_player_success(self, player_input: str) -> float:
        """
        Calcula un valor de éxito del jugador entre 0 y 1 basado en factores simples.
        (Futuro: integrar con tiradas de dados y stats de personaje)
        """
        keywords_success = ["ataco", "logro", "enciendo", "abro", "descubro", "supero"]
        keywords_failure = ["caigo", "fracaso", "pierdo", "rompo", "fallo", "huyo"]

        score = 0.5  # base neutra
        for kw in keywords_success:
            if kw in player_input.lower():
                score += 0.2
        for kw in keywords_failure:
            if kw in player_input.lower():
                score -= 0.2

        # normaliza entre 0 y 1
        final_score = max(0.0, min(1.0, score + random.uniform(-0.1, 0.1)))
        logger.info(f"[SceneManager] Éxito estimado del jugador: {final_score:.2f}")
        return final_score

    # ------------------------------------------------------------
    # 📖 Obtener la escena actual
    # ------------------------------------------------------------
    def get_current_scene(self):
        """
        Devuelve la escena activa.
        """
        return self.current_scene

    # ------------------------------------------------------------
    # 🗺️ Listar todas las escenas
    # ------------------------------------------------------------
    def list_scenes(self):
        """
        Devuelve una lista de todas las escenas registradas.
        """
        return [scene.to_dict() for scene in self.scenes]


# ------------------------------------------------------------
# 🧪 DEMO LOCAL
# ------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sm = SceneManager()

    sm.reset_scenes()
    sm.generate_scene_description("Observo las ruinas", "tension")
    sm.generate_scene_description("Cruzo el puente", "progress")
    print("\nEscenas generadas:")
    for s in sm.list_scenes():
        print(f"- {s['title']}: {s['description']}")
