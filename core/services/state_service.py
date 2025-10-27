import json
import os

class StateService:
    """
    Servicio responsable de guardar y recuperar el estado narrativo actual
    (escena activa, emoción, progresión narrativa, etc.).
    """

    def __init__(self, file_path: str = "data/game_state.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # ==========================================================
    # 🔹 CARGA Y GUARDADO DE ESCENA
    # ==========================================================
    def load_scene(self):
        """Carga la escena activa desde el archivo de estado."""
        if not os.path.exists(self.file_path):
            return None
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("current_scene")
        except Exception:
            return None

    def save_scene(self, scene: dict):
        """Guarda la escena actual."""
        data = self._load_full_state()
        data["current_scene"] = scene
        self._save_full_state(data)

    def load_state(self):
        """Devuelve el estado completo."""
        return self._load_full_state()

    # ==========================================================
    # 🔹 ACTUALIZACIONES DE HISTORIA / EMOCIÓN
    # ==========================================================
    def update_emotion_level(self, level: int):
        data = self._load_full_state()
        data["emotion_intensity"] = level
        self._save_full_state(data)

    def update_story_flow(self, transition: dict):
        """Guarda una transición narrativa."""
        data = self._load_full_state()
        data.setdefault("story_transitions", []).append(transition)
        self._save_full_state(data)

    # ==========================================================
    # 🔹 MÉTODOS PRIVADOS
    # ==========================================================
    def _load_full_state(self):
        if not os.path.exists(self.file_path):
            return {}
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _save_full_state(self, data: dict):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
