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

        mapped_mood = self._map_emotion_to_mood(dominant)
        self.mood_state = mapped_mood
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

    # ------------------------------------------------------------
    # 🧠 TRADUCTOR DE EMOCIONES → MOOD GLOBAL
    # ------------------------------------------------------------

    def _map_emotion_to_mood(self, emotion):
        """
        Traduce una emoción detectada (de escena o evento)
        a una categoría de mood coherente con emotional_scale.json.
        """
        emotion = (emotion or "").lower().strip()

        emotion_map = {
            # Positivos / heroicos
            "joy": "hopeful",
            "hope": "hopeful",
            "triumph": "triumphant",
            "victory": "triumphant",
            "confidence": "hopeful",
            "love": "romantic",

            # Neutrales / contemplativos
            "curiosity": "curious",
            "wonder": "curious",
            "discovery": "curious",
            "serenity": "serene",
            "peace": "serene",

            # Negativos / tensos
            "fear": "fearful",
            "terror": "fearful",
            "anger": "grim",
            "rage": "grim",
            "hatred": "grim",
            "conflict": "chaotic",
            "tension": "tense",
            "stress": "tense",

            # Tristes / melancólicos
            "sadness": "melancholic",
            "melancholy": "melancholic",
            "loss": "melancholic",
            "grief": "melancholic",

            # Espirituales / místicos
            "mystery": "mystical",
            "magic": "mystical",
            "dream": "mystical",
            "ritual": "mystical",

            # Catch-all
            "neutral": "serene",
            "unknown": "serene"
        }

        return emotion_map.get(emotion, "neutral")

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
    # 💬 RETROALIMENTACIÓN DESDE JUGADORES O STORY DIRECTOR
    # ------------------------------------------------------------

    def adjust_from_feedback(self, player_emotion: str, delta: float = 0.1):
        """
        Ajusta el tono según feedback emocional directo del jugador o del Story Director.
        Ej: player_emotion="bored", delta=+0.3  -> sube la intensidad.
        """
        if player_emotion in ["bored", "disengaged"]:
            self.mood_intensity = max(0.3, self.mood_intensity - 0.2)
        elif player_emotion in ["excited", "immersed"]:
            self.mood_intensity = min(1.0, self.mood_intensity + 0.2)
        elif player_emotion in ["fear", "tense"]:
            self.mood_intensity = min(1.0, self.mood_intensity + 0.1)
            self.mood_state = "tense"
        elif player_emotion in ["sad", "melancholic"]:
            self.mood_intensity = max(0.2, self.mood_intensity - 0.1)
            self.mood_state = "melancholic"
        else:
            self.mood_intensity = max(0, min(1, self.mood_intensity + delta))

        self.last_update = datetime.utcnow().isoformat()
        self._save_game_state()
        return self.mood_intensity
