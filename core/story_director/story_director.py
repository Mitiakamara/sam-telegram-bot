import os
import random
from core.attributes.attribute_analyzer import AttributeAnalyzer
from core.emotion.emotional_tracker import EmotionalTracker
from core.tone_adapter import ToneAdapter
from core.scene_manager.scene_manager import SceneManager
from core.renderer import render


class StoryDirector:
    """
    🎬 STORY DIRECTOR — Fase 7.3
    Coordina la narrativa dinámica de SAM combinando:
    - Estado emocional global (EmotionalTracker)
    - Perfil de atributos del grupo (AttributeAnalyzer)
    - Tono narrativo (ToneAdapter)
    - Escenas dinámicas (SceneManager)
    """

    def __init__(self):
        self.scene_manager = SceneManager()
        self.emotion_tracker = EmotionalTracker()
        self.attribute_analyzer = AttributeAnalyzer()
        self.tone_adapter = ToneAdapter()

        self.party_profile = None
        self.active_scene = None

    # =========================================================
    # SESIÓN / INICIALIZACIÓN
    # =========================================================
    def initialize_session(self, party_attributes):
        """
        Genera el perfil narrativo de grupo a partir de los atributos
        combinados de los personajes. Reinicia el estado emocional.
        """
        self.party_profile = self.attribute_analyzer.analyze_party(party_attributes)
        self.emotion_tracker.reset_emotional_state()
        print(f"[StoryDirector] Perfil narrativo del grupo cargado: {self.party_profile}")

    # =========================================================
    # CREACIÓN DE ESCENAS
    # =========================================================
    def start_scene(self, scene_template):
        """
        Crea y adapta una nueva escena narrativa según:
        - El perfil del grupo (atributos)
        - El estado emocional actual
        """
        current_emotion = self.emotion_tracker.get_current_emotion()

        scene = self.scene_manager.create_scene_from_template(
            template_name=scene_template,
            party_profile=self.party_profile,
            emotion_state=current_emotion
        )

        # Adaptar tono emocional general con el ToneAdapter
        adapted_description = self.tone_adapter.apply_tone(
            text=scene["description_adapted"],
            emotional_state=current_emotion,
            party_profile=self.party_profile
        )

        scene["description_adapted"] = adapted_description
        self.active_scene = scene

        render(adapted_description)
        return scene

    # =========================================================
    # EVENTOS Y EVOLUCIÓN EMOCIONAL
    # =========================================================
    def handle_event(self, event_type):
        """
        Modifica el estado emocional global y actualiza la escena activa.
        Ejemplos de event_type: 'combat_victory', 'setback', 'discovery', etc.
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
    # RESÚMENES Y ESTADO
    # =========================================================
    def summarize_scene(self):
        """
        Devuelve un resumen de la escena actual con su tono adaptado.
        """
        if not self.active_scene:
            return "No hay escena activa."
        summary = f"[{self.emotion_tracker.get_current_emotion().capitalize()}] {self.active_scene['description_adapted']}"
        return summary

    def get_current_profile(self):
        """
        Devuelve el perfil narrativo del grupo.
        """
        return self.party_profile or {}

    # =========================================================
    # DEMO LOCAL
    # =========================================================
    def demo(self):
        """
        Permite probar el sistema narrativo sin usar Telegram.
        """
        party = [
            {"strength": 16, "dexterity": 14, "constitution": 13, "intelligence": 11, "wisdom": 10, "charisma": 8},
            {"strength": 8, "dexterity": 16, "constitution": 10, "intelligence": 15, "wisdom": 12, "charisma": 14}
        ]

        self.initialize_session(party)
        scene = self.start_scene("progress_scene.json")
        self.handle_event("triumph")
        print(self.summarize_scene())


# =========================================================
# MODO STANDALONE
# =========================================================
if __name__ == "__main__":
    director = StoryDirector()
    try:
        director.demo()
    except FileNotFoundError:
        print("⚠️  No se encontró 'progress_scene.json'. "
              "Asegúrate de tener las plantillas en 'data/scene_templates/'.")
