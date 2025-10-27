import os
import json
from datetime import datetime

from core.scene_manager.scene_manager import SceneManager
from core.tone_adapter.tone_adapter import ToneAdapter
from core.mood_manager.mood_manager import MoodManager


# ================================================================
# 🎬 STORY DIRECTOR
# Motor de decisiones narrativas y gestor de flujo adaptativo
# ================================================================

class StoryDirector:
    """
    Coordina el flujo narrativo general de la campaña.
    Controla la creación y cierre de escenas, el tono adaptativo
    y el clima emocional global de la historia.
    """

    def __init__(self, base_path: str = "data/"):
        self.base_path = base_path
        self.scene_manager = SceneManager(os.path.join(base_path, "game_state.json"))
        self.tone_adapter = ToneAdapter(os.path.join(base_path, "emotion/emotional_scale.json"))
        self.mood_manager = MoodManager(os.path.join(base_path, "game_state.json"))

        self.state_path = os.path.join(base_path, "game_state.json")
        self.state = self._load_state()

    # ------------------------------------------------------------
    # 🔧 UTILIDADES INTERNAS
    # ------------------------------------------------------------

    def _load_state(self):
        if not os.path.exists(self.state_path):
            return {}
        with open(self.state_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _save_state(self):
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------
    # 🎭 CONTROL DE ESCENAS
    # ------------------------------------------------------------

    def create_scene(self, title: str, description: str, scene_type: str, emotion_intensity: float = 0.5):
        """
        Crea una nueva escena y la adapta según el mood global actual.
        """
        current_mood = self.mood_manager.mood_state
        genre_profile = self.mood_manager.genre_profile

        # 1️⃣ Crear la escena base
        new_scene = self.scene_manager.create_scene(
            title=title,
            description=description,
            scene_type=scene_type,
            emotion_intensity=emotion_intensity
        )

        # 2️⃣ Adaptar tono de descripción según mood global
        adapted_description = self.tone_adapter.adapt_tone(
            description=description,
            emotion=current_mood,
            intensity=emotion_intensity,
            genre=genre_profile
        )

        new_scene["description_adapted"] = adapted_description

        # 3️⃣ Registrar escena
        self.scene_manager.add_scene(new_scene)

        # 4️⃣ Analizar clima emocional global
        self._update_mood()

        return new_scene

    def close_scene(self, scene_id: str, result: str = None):
        """
        Cierra una escena y actualiza el mood global de la campaña.
        """
        closed_scene = self.scene_manager.close_scene(scene_id, result)
        if not closed_scene:
            return None

        # 🔄 Actualiza mood con últimas escenas
        self._update_mood()
        return closed_scene

    def _update_mood(self):
        """
        Analiza las últimas escenas para ajustar el mood global.
        Si hay saltos bruscos, sugiere una transición tonal.
        """
        recent_scenes = self.scene_manager.get_recent_scenes(limit=5)
        if not recent_scenes:
            return

        # 1️⃣ Calcular mood global
        mood, intensity = self.mood_manager.analyze_recent_scenes([
            {
                "scene_id": s.get("scene_id"),
                "emotion": s.get("emotion", "neutral"),
                "emotion_intensity": s.get("emotion_intensity", 0.5)
            }
            for s in recent_scenes
        ])

        # 2️⃣ Normalizar tono
        transition = self.mood_manager.normalize_mood()
        if transition:
            self._inject_transition_scene(transition)

        # 3️⃣ Reforzar alineación de género
        self.mood_manager.align_to_genre()

        print(f"[🎭 MoodManager] Estado tonal actualizado → {mood} ({intensity})")

    # ------------------------------------------------------------
    # 🧩 TRANSICIONES NARRATIVAS
    # ------------------------------------------------------------

    def _inject_transition_scene(self, transition_data: dict):
        """
        Inserta una escena puente si el MoodManager detecta un salto tonal fuerte.
        """
        if not transition_data:
            return

        title = "Transición emocional"
        description = transition_data.get("suggestion", "Un cambio sutil de atmósfera une las emociones opuestas.")
        scene_type = "transition"

        new_scene = self.scene_manager.create_scene(
            title=title,
            description=description,
            scene_type=scene_type,
            emotion_intensity=0.3
        )
        new_scene["description_adapted"] = self.tone_adapter.adapt_tone(
            description=description,
            emotion="neutral",
            intensity=0.3
        )
        self.scene_manager.add_scene(new_scene)
        print(f"[⚖️ Transition] Escena de transición generada entre moods {transition_data['from']} → {transition_data['to']}")

    # ------------------------------------------------------------
    # 💬 RETROALIMENTACIÓN EMOCIONAL (Jugador o sistema)
    # ------------------------------------------------------------

    def apply_feedback(self, player_emotion: str, delta: float = 0.1):
        """
        Ajusta la intensidad del mood global según la respuesta emocional del jugador o el ritmo narrativo.
        """
        new_intensity = self.mood_manager.adjust_from_feedback(player_emotion, delta)
        print(f"[🧠 Feedback] Intensidad tonal ajustada → {new_intensity} por emoción '{player_emotion}'")

    # ------------------------------------------------------------
    # 🧾 CONSULTAS Y UTILIDADES
    # ------------------------------------------------------------

    def get_current_mood(self):
        """
        Devuelve el estado tonal global actual.
        """
        return {
            "mood_state": self.mood_manager.mood_state,
            "mood_intensity": self.mood_manager.mood_intensity,
            "genre_profile": self.mood_manager.genre_profile,
            "last_update": self.mood_manager.last_update
        }

    def get_scene_history(self, limit: int = 10):
        """
        Retorna un resumen de las últimas escenas y su clima emocional.
        """
        recent = self.scene_manager.get_recent_scenes(limit=limit)
        return [
            {
                "title": s.get("title"),
                "emotion": s.get("emotion"),
                "emotion_intensity": s.get("emotion_intensity"),
                "status": s.get("status")
            }
            for s in recent
        ]


# ================================================================
# ✅ Ejemplo de uso (modo silencioso)
# ================================================================

if __name__ == "__main__":
    sd = StoryDirector(base_path="data/")
    print("🎬 Iniciando Story Director con Mood Manager integrado")

    # Crear una escena de ejemplo
    scene = sd.create_scene(
        title="El eco del hielo",
        description="Los héroes avanzan por un valle cubierto de escarcha, mientras el viento silba entre las ruinas.",
        scene_type="exploration",
        emotion_intensity=0.6
    )
    print("➡️ Escena creada:", scene["title"])

    # Cerrar escena y analizar mood
    sd.close_scene(scene_id=scene["scene_id"], result="descubren un portal sellado en hielo")

    # Consultar mood global
    print("🌡️ Estado tonal actual:", sd.get_current_mood())
