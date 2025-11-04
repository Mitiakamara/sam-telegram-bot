import os
import random
from core.attributes.attribute_analyzer import AttributeAnalyzer
from core.emotion.emotional_tracker import EmotionalTracker
from core.tone_adapter import ToneAdapter
from core.scene_manager.scene_manager import SceneManager
from core.story_director.transition_engine import TransitionEngine
from core.renderer import render


class StoryDirector:
    """
    🎬 STORY DIRECTOR – Fase 7.4
    Orquesta toda la narrativa dinámica del sistema SAM.
    Combina emociones, atributos, tono, escenas y transiciones automáticas.
    """

    def __init__(self):
        # Módulos principales del motor narrativo
        self.scene_manager = SceneManager()
        self.emotion_tracker = EmotionalTracker()
        self.attribute_analyzer = AttributeAnalyzer()
        self.tone_adapter = ToneAdapter()
        self.transition_engine = TransitionEngine()

        # Estado actual de la historia
        self.party_profile = None
        self.active_scene = None

    # =========================================================
    # SESIÓN / INICIALIZACIÓN
    # =========================================================
    def initialize_session(self, party_attributes):
        """
        Genera el perfil narrativo del grupo a partir de sus atributos
        y reinicia el estado emocional global.
        """
        self.party_profile = self.attribute_analyzer.analyze_party(party_attributes)
        self.emotion_tracker.reset_emotional_state()
        print(f"[StoryDirector] Perfil narrativo del grupo cargado: {self.party_profile}")

    # =========================================================
    # CREACIÓN DE ESCENAS
    # =========================================================
    def start_scene(self, scene_template):
        """
        Crea y adapta una escena narrativa según:
        - El perfil del grupo (atributos)
        - El estado emocional actual
        """
        current_emotion = self.emotion_tracker.get_current_emotion()

        scene = self.scene_manager.create_scene_from_template(
            template_name=scene_template,
            party_profile=self.party_profile,
            emotion_state=current_emotion
        )

        # Aplicar tono final al texto de la escena
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
        Reacciona a un evento narrativo, actualiza emoción global
        y ejecuta transición automática hacia la siguiente escena.
        Ejemplos de event_type: 'combat_victory', 'setback', 'rally', etc.
        """
        # Actualizar emoción global
        new_emotion = self.emotion_tracker.update_from_event(event_type)
        print(f"[StoryDirector] Estado emocional actualizado: {new_emotion}")

        # Transición automática según evento
        self.auto_transition(event_type)
        return new_emotion

    # =========================================================
    # MOTOR DE TRANSICIONES AUTOMÁTICAS
    # =========================================================
    def auto_transition(self, event_type):
        """
        Determina la siguiente escena según la emoción actual
        y el tipo de evento ocurrido.
        """
        current_emotion = self.emotion_tracker.get_current_emotion()
        next_scene = self.transition_engine.get_next_scene(current_emotion, event_type)

        print(f"[StoryDirector] Transición automática a escena: {next_scene}")
        self.start_scene(next_scene)

    # =========================================================
    # RESÚMENES Y ESTADO
    # =========================================================
    def summarize_scene(self):
        """
        Devuelve un resumen de la escena actual con su tono y emoción.
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
    def demo(self):
        """
        Permite probar la narrativa completa con transiciones automáticas.
        """
        party = [
            {"strength": 16, "dexterity": 14, "constitution": 13, "intelligence": 11, "wisdom": 10, "charisma": 8},
            {"strength": 8, "dexterity": 16, "constitution": 10, "intelligence": 15, "wisdom": 12, "charisma": 14}
        ]

        self.initialize_session(party)
        print("\n🌄 Escena inicial:")
        self.start_scene("progress_scene.json")

        print("\n⚔️ Evento: combate victorioso")
        self.handle_event("combat_victory")

        print("\n💬 Resumen de la escena actual:")
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
