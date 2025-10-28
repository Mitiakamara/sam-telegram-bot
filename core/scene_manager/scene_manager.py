import os
import json
import uuid
from datetime import datetime
from typing import List, Optional

# ================================================================
# 🧩 Scene Manager
# ================================================================
# Administra las escenas activas de la sesión, sus transiciones y
# el registro histórico de emociones (Fase 6.10).
# ================================================================

from core.emotion.emotional_tracker import log_scene, get_emotional_summary


# ------------------------------------------------
# 🧱 MODELO DE ESCENA
# ------------------------------------------------
class Scene:
    def __init__(
        self,
        title: str,
        description: str,
        scene_type: str = "progress",
        objectives: Optional[List[str]] = None,
        npcs: Optional[List[str]] = None,
        environment: Optional[dict] = None,
        available_actions: Optional[List[str]] = None,
    ):
        self.scene_id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.scene_type = scene_type
        self.objectives = objectives or []
        self.npcs = npcs or []
        self.environment = environment or {
            "lighting": "",
            "weather": "",
            "terrain": ""
        }
        self.available_actions = available_actions or []
        self.status = "active"
        self.emotion_intensity = 3
        self.timestamp_start = datetime.utcnow().isoformat()
        self.timestamp_end = None

    def to_dict(self):
        return {
            "scene_id": self.scene_id,
            "title": self.title,
            "description": self.description,
            "scene_type": self.scene_type,
            "objectives": self.objectives,
            "npcs": self.npcs,
            "environment": self.environment,
            "available_actions": self.available_actions,
            "status": self.status,
            "emotion_intensity": self.emotion_intensity,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
        }


# ------------------------------------------------
# 🎬 SCENE MANAGER
# ------------------------------------------------
class SceneManager:
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self.current_scene: Optional[Scene] = None
        self.scenes_log: List[dict] = []

    # ------------------------------
    # Crear una nueva escena
    # ------------------------------
    def create_scene(self, title: str, description: str, scene_type: str = "progress"):
        self.current_scene = Scene(title=title, description=description, scene_type=scene_type)
        print(f"\n🌅 Nueva escena creada: {self.current_scene.title}")
        return self.current_scene

    # ------------------------------
    # Obtener escena activa
    # ------------------------------
    def get_current_scene(self) -> Optional[Scene]:
        return self.current_scene

    # ------------------------------
    # Cerrar la escena actual
    # ------------------------------
    def end_scene(self, tone_adapter, mood_manager, story_director, action_handler, renderer):
        """
        Marca la escena actual como finalizada, registra su estado emocional
        y la guarda en el historial mediante Emotional Tracker.
        """
        if not self.current_scene:
            print("[⚠️] No hay escena activa para cerrar.")
            return None

        scene = self.current_scene
        try:
            # 1️⃣ Actualiza estado y tiempos
            scene.status = "completed"
            scene.timestamp_end = datetime.utcnow().isoformat()

            # 2️⃣ Extrae información emocional y contextual
            emotion_vector = tone_adapter.get_current_emotions() if hasattr(tone_adapter, "get_current_emotions") else {}
            dominant_emotion = tone_adapter.get_dominant() if hasattr(tone_adapter, "get_dominant") else "neutral"
            current_tone = getattr(mood_manager, "current_tone", "neutral")
            outcome = getattr(story_director, "last_outcome", "mixed")
            player_actions = getattr(action_handler, "get_last_actions", lambda: [])()
            scene_summary = getattr(renderer, "get_last_summary", lambda: "")()

            # 3️⃣ Registrar en Emotional Tracker
            log_scene({
                "scene_id": scene.scene_id,
                "title": scene.title,
                "scene_type": scene.scene_type,
                "emotion_vector": emotion_vector,
                "dominant_emotion": dominant_emotion,
                "tone": current_tone,
                "summary": scene_summary,
                "player_actions": player_actions,
                "outcome": outcome,
            })

            # 4️⃣ Registrar también en memoria local
            self.scenes_log.append(scene.to_dict())
            self._save_scenes()

            # 5️⃣ Mostrar resumen en consola
            summary = get_emotional_summary()
            print(f"\n📘 Escena finalizada: {scene.title}")
            print(f"   Dominante: {dominant_emotion} | Tono: {current_tone}")
            print(f"   Tendencia global → {summary.get('tone_trend')} ({summary.get('dominant_emotion')})")

            # 6️⃣ Reinicia la escena activa
            self.current_scene = None
            return scene

        except Exception as e:
            print(f"[❌ ERROR] No se pudo registrar la escena: {e}")
            return scene

    # ------------------------------
    # Guardar log local de escenas
    # ------------------------------
    def _save_scenes(self):
        os.makedirs(os.path.join(self.data_path, "emotion"), exist_ok=True)
        path = os.path.join(self.data_path, "emotion", "scene_log.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"scenes": self.scenes_log}, f, indent=4, ensure_ascii=False)

    # ------------------------------
    # Resetear historial local
    # ------------------------------
    def reset_local_log(self):
        self.scenes_log = []
        path = os.path.join(self.data_path, "emotion", "scene_log.json")
        if os.path.exists(path):
            os.remove(path)
        print("🧹 Historial local de escenas reiniciado.")


# ------------------------------------------------
# 🧪 DEMO LOCAL
# ------------------------------------------------
if __name__ == "__main__":
    print("🧩 Ejecutando demo de SceneManager con Emotional Tracker...\n")

    # Simular dependencias mínimas
    class DummyTone:
        def get_current_emotions(self): return {"joy": 0.5, "fear": 0.2, "sadness": 0.1}
        def get
