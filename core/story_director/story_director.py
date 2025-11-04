import os
import random
from core.attributes.attribute_analyzer import AttributeAnalyzer
from core.emotion.emotional_tracker import EmotionalTracker
from core.tone_adapter import ToneAdapter
from core.scene_manager.scene_manager import SceneManager
from core.story_director.transition_engine import TransitionEngine
from core.renderer import render
from core.campaign import CampaignManager


class StoryDirector:
    """
    🎬 STORY DIRECTOR – Fase 7.5 (Integrado con CampaignManager)
    Coordina narrativa, tono, emociones y progreso de campaña SRD.
    """

    def __init__(self):
        # Módulos principales
        self.scene_manager = SceneManager()
        self.emotion_tracker = EmotionalTracker()
        self.attribute_analyzer = AttributeAnalyzer()
        self.tone_adapter = ToneAdapter()
        self.transition_engine = TransitionEngine()
        self.campaign_manager = CampaignManager("The_Genie_s_Wishes")

        # Estado actual
        self.party_profile = None
        self.active_scene = None

    # =========================================================
    # SESIÓN / INICIALIZACIÓN
    # =========================================================
    def initialize_session(self, party_attributes, party_names=None):
        """
        Genera el perfil narrativo del grupo a partir de sus atributos
        y reinicia el estado emocional global. También establece la party.
        """
        self.party_profile = self.attribute_analyzer.analyze_party(party_attributes)
        self.emotion_tracker.reset_emotional_state()

        if party_names:
            self.campaign_manager.set_party(party_names)

        print(f"[StoryDirector] Perfil narrativo del grupo cargado: {self.party_profile}")

    # =========================================================
    # CREACIÓN DE ESCENAS
    # =========================================================
    def start_scene(self, scene_template):
        """
        Crea y adapta una nueva escena según el perfil del grupo
        y el estado emocional actual. También actualiza el progreso
        en CampaignManager.
        """
        current_emotion = self.emotion_tracker.get_current_emotion()

        scene = self.scene_manager.create_scene_from_template(
            template_name=scene_template,
            party_profile=self.party_profile,
            emotion_state=current_emotion
        )

        # Aplicar tono narrativo final
        adapted_description = self.tone_adapter.apply_tone(
            text=scene["description_adapted"],
            emotional_state=current_emotion,
            party_profile=self.party_profile
        )

        scene["description_adapted"] = adapted_description
        self.active_scene = scene

        # Guardar progreso de campaña
        self.campaign_manager.update_scene(scene_template)

        render(adapted_description)
        return scene

    # =========================================================
    # EVENTOS Y EVOLUCIÓN EMOCIONAL
    # =========================================================
    def handle_event(self, event_type):
        """
        Reacciona a un evento narrativo y guarda el progreso actualizado.
        """
        new_emotion = self.emotion_tracker.update_from_event(event_type)
        print(f"[StoryDirector] Estado emocional actualizado: {new_emotion}")

        # Transición automática
        self.auto_transition(event_type)

        # Guardar estado luego de evento
        self.campaign_manager.save_state()

        return new_emotion

    # =========================================================
    # MOTOR DE TRANSICIONES AUTOMÁTICAS
    # =========================================================
    def auto_transition(self, event_type):
        """
        Determina la siguiente escena y actualiza el registro de campaña.
        """
        current_emotion = self.emotion_tracker.get_current_emotion()
        next_scene = self.transition_engine.get_next_scene(current_emotion, event_type)

        print(f"[StoryDirector] Transición automática a escena: {next_scene}")
        self.start_scene(next_scene)

    # =========================================================
    # GESTIÓN DE CAMPAÑA
    # =========================================================
    def complete_quest(self, quest_name):
        """
        Marca una misión como completada en la campaña actual.
        """
        self.campaign_manager.add_completed_quest(quest_name)
        print(f"[StoryDirector] Misión completada: {quest_name}")

    def add_pending_quest(self, quest_name):
        """
        Agrega una nueva misión pendiente.
        """
        self.campaign_manager.add_pending_quest(quest_name)
        print(f"[StoryDirector] Nueva misión añadida: {quest_name}")

    # =========================================================
    # RESÚMENES Y ESTADO
    # =========================================================
    def summarize_scene(self):
        if not self.active_scene:
            return "No hay escena activa."
        summary = f"[{self.emotion_tracker.get_current_emotion().capitalize()}] {self.active_scene['description_adapted']}"
        return summary

    def get_current_profile(self):
        return self.party_profile or {}

    def get_campaign_summary(self):
        """
        Devuelve el resumen formateado del estado actual de la campaña.
        """
        return self.campaign_manager.get_summary()

    # =========================================================
    # DEMO LOCAL
    # =========================================================
    def demo(self):
        """
        Prueba completa de flujo narrativo + guardado de progreso.
        """
        party = [
            {"strength": 16, "dexterity": 14, "constitution": 13, "intelligence": 11, "wisdom": 10, "charisma": 8},
            {"strength": 8, "dexterity": 16, "constitution": 10, "intelligence": 15, "wisdom": 12, "charisma": 14}
        ]
        names = ["Pimp", "Asterix"]

        self.initialize_session(party, names)
        print("\n🌄 Escena inicial:")
        self.start_scene("progress_scene.json")

        print("\n⚔️ Evento: combate victorioso")
        self.handle_event("combat_victory")

        print("\n📘 Estado actual de la campaña:")
        print(self.get_campaign_summary())

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
