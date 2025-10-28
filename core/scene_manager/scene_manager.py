import json
from datetime import datetime
from core.tone_adapter.tone_adapter import ToneAdapter
from core.services.state_service import StateService
from core.services.emotion_service import EmotionService


class SceneManager:
    """
    Maneja las escenas narrativas activas, su persistencia y las transiciones.
    Integra el StoryDirector de forma diferida para evitar importación circular.
    """

    def __init__(self):
        self.state_service = StateService()
        self.emotion_service = EmotionService()
        self.tone_adapter = ToneAdapter()

        # 🔄 Importación diferida para evitar circular import
        from core.story_director.story_director import StoryDirector
        self.story_director = StoryDirector(self, self.tone_adapter)

    # ==========================================================
    # 🔹 CREACIÓN Y ACTUALIZACIÓN DE ESCENAS
    # ==========================================================
    def create_scene(self, title, description, scene_type="exploration",
                     objectives=None, npcs=None, environment=None):
        """Crea una nueva escena narrativa y la guarda en el estado actual."""
        scene = {
            "scene_id": datetime.utcnow().isoformat(),
            "title": title,
            "description": description,
            "description_adapted": "",
            "scene_type": scene_type,
            "emotion_intensity": 0.5,
            "status": "active",
            "objectives": objectives or [],
            "npcs": npcs or [],
            "environment": environment or {"lighting": "", "weather": "", "terrain": ""},
            "available_actions": [],
            "transitions": []
        }

        # Evaluar emoción base y adaptar descripción
        emotion_label = self.emotion_service.evaluate_emotion(description)
        scene["emotion"] = emotion_label if isinstance(emotion_label, str) else "neutral"
        scene["emotion_intensity"] = (
            emotion_label if isinstance(emotion_label, (float, int)) else 0.5
        )

        # ✅ Nuevo método adapt_tone
        scene["description_adapted"] = self.tone_adapter.adapt_tone(
            description=description,
            emotion=scene["emotion"],
            intensity=scene["emotion_intensity"],
            genre="heroic"
        )

        self.state_service.save_scene(scene)
        return scene

    # ==========================================================
    # 🔹 FINALIZAR ESCENA Y GENERAR TRANSICIÓN ADAPTATIVA
    # ==========================================================
    def close_scene(self, resolution_text: str = ""):
        """
        Marca la escena actual como 'completed', guarda su estado,
        y genera automáticamente la siguiente transición usando StoryDirector.
        """
        current_scene = self.state_service.load_scene()
        if not current_scene:
            return "⚠️ No hay escena activa para cerrar."

        current_scene["status"] = "completed"
        current_scene["resolution"] = resolution_text
        current_scene["ended_at"] = datetime.utcnow().isoformat()
        self.state_service.save_scene(current_scene)

        # Analizar emoción final del texto de cierre
        final_emotion = self.emotion_service.evaluate_emotion(resolution_text)
        self.state_service.update_emotion_level(final_emotion)

        # 🔸 Generar la siguiente transición narrativa adaptativa
        try:
            transition_text = self.story_director.generate_transition()
        except Exception as e:
            transition_text = f"La historia continúa sin un evento guiado. ({e})"

        # Crear nueva escena a partir del nodo generado
        new_scene = {
            "scene_id": datetime.utcnow().isoformat(),
            "title": "Nueva escena generada",
            "description": transition_text,
            # ✅ Aquí también usamos adapt_tone
            "description_adapted": self.tone_adapter.adapt_tone(
                description=transition_text,
                emotion="neutral",
                intensity=0.5,
                genre="heroic"
            ),
            "scene_type": "narrative_transition",
            "emotion_intensity": 0.5,
            "status": "active",
            "objectives": [],
            "npcs": [],
            "environment": {"lighting": "", "weather": "", "terrain": ""},
            "available_actions": [],
            "transitions": []
        }

        self.state_service.save_scene(new_scene)
        return transition_text

    # ==========================================================
    # 🔹 UTILIDADES DE CONSULTA
    # ==========================================================
    def get_active_scene(self):
        """Obtiene la escena activa desde el estado persistente."""
        return self.state_service.load_scene()

    def summarize_scene(self):
        """Devuelve un resumen narrativo del estado actual."""
        scene = self.get_active_scene()
        if not scene:
            return "No hay escena activa en este momento."

        summary = (
            f"🎭 *Escena actual:* {scene['title']}\n"
            f"📖 {scene['description_adapted']}\n"
            f"💫 Intensidad emocional: {scene.get('emotion_intensity', '?')}"
        )
        return summary
