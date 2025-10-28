import re
from statistics import mean
from datetime import datetime

# ================================================================
# 💓 PLAYER EMOTIONAL RESONANCE (Fase 6.22)
# ================================================================
# Analiza el tono emocional de los mensajes del jugador
# y lo incorpora al ciclo emocional global.
# ================================================================


class PlayerResonance:
    def __init__(self):
        self.sentiment_log = []
        self.last_emotion = "neutral"
        self.resonance_strength = 0.0  # 0–1

        # Palabras clave por emoción
        self.emotion_map = {
            "joy": ["genial", "jajaja", "feliz", "bueno", "excelente", "victoria", "alegre", "divertido"],
            "fear": ["miedo", "asusta", "temo", "peligro", "cuidado", "nervioso", "tenso"],
            "anger": ["odio", "maldito", "enfado", "asco", "enojado", "furia"],
            "sadness": ["triste", "pérdida", "mal", "cansado", "deprimido", "fracaso"],
            "surprise": ["wow", "no puede ser", "increíble", "sorprendente", "qué", "vaya"],
        }

    # ------------------------------------------------------------
    # 🧠 Analizar mensaje del jugador
    # ------------------------------------------------------------
    def analyze_message(self, text: str):
        """
        Determina la emoción dominante del texto del jugador
        usando coincidencias simples de palabras clave.
        """
        text_lower = text.lower()
        emotion_scores = {}

        for emotion, keywords in self.emotion_map.items():
            score = sum(1 for word in keywords if re.search(rf"\b{word}\b", text_lower))
            if score > 0:
                emotion_scores[emotion] = score

        if not emotion_scores:
            self.last_emotion = "neutral"
            self.resonance_strength = 0.1
        else:
            # Seleccionar emoción dominante
            self.last_emotion = max(emotion_scores, key=emotion_scores.get)
            total = sum(emotion_scores.values())
            self.resonance_strength = min(1.0, emotion_scores[self.last_emotion] / total)

        # Registrar entrada
        self.sentiment_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "text": text,
            "emotion": self.last_emotion,
            "strength": round(self.resonance_strength, 2),
        })

        print(f"💬 [PlayerResonance] '{text}' → {self.last_emotion} ({self.resonance_strength})")
        return self.last_emotion, self.resonance_strength

    # ------------------------------------------------------------
    # 💞 Integrar emoción del jugador al MoodManager
    # ------------------------------------------------------------
    def apply_to_mood(self, mood_manager):
        """
        Ajusta la intensidad emocional o matiz del MoodManager
        según la emoción dominante del jugador.
        """
        delta = 0.0
        tone_adjust = None

        if self.last_emotion == "joy":
            delta = +0.1
            tone_adjust = "bright"
        elif self.last_emotion == "fear":
            delta = -0.1
            tone_adjust = "tense"
        elif self.last_emotion == "anger":
            delta = +0.15
            tone_adjust = "dark"
        elif self.last_emotion == "sadness":
            delta = -0.15
            tone_adjust = "melancholic"
        elif self.last_emotion == "surprise":
            delta = +0.05
            tone_adjust = "neutral"

        # Aplicar cambios
        mood_manager.adjust_intensity(delta)
        if tone_adjust:
            mood_manager.current_tone = tone_adjust

        print(f"💞 [PlayerResonance] Ajuste → tono '{tone_adjust}', intensidad {mood_manager.intensity:.2f}")
        return tone_adjust
