from statistics import mean
from datetime import datetime

# ================================================================
# 🤝 GROUP EMOTIONAL COHESION (Fase 6.23)
# ================================================================
# Calcula la sincronía emocional del grupo de jugadores
# y ajusta el tono global de la campaña en función del estado colectivo.
# ================================================================

class GroupResonance:
    def __init__(self):
        self.group_log = []  # lista de dicts: {player, emotion, strength}
        self.last_cohesion = 1.0
        self.last_dominant = "neutral"
        self.timestamp = datetime.utcnow().isoformat()

    # ------------------------------------------------------------
    # 🧠 Registrar emoción de un jugador
    # ------------------------------------------------------------
    def record_player_emotion(self, player_name: str, emotion: str, strength: float):
        """Agrega la emoción de un jugador al registro temporal del grupo."""
        self.group_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "player": player_name,
            "emotion": emotion,
            "strength": strength
        })
        print(f"🧩 [GroupResonance] {player_name}: {emotion} ({strength:.2f})")

    # ------------------------------------------------------------
    # 🔍 Calcular cohesión emocional del grupo
    # ------------------------------------------------------------
    def compute_cohesion(self):
        """
        Evalúa el grado de sincronía emocional del grupo.
        Retorna: {dominant_emotion, cohesion_score, group_state}
        """
        if not self.group_log:
            return {"dominant_emotion": "neutral", "cohesion": 1.0, "group_state": "stable"}

        # Últimas emociones registradas
        emotions = [g["emotion"] for g in self.group_log[-10:]]
        strengths = [g["strength"] for g in self.group_log[-10:]]

        # Frecuencia emocional
        freq = {}
        for e in emotions:
            freq[e] = freq.get(e, 0) + 1
        dominant = max(freq, key=freq.get)

        # Cohesión = cuán uniforme es la distribución emocional
        cohesion = round(max(freq.values()) / len(emotions), 2)
        avg_strength = round(mean(strengths), 2)

        # Estado grupal
        if cohesion >= 0.8:
            state = "united"
        elif cohesion >= 0.5:
            state = "mixed"
        else:
            state = "fragmented"

        self.last_cohesion = cohesion
        self.last_dominant = dominant
        self.timestamp = datetime.utcnow().isoformat()

        print(f"🤝 [GroupResonance] Cohesión: {cohesion}, Dominante: {dominant}, Estado: {state}")
        return {
            "dominant_emotion": dominant,
            "cohesion": cohesion,
            "avg_strength": avg_strength,
            "group_state": state,
            "timestamp": self.timestamp
        }

    # ------------------------------------------------------------
    # 💞 Aplicar el estado del grupo al MoodManager
    # ------------------------------------------------------------
    def apply_to_mood(self, mood_manager, result):
        """
        Ajusta tono e intensidad global según cohesión grupal.
        - Grupos unidos → más intensidad y tono positivo.
        - Grupos fragmentados → tono tenso o neutro.
        """
        if not result:
            return

        cohesion = result["cohesion"]
        dominant = result["dominant_emotion"]
        delta = 0.0
        tone_adjust = "neutral"

        if result["group_state"] == "united":
            delta = +0.1
            if dominant in ["joy", "surprise"]:
                tone_adjust = "bright"
            elif dominant in ["fear", "anger"]:
                tone_adjust = "tense"
        elif result["group_state"] == "mixed":
            delta = 0.0
            tone_adjust = "neutral"
        else:  # fragmented
            delta = -0.1
            tone_adjust = "melancholic"

        mood_manager.adjust_intensity(delta)
        mood_manager.current_tone = tone_adjust

        print(f"🎭 [GroupResonance] Ajuste global → tono '{tone_adjust}', intensidad {mood_manager.intensity:.2f}")
        return tone_adjust
