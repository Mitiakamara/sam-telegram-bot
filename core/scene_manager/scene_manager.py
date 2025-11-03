import os
import json
from datetime import datetime
from core.scene_manager.scene_adapter import SceneAdapter

class SceneManager:
    """
    Gestiona las escenas activas y su adaptación narrativa.
    Fase 7.3: integra el SceneAdapter para modificar descripciones
    según el perfil de grupo y el estado emocional actual.
    """

    def __init__(self, templates_path="data/scene_templates"):
        self.templates_path = templates_path
        self.active_scene = None
        self.scene_history = []
        self.scene_adapter = SceneAdapter()

    # =========================================================
    # CARGA DE PLANTILLAS
    # =========================================================
    def load_template(self, template_name):
        """
        Carga una plantilla JSON desde la carpeta de plantillas.
        """
        path = os.path.join(self.templates_path, template_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Plantilla de escena no encontrada: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    # =========================================================
    # CREACIÓN Y ADAPTACIÓN DE ESCENA
    # =========================================================
    def create_scene_from_template(self, template_name, party_profile=None, emotion_state="neutral"):
        """
        Crea una escena nueva a partir de un template JSON.
        Luego adapta su descripción según el perfil del grupo y el estado emocional actual.
        """
        data = self.load_template(template_name)

        # Datos base de la plantilla
        scene = {
            "scene_id": f"scene_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": data.get("title", "Escena sin título"),
            "description": data.get("description", ""),
            "scene_type": data.get("scene_type", "narrative"),
            "emotion_intensity": data.get("emotion_intensity", 3),
            "objectives": data.get("objectives", []),
            "environment": data.get("environment", {}),
            "available_actions": data.get("available_actions", []),
            "npcs": data.get("npcs", []),
            "transitions": data.get("transitions", []),
            "status": "active"
        }

        # Adaptar descripción con el SceneAdapter
        adapted_text = self.scene_adapter.adapt_scene_description(
            base_text=scene["description"],
            party_profile=party_profile,
            emotion_state=emotion_state
        )
        scene["description_adapted"] = adapted_text

        # Registrar escena activa e historial
        self.active_scene = scene
        self.scene_history.append(scene)
        return scene

    # =========================================================
    # HISTORIAL DE ESCENAS
    # =========================================================
    def get_scene_history(self, limit=5):
        """
        Devuelve las últimas escenas creadas o activas.
        """
        return self.scene_history[-limit:]

    # =========================================================
    # ACTUALIZACIÓN DE ESTADO
    # =========================================================
    def update_scene_status(self, new_status="completed"):
        """
        Cambia el estado de la escena activa.
        """
        if self.active_scene:
            self.active_scene["status"] = new_status

    # =========================================================
    # OBTENER ESCENA ACTIVA
    # =========================================================
    def get_active_scene(self):
        """
        Devuelve la escena actualmente activa.
        """
        return self.active_scene

    # =========================================================
    # DEMO LOCAL
    # =========================================================
    def demo(self):
        """
        Prueba rápida de adaptación narrativa sin StoryDirector.
        """
        fake_profile = {
            "brute": 0.2, "graceful": 0.7, "clever": 0.5,
            "resilient": 0.4, "insightful": 0.6, "charming": 0.3
        }
        scene = self.create_scene_from_template(
            "progress_scene.json",
            party_profile=fake_profile,
            emotion_state="progress"
        )
        print(f"Título: {scene['title']}")
        print(f"Descripción adaptada:\n{scene['description_adapted']}")


# =========================================================
# MODO STANDALONE
# =========================================================
if __name__ == "__main__":
    manager = SceneManager()
    try:
        manager.demo()
    except FileNotFoundError:
        print("⚠️  No se encontró 'progress_scene.json'. "
              "Asegúrate de tener las plantillas en 'data/scene_templates/'.")
