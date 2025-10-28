import os
from datetime import datetime
from core.tone_adapter.tone_adapter import ToneAdapter
from core.mood_manager.mood_manager import MoodManager


# ================================================================
# 🎬 STORY DIRECTOR – Motor de decisiones narrativas adaptativas
# ================================================================
class StoryDirector:
    """
    Coordina el flujo narrativo general de la campaña.
    Controla la creación y cierre de escenas, el tono adaptativo
    y el clima emocional global de la historia.
    """

    def __init__(self, scene_manager=None, tone_adapter=None, base_path: str = "data/"):
        """
        scene_manager: referencia al SceneManager (opcional)
        tone_adapter: referencia al ToneAdapter
        base_path: ruta base para cargar estado y datos
        """
        self.base_path = base_path
        self.scene_manager = scene_manager  # se setea desde fuera o se crea diferidamente
        self.tone_adapter = tone_adapter or ToneAdapter(os.path.join(base_path, "emotion/emotional_scale.json"))
        self.mood_manager = MoodManager(os.path.join(base_path, "game_state.json"))

        # 🔄 Importación diferida para romper el ciclo con SceneManager
        if self.scene_manager is None:
            from core.scene_manager.scene_manager import SceneManager
            self.scene_manager = SceneManager()

    # ------------------------------------------------------------
    # 🎭 CONTROL DE ESCENAS
    # ------------------------------------------------------------

    def create_scene(self, title: str, description: str, scene_type: str, emotion_intensity: float = 0.5):
        """
        Crea una nueva escena adaptada al mood global actual.
        """
        current_mood = self.mood_manager.mood_state
        genre_profile = self.mood_manager.genre_profile

        # Adaptar tono narrativo según clima global
        adapted_description = self.tone_adapter.adapt_tone(
            description=description,
            emotion=current_mood,
            intensity=emotion_intensity,
            genre=genre_profile
        )

        new_scene = {
            "scene_id": datetime.utcnow().isoformat(),
            "title": title,
            "description": description,
            "description_adapted": adapted_description,
            "scene_type": scene_type,
            "emotion": current_mood,
            "emotion_intensity": emotion_intensity,
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }

        # Guardar en SceneManager
        try:
            self.scene_manager.state_service.save_scene(new_scene)
        except Exception:
            pass

        # Analizar clima emocional global
        self._update_mood()
        return new_scene

    def close_scene(self, result: str = None):
        """
        Cierra la escena actual y actualiza el clima emocional global.
        """
        current_scene = self.scene_manager.get_active_scene()
        if not current_scene:
            return None

        current_scene["status"] = "closed"
        current_scene["ended_at"] = datetime.utcnow().isoformat()
        if result:
            current_scene["resolution"] = result

        try:
            self.scene_manager.state_service.save_scene(current_scene)
        except Exception:
            pass

        # 🔄 Actualiza el mood global
        self._update_mood()
        return current_scene

    # ------------------------------------------------------------
    # 🔄 ACTUALIZACIÓN DE MOOD GLOBAL
    # ------------------------------------------------------------

    def _update_mood(self):
        """
        Analiza las últimas escenas para ajustar el mood global.
        Si hay saltos bruscos, sugiere una transición tonal.
        """
        recent_scenes = []
        try:
            recent_scenes = self.scene_manager.state_service.load_recent_scenes(limit=5)
        except Exception:
            if hasattr(self.scene_manager, "get_recent_scenes"):
                recent_scenes = self.scene_manager.get_recent_scenes(limit=5)

        if not recent_scenes:
            return

        mood, intensity = self.mood_manager.analyze_recent_scenes([
            {
                "scene_id": s.get("scene_id"),
                "emotion": s.get("emotion", "neutral"),
                "emotion_intensity": s.get("emotion_intensity", 0.5)
            }
            for s in recent_scenes
        ])

        # Normalizar tono si hay salto emocional
        transition = self.mood_manager.normalize_mood()
        if transition:
            self._inject_transition_scene(transition)

        # Reforzar alineación de género
        self.mood_manager.align_to_genre()

        print(f"[🎭 MoodManager] Estado tonal actualizado → {mood} ({intensity})")

    # ------------------------------------------------------------
    # ⚖️ TRANSICIONES TONALES
    # ------------------------------------------------------------

    def _inject_transition_scene(self, transition_data: dict):
        """
        Inserta una escena puente si el MoodManager detecta un salto tonal fuerte.
        """
        if not transition_data:
            return

        title = "Transición emocional"
        description = transition_data.get("suggestion", "El ambiente cambia sutilmente, reflejando las emociones recientes.")
        scene_type = "transition"

        new_scene = {
            "scene_id": datetime.utcnow().isoformat(),
            "title": title,
            "description": description,
            "description_adapted": self.tone_adapter.adapt_tone(
                description=description,
                emotion="neutral",
                intensity=0.3
            ),
            "scene_type": scene_type,
            "emotion": "neutral",
            "emotion_intensity": 0.3,
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }

        try:
            self.scene_manager.state_service.save_scene(new_scene)
        except Exception:
            pass

        print(f"[⚖️ Transition] Escena de transición generada entre moods {transition_data['from']} → {transition_data['to']}")

    # ------------------------------------------------------------
    # 💬 FEEDBACK EMOCIONAL
    # ------------------------------------------------------------

    def apply_feedback(self, player_emotion: str, delta: float = 0.1):
        """
        Ajusta la intensidad tonal global según feedback emocional del jugador o del sistema.
        """
        try:
            new_intensity = self.mood_manager.adjust_from_feedback(player_emotion, delta)
            print(f"[🧠 Feedback] Intensidad tonal ajustada → {new_intensity} por emoción '{player_emotion}'")
            return new_intensity
        except Exception as e:
            print(f"[⚠️ StoryDirector] No se pudo aplicar feedback emocional: {e}")
            return None

    # ------------------------------------------------------------
    # 📊 CONSULTAS
    # ------------------------------------------------------------

    def get_current_mood(self):
        """Devuelve el estado tonal global actual."""
        return {
            "mood_state": self.mood_manager.mood_state,
            "mood_intensity": self.mood_manager.mood_intensity,
            "genre_profile": self.mood_manager.genre_profile,
            "last_update": self.mood_manager.last_update
        }

    def generate_transition(self):
        """
        Genera un texto breve de transición adaptado al estado tonal actual.
        """
        mood = self.mood_manager.mood_state
        intensity = self.mood_manager.mood_intensity

        transition_templates = {
            "hopeful": "La luz renace en medio de la oscuridad, un nuevo comienzo parece cercano.",
            "tense": "El ambiente se carga de tensión; cada paso podría ser el último.",
            "melancholic": "El eco del pasado resuena entre las sombras del presente.",
            "grim": "Nada bueno aguarda más adelante, pero el deber empuja hacia el abismo.",
            "mystical": "Las energías del mundo despiertan, tejiendo un nuevo hilo en el destino.",
            "fearful": "Un frío extraño recorre la piel, presagio de lo que está por venir.",
            "serene": "Todo parece en calma, pero la calma rara vez dura.",
            "triumphant": "El aire vibra con la energía de la victoria, aunque el viaje continúa."
        }

        text = transition_templates.get(mood, "La historia continúa, guiada por fuerzas invisibles.")
        adapted = self.tone_adapter.adapt_tone(text, emotion=mood, intensity=intensity)
        return adapted
