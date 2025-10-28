import os
import json
from datetime import datetime
from core.tone_adapter.tone_adapter import ToneAdapter
from core.services.state_service import StateService
from core.services.emotion_service import EmotionService


class SceneManager:
    """
    Maneja las escenas narrativas activas, su persistencia y las transiciones.
    Integra el StoryDirector y mantiene un historial de escenas completadas.
    """

    def __init__(self, base_path: str = "data/"):
        self.base_path = base_path
        self.state_service = StateService()
        self.emotion_service = EmotionService()
        self.tone_adapter = ToneAdapter()
        self.history_path = os.path.join(base_path, "scenes_history.json")

        # 🔄 Importación diferida para evitar circular import
        from core.story_director.story_director import StoryDirector
        self.story_director = StoryDirector(self, self.tone_adapter)

        # Crear archivo de historial si no existe
        self._ensure_history_file()

    # ==========================================================
    # 📂 UTILIDADES INTERNAS
    # ==========================================================
    def _ensure_history_file(self):
        """Crea el archivo de historial si no existe."""
        os.makedirs(self.base_path, exist_ok=True)
        if not os.path.exists(self.history_path):
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def _append_to_history(self, scene: dict):
        """Agrega una escena cerrada al historial de campaña."""
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

        # No duplicar escenas con mismo ID
        if not any(s.get("scene_id") == scene.get("scene_id") for s in history):
            history.append(scene)
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)

    # ==========================================================
    # 🎭 CREACIÓN DE ESCENAS
    # ==========================================================
    def create_scene(self, title, description, scene_type="exploration",
                     objectives=None, npcs=None, environment=None):
        """Crea una nueva escena narrativa y la guarda como activa."""
        emotion_label, emotion_intensity = self.emotion_service.evaluate_emotion(description)

        scene = {
            "scene_id": datetime.utcnow().isoformat(),
            "title": title,
            "description": description,
            "description_adapted": self.tone_adapter.adapt_tone(
                description=description,
                emotion=emotion_label,
                intensity=emotion_intensity,
                genre="heroic"
            ),
            "scene_type": scene_type,
            "emotion": emotion_label,
            "emotion_intensity": emotion_intensity,
            "status": "active",
            "objectives": objectives or [],
            "npcs": npcs or [],
            "environment": environment or {"lighting": "", "weather": "", "terrain": ""},
            "available_actions": [],
            "transitions": [],
            "created_at": datetime.utcnow().isoformat()
        }

        self.state_service.save_scene(scene)
        return scene

    # ==========================================================
    # 🎬 CIERRE Y TRANSICIÓN DE ESCENAS
    # ==========================================================
    def close_scene(self, resolution_text: str = ""):
        """
        Marca la escena actual como 'completed', guarda su estado
        y genera automáticamente la siguiente transición narrativa.
        """
        current_scene = self.state_service.load_scene()
        if not current_scene:
            return "⚠️ No hay escena activa para cerrar."

        current_scene["status"] = "completed"
        current_scene["resolution"] = resolution_text
        current_scene["ended_at"] = datetime.utcnow().isoformat()

        # Analizar emoción final
        emotion_label, emotion_intensity = self.emotion_service.evaluate_emotion(resolution_text)
        current_scene["emotion"] = emotion_label
        current_scene["emotion_intensity"] = emotion_intensity

        # Guardar escena actual y añadir al historial
        self.state_service.save_scene(current_scene)
        self._append_to_history(current_scene)

        # 🔸 Generar la transición adaptativa
        try:
            transition_text = self.story_director.generate_transition()
        except Exception as e:
            transition_text = f"La historia continúa sin un evento guiado. ({e})"

        # Crear nueva escena a partir de la transición
        new_scene = {
            "scene_id": datetime.utcnow().isoformat(),
            "title": "Nueva escena generada",
            "description": transition_text,
            "description_adapted": self.tone_adapter.adapt_tone(
                description=transition_text,
                emotion="neutral",
                intensity=0.5,
                genre="heroic"
            ),
            "scene_type": "narrative_transition",
            "emotion": "neutral",
            "emotion_intensity": 0.5,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "objectives": [],
            "npcs": [],
            "environment": {"lighting": "", "weather": "", "terrain": ""},
            "available_actions": [],
            "transitions": []
        }

        self.state_service.save_scene(new_scene)
        return transition_text

    # ==========================================================
    # 🔍 CONSULTAS
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
            f"💫 Emoción: `{scene.get('emotion', 'neutral')}` "
            f"(intensidad {scene.get('emotion_intensity', 0.5)})"
        )
        return summary
