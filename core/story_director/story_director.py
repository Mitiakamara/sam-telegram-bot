# ================================================================
# 🎬 STORY DIRECTOR – Fase 7.6.1 (SRD 5.1.2 Stable)
# ================================================================
# Coordina narrativa, tono, emociones y progreso de campaña SRD.
# Ahora también integra personajes creados desde el Character Builder.
# ================================================================

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
    🎬 STORY DIRECTOR – Motor narrativo principal
    - Coordina emoción, tono, escena y progreso de campaña.
    - Administra personajes del grupo.
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
        self.player_characters = []  # lista de dicts con personajes creados

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
    # INTERFAZ PÚBLICA – Integración con Telegram
    # =========================================================
    def create_character(self, char_data: dict):
        """
        Registra un personaje creado desde el Character Builder
        o desde el flujo de Telegram.
        """
        self.player_characters.append(char_data)
        self.campaign_manager.set_party([c["name"] for c in self.player_characters])
        print(f"[StoryDirector] Personaje añadido: {char_data['name']}")
        return char_data

    def join_player(self, telegram_id, username):
        """Une un jugador existente o lo confirma en la campaña."""
        if username not in [c.get("name") for c in self.player_characters]:
            self.player_characters.append({"name": username})
            self.campaign_manager.set_party([c["name"] for c in self.player_characters])
        return {"message": f"✅ {username} se unió a la campaña."}

    def render_current_scene(self):
        """Devuelve el texto renderizado de la escena actual."""
        if not self.active_scene:
            return "No hay ninguna escena activa."
        return self.summarize_scene()

    def trigger_event(self, event_type):
        """Dispara un evento narrativo y devuelve el nuevo texto."""
        new_emotion = self.handle_event(event_type)
        return f"🎭 Evento '{event_type}' ejecutado. Emoción actual: {new_emotion.capitalize()}.\n\n{self.summarize_scene()}"

    def get_player_status(self, telegram_id=None):
        """Muestra estado narrativo general."""
        emotion = self.emotion_tracker.get_current_emotion()
        return (
            f"🎭 Estado emocional: *{emotion.capitalize()}*\n"
            f"📖 Escena actual: {self.active_scene['title'] if self.active_scene else 'N/A'}"
        )

    def get_campaign_progress(self):
        """Devuelve el progreso de campaña formateado."""
        return self.get_campaign_summary()

    def restart_campaign(self):
        """Reinicia la campaña al capítulo inicial."""
        self.campaign_manager.state["current_chapter"] = 1
        self.campaign_manager.state["completed_quests"] = []
        self.campaign_manager.state["pending_quests"] = []
        self.campaign_manager.state["active_scene"] = None
        self.campaign_manager.save_state()
        self.emotion_tracker.reset_emotional_state()
        print("[StoryDirector] Campaña reiniciada desde el inicio.")

    def load_campaign(self, campaign_slug):
        """Cambia la campaña activa (cargando un nuevo CampaignManager)."""
        self.campaign_manager = CampaignManager(campaign_slug)
        print(f"[StoryDirector] Campaña cargada: {campaign_slug}")

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

        adapted_description = self.tone_adapter.apply_tone(
            text=scene["description_adapted"],
            emotional_state=current_emotion,
            party_profile=self.party_profile
        )

        scene["description_adapted"] = adapted_description
        self.active_scene = scene

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
        self.auto_transition(event_type)
        self.campaign_manager.save_state()
        return new_emotion

    # =========================================================
    # MOTOR DE TRANSICIONES AUTOMÁTICAS
    # =========================================================
    def auto_transition(self, event_type):
        current_emotion = self.emotion_tracker.get_current_emotion()
        next_scene = self.transition_engine.get_next_scene(current_emotion, event_type)
        print(f"[StoryDirector] Transición automática a escena: {next_scene}")
        self.start_scene(next_scene)

    # =========================================================
    # GESTIÓN DE CAMPAÑA
    # =========================================================
    def complete_quest(self, quest_name):
        self.campaign_manager.add_completed_quest(quest_name)
        print(f"[StoryDirector] Misión completada: {quest_name}")

    def add_pending_quest(self, quest_name):
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
        return self.campaign_manager.get_summary()

    # =========================================================
    # DEMO LOCAL
    # =========================================================
    def demo(self):
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


if __name__ == "__main__":
    director = StoryDirector()
    try:
        director.demo()
    except FileNotFoundError:
        print("⚠️ No se encontró 'progress_scene.json'. "
              "Asegúrate de tener las plantillas en 'data/scene_templates/'.")
