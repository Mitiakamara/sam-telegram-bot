import json
import os
from datetime import datetime
from statistics import mean

# ================================================================
# 🎭 Mood Manager – Gestor de tono global de campaña
# ================================================================

class MoodManager:
    """
    Controla y mantiene la coherencia emocional y tonal
    de la campaña completa. Evalúa las últimas escenas,
    ajusta el clima narrativo y sincroniza el tono global
    con el Story Director y el Tone Adapter.
    """

    MOOD_PROFILES = {
        "heroic": ["hopeful", "triumphant", "bright", "courageous"],
        "dark_fantasy": ["grim", "tense", "melancholic", "foreboding"],
        "mystery": ["curious", "tense", "mystical", "uneasy"],
        "exploration": ["curious", "serene", "wonder", "awe"],
        "horror": ["fearful", "oppressive", "desperate", "unsettling"]
    }

    def __init__(self, game_state_path: str):
        self.game_state_path = game_state_path
        self.data = self._load_game_state()
        self.mood_state = self.data.get("mood_manager", {}).get("campaign_mood_state", "neutral")
        self.mood_intensity = self.data.get("mood_manager", {}).get("mood_intensity", 0.5)
        self.genre_profile = self.data.get("mood_manager", {}).get("genre_profile", "heroic")
        self.history = self.data.get("mood_manager", {}).get("history", [])
        self.last_update = self.data.get("mood_manager", {}).get("last_update")

    # ------------------------------------------------------------
    # 🧩 UTILIDADES INTERNAS
    # ------------------------------------------------------------

    def _load_game_state(self):
        if not os.path.exists(self.game_state_path):
            return {}
        with open(self.game_state_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _save_game_state(self):
        self.data["mood_manager"] = {
            "campaign_mood_state": self.mood_state,
            "mood_intensity": self.mood_intensity,
            "genre_profile": self.genre_profile,
            "last_update": self.last_update,
            "history": self.history[-20:]  # guarda solo las últimas 20 escenas
        }
        with open(self.game_state_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------
    # 🔍 ANÁLISIS Y CÁLCULO DE MOOD GLOBAL
    # ------------------------------------------------------------

    def analyze_recent_scenes(self, recent_scenes: list):
        """
        Recibe una lista de escenas recientes desde SceneManager.
        Cada escena debe incluir:
        {
            "scene_id": str,
            "emotion": str,
            "emotion_intensity": float
        }
        """
        if not recent_scenes:
            return self.mood_state, self.mood_intensity

        emotions = [s["emotion"] for s in recent_scenes if "emotion" in s]
        intensities = [s.get("emotion_intensity", 0.5) for s in recent_scenes]

        # Determina emoción dominante
        dominant = self._most_common(emotions)
        avg_intensity = mean(intensities)

        self.mood_state = self._map_emotion_to_mood(dominant)
        self.mood_intensity = round(avg_intensity, 2)
        self.last_update = datetime.utcnow().isoformat()

        # Guarda en historial
        self.history.append({
            "scene_id": recent_scenes[-1].get("scene_id", "unknown"),
            "mood": self.mood_state,
            "intensity": self.mood_intensity,
            "timestamp": self.last_update
        })

        self._save_game_state()
        return self.mood_state, self.mood_intensity

    def _most_common(self, items):
        return max(set(items), key=items.count) if items else "neutral"

    def _map_emotion_to_mood(self, emotion):
        """
        Traduce una emoción de escena (e.g., 'fear', 'hope', 'sadness')
        a un estado de mood más abstracto de campaña.
        """
        mapping = {
            "joy": "hopeful",
            "hope": "hopeful",
            "triumph": "triumphant",
            "fear": "tense",
            "sadness": "melancholic",
            "anger": "grim",
            "curiosity": "mystical",
            "serenity": "serene",
            "anticipation": "tense",
            "conflict": "chaotic",
            "neutral": "neutral"
        }
        return mapping.get(emotion.lower(), "neutral")

    # ------------------------------------------------------------
    # ⚖️ AJUSTE DE TONO Y NORMALIZACIÓN
    # ------------------------------------------------------------

    def normalize_mood(self):
        """
        Evita saltos bruscos en el tono global.
        Si el cambio de mood supera un umbral,
        propone una escena de transición.
        """
        if len(self.history) < 2:
            return None

        last = self.history[-1]
        prev = self.history[-2]

        delta = abs(last["intensity"] - prev["intensity"])
        if delta > 0.4:
            transition = self._suggest_transition(prev["mood"], last["mood"])
            return transition
        return None

    def _suggest_transition(self, prev_mood, new_mood):
        """
        Devuelve una sugerencia narrativa para suavizar la transición.
        """
        return {
            "type": "transition_scene",
            "from": prev_mood,
            "to": new_mood,
            "suggestion": f"Introduce una breve escena de respiro o reflexión antes de pasar de '{prev_mood}' a '{new_mood}'."
        }

    # ------------------------------------------------------------
    # 🧭 PERFIL DE GÉNERO Y ALINEACIÓN TONAL
    # ------------------------------------------------------------

    def align_to_genre(self):
        """
        Atrae el mood global hacia el perfil tonal del género.
        """
        target_profile = self.MOOD_PROFILES.get(self.genre_profile, [])
        if not target_profile:
            return self.mood_state

        if self.mood_state not in target_profile:
            # Empuja el estado hacia el más cercano del perfil
            self.mood_state = target_profile[0]
            self._save_game_state()

        return self.mood_state

    # ------------------------------------------------------------
    # 📊 RETROALIMENTACIÓN DESDE EL STORY DIRECTOR
    # ------------------------------------------------------------

    def adjust_from_feedback(self, player_emotion: str, delta: float):
        """
        Ajusta el tono según feedback emocional directo del jugador o del Story Director.
        Ej: player_emotion="bored", delta=+0.3  -> sube la intensidad.
        """
        if player_emotion in ["bored", "disengaged"]:
            self.mood_intensity = max(0.3, self.mood_intensity - 0.2)
        elif player_emotion in ["excited", "immersed"]:
            self.mood_intensity = min(1.0, self.mood_intensity + 0.2)
        else:
            self.mood_intensity = max(0, min(1, self.mood_intensity + delta))

        self._save_game_state()
        return self.mood_intensity

# ================================================================
# ✅ Uso ejemplo (silencioso)
# ================================================================

if __name__ == "__main__":
    mm = MoodManager("data/game_state.json")
    scenes = [
        {"scene_id": "A01", "emotion": "fear", "emotion_intensity": 0.8},
        {"scene_id": "A02", "emotion": "sadness", "emotion_intensity": 0.6}
    ]
    mood, intensity = mm.analyze_recent_scenes(scenes)
    print("Mood global:", mood, "| Intensidad:", intensity)
    print("Transición sugerida:", mm.normalize_mood())
