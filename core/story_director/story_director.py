import os
import random
from core.attributes.attribute_analyzer import AttributeAnalyzer
from core.emotion.emotional_tracker import EmotionalTracker
from core.emotion.tone_adapter import ToneAdapter
from core.scene_manager.scene_manager import SceneManager
from core.renderer.renderer import render

class StoryDirector:
    """
    Controlador maestro de la narrativa dinámica.
    Integra emociones, atributos y tono en una misma dirección narrativa.
    """

    def __init__(self):
        self.scene_manager = SceneManager()
        self.emotion_tracker = EmotionalTracker()
        self.attribute_analyzer = AttributeAnalyzer()
        self.tone_adapter = ToneAdapter()
        self.party_profile = None
        self.active_scene = None

    # =========================================================
    # CONFIGURACIÓN DE LA SESIÓN
    # =========================================================
    def initialize_session(self, party_attributes):
        """
        Inicializa el perfil narrativo del grupo combinando sus atributos.
        """
        self.party_profile = self.attribute_analyzer.analyze_party(party_attributes)
        self.emotion_tracker.reset_emotional_state()
        print(f"[StoryDirector] Perfil narrativo del grupo cargado: {self.party_profile}")

    # =========================================================
    # ESCENAS Y FLUJO NARRATIVO
    # =========================================================
    def start_scene(self, scene_template):
        """
        Crea una escena inicial basada en un template (progreso, tensión, etc.)
        y aplica los tonos según el perfil del grupo.
        """
        scene = self.scene_manager.create_scene_from_template(scene_template)
        adapted_description = self.tone_adapter.apply_tone(
            text=scene["description"],
            emotional_state=self.emotion_tracker.get_current_emotion(),
            party_profile=self.party_profile
        )

        scene["description_adapted"] = adapted_description
        self.active_scene = scene
        render(adapted_description)
        return scene

    # =========================================================
    # EVENTOS Y TRANSICIONES
    # =========================================================
    def handle_event(self, event_type):
        """
        Modifica emoción y tono según el tipo de evento narrativo (combate, éxito, pérdida, etc.).
        """
        new_emotion = self.emotion_tracker.update_from_event(event_type)
        print(f"[StoryDirector] Estado emocional actualizado: {new_emotion}")

        if self.active_scene:
            base_text = self.active_scene.get("description", "")
            new_description = self.tone_adapter.apply_tone(
                text=base_text,
                emotional_state=new_emotion,
                party_profile=self.party_profile
            )
            self.active_scene["description_adapted"] = new_description
            render(new_description)
        return new_emotion

    # =========================================================
    # UTILIDADES
    # =========================================================
    def summarize_scene(self):
        """
        Devuelve un resumen de la escena adaptada con tono y emoción.
        """
        if not self.active_scene:
            return "No hay escena activa."
        summary = f"[{self.emotion_tracker.get_current_emotion().capitalize()}] {self.active_scene['description_adapted']}"
        return summary

    def get_current_profile(self):
        """
        Devuelve el perfil narrativo actual del grupo.
        """
        return self.party_profile or {}


# =========================================================
# DEMO LOCAL
# =========================================================
if __name__ == "__main__":
    director = StoryDirector()
    party = [
        {"strength": 16, "dexterity": 14, "constitution": 13, "intelligence": 11, "wisdom": 10, "charisma": 8},
        {"strength": 8, "dexterity": 16, "constitution": 10, "intelligence": 15, "wisdom": 12, "charisma": 14}
    ]
    director.initialize_session(party)
    scene = director.start_scene("progress_scene.json")
    director.handle_event("combat_victory")
    print(director.summarize_scene())
