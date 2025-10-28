# sam-telegram-bot/core/mood_manager/mood_manager.py
"""
MoodManager
------------
Controla el estado tonal global de la campaña.
Coordina la intensidad emocional, el perfil de género y
las transiciones suaves entre estados de ánimo detectados.

Este módulo se alimenta de las emociones analizadas por
EmotionService y las decisiones narrativas del StoryDirector.
"""

import os
import json
from datetime import datetime
from core.services.emotion_service import EmotionService


class MoodManager:
    """
    Mantiene y ajusta el clima emocional global de la historia.
    """

    def __init__(self, state_path: str = "data/game_state.json"):
        self.state_path = state_path
        self.emotion_service = EmotionService()

        # Estado tonal actual
        self.mood_state = "neutral"
        self.mood_intensity = 0.5
        self.genre_profile = "heroic"
        self.last_update = datetime.utcnow().isoformat()

        self._load_state()

    # ==========================================================
    # 📂 PERSISTENCIA DEL ESTADO
    # ==========================================================
    def _load_state(self):
        """Carga el estado global del mood desde disco."""
        if not os.path.exists(self.state_path):
            return
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.mood_state = data.get("mood_state", self.mood_state)
            self.mood_intensity = data.get("mood_intensity", self.mood_intensity)
            self.genre_profile = data.get("genre_profile", self.genre_profile)
            self.last_update = data.get("last_update", self.last_update)
        except Exception:
            pass

    def _save_state(self):
        """Guarda el estado global actual."""
        data = {
            "mood_state": self.mood_state,
            "mood_intensity": self.mood_intensity,
            "genre_profile": self.genre_profile,
            "last_update": self.last_update,
        }
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ==========================================================
    # 🧠 ANÁLISIS DE ESCENAS RECIENTES
    # ==========================================================
    def analyze_recent_scenes(self, scenes: list[dict]) -> tuple[str, float]:
        """
        Calcula el estado tonal promedio a partir de las últimas escenas.
        """
        if not scenes:
            return (self.mood_state, self.mood_intensity)

        total_intensity = 0
        emotion_counts = {}

        for scene in scenes:
            emo = scene.get("emotion", "neutral")
            val = scene.get("emotion_intensity", 0.5)
            total_intensity += val
            emotion_counts[emo] = emotion_counts.get(emo, 0) + 1

        # Emoción dominante y media de intensidad
        dominant = max(emotion_counts, key=emotion_counts.get)
        avg_intensity = total_intensity / max(len(scenes), 1)

        self.mood_state = dominant
        self.mood_intensity = round(avg_intensity, 2)
        self.last_update = datetime.utcnow().isoformat()
        self._save_state()

        return (self.mood_state, self.mood_intensity)

    # ==========================================================
    # 💫 NORMALIZACIÓN DEL MOOD
    # ==========================================================
    def normalize_mood(self) -> dict | None:
        """
        Si hay un salto emocional fuerte, genera una transición tonal sugerida.
        """
        if self.mood_intensity > 0.9:
            return {
                "from": self.mood_state,
                "to": "triumphant",
                "suggestion": "La tensión se disipa y surge una sensación de triunfo."
            }
        elif self.mood_intensity < 0.3:
            return {
                "from": self.mood_state,
                "to": "melancholic",
                "suggestion": "Un velo de melancolía cubre el ambiente, suavizando el ánimo del grupo."
            }
        return None

    # ==========================================================
    # ⚙️ AJUSTE DESDE FEEDBACK EMOCIONAL
    # ==========================================================
    def adjust_from_feedback(self, player_emotion: str, delta: float = 0.1):
        """
        Ajusta la intensidad del mood global según feedback emocional
        de los jugadores o el sistema.
        """
        level = self.emotion_service.emotion_to_level(player_emotion)
        # Mezcla ponderada entre el nivel base y el delta
        self.mood_intensity = min(1.0, max(0.0, self.mood_intensity + delta * (level - 0.5)))
        self.mood_state = player_emotion.lower()
        self.last_update = datetime.utcnow().isoformat()
        self._save_state()
        return self.mood_intensity

    # ==========================================================
    # 🎭 REFORZAR ALINEACIÓN CON EL GÉNERO
    # ==========================================================
    def align_to_genre(self):
        """
        Ajusta el tono general según el género narrativo actual.
        """
        if self.genre_profile == "dark_fantasy" and self.mood_intensity > 0.7:
            self.mood_state = "grim"
        elif self.genre_profile == "mystery" and self.mood_state not in ["mystical", "serene"]:
            self.mood_state = "mystical"
        elif self.genre_profile == "romantic" and self.mood_state in ["sadness", "melancholic"]:
            self.mood_state = "hopeful"
        self.last_update = datetime.utcnow().isoformat()
        self._save_state()

    # ==========================================================
    # 📊 ESTADO ACTUAL
    # ==========================================================
    def get_mood_summary(self) -> str:
        """Devuelve un resumen textual del estado tonal."""
        return (
            f"🌡️ Estado tonal global:\n"
            f"- Mood: {self.mood_state}\n"
            f"- Intensidad: {self.mood_intensity}\n"
            f"- Género: {self.genre_profile}\n"
            f"- Última actualización: {self.last_update}"
        )
