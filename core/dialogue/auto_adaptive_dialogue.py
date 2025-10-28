import random
from core.emotion.emotional_continuity import EmotionalContinuity
from core.emotion.emotional_tracker import get_last_scene

# ================================================================
# 🗣️ AUTO-ADAPTIVE DIALOGUE (Fase 6.17)
# ================================================================
# Genera líneas de diálogo adaptadas al tono emocional global y
# la emoción dominante de la escena actual.
# ================================================================


class AutoAdaptiveDialogue:
    def __init__(self):
        self.continuity = EmotionalContinuity()
        self.state = self.continuity.load_previous_state()
        self.baseline = self.continuity.get_emotional_baseline()

    # ------------------------------------------------------------
    # 🧠 Determinar estilo global según el tono del mundo
    # ------------------------------------------------------------
    def _get_style_by_tone(self, tone_label):
        styles = {
            "dark": "voz baja, palabras tensas, frases cortas",
            "melancholic": "voz suave, tono pensativo",
            "neutral": "voz calmada y controlada",
            "hopeful": "voz firme, tono cálido y optimista",
            "bright": "voz alegre y desenfadada",
        }
        return styles.get(tone_label, "voz neutral y sin emoción visible")

    # ------------------------------------------------------------
    # 💬 Generar diálogo adaptado al estado emocional
    # ------------------------------------------------------------
    def generate_dialogue(self, npc_name: str = "NPC") -> str:
        """Crea una línea de diálogo coherente con el clima emocional global."""
        tone_label = self.baseline.get("tone", "neutral")
        scene = get_last_scene() or {}
        emotion = scene.get("dominant_emotion", "neutral")

        style = self._get_style_by_tone(tone_label)
        emotion_line = self._get_line_by_emotion(emotion, tone_label)

        line = f"{npc_name} ({style}): {emotion_line}"
        return line

    # ------------------------------------------------------------
    # 💫 Selección de frase base por emoción dominante
    # ------------------------------------------------------------
    def _get_line_by_emotion(self, emotion, tone_label):
        lines = {
            "joy": [
                "¡Hoy es un buen día para cantar nuestras victorias!",
                "No todo está perdido; aún hay esperanza.",
                "Tu risa me recuerda que seguimos vivos.",
            ],
            "fear": [
                "Algo no anda bien… ¿lo sientes?",
                "Mantén la voz baja, hay ojos observando.",
                "No me gusta este silencio… parece que nos espera algo.",
            ],
            "anger": [
                "¡Ya basta! No pienso huir otra vez.",
                "Mi sangre hierve, y no por el frío.",
                "No soporto más tanta injusticia.",
            ],
            "sadness": [
                "Las sombras pesan más con cada paso.",
                "No sé si quiero seguir adelante… pero no puedo detenerme.",
                "Cada pérdida deja una herida que no cicatriza.",
            ],
            "surprise": [
                "¡Por los dioses! No esperaba eso.",
                "¿Has visto eso? Ni los ancianos lo creerían.",
                "El destino tiene un sentido del humor retorcido.",
            ],
            "neutral": [
                "Sigamos adelante, sin perder el ritmo.",
                "No hay señales claras… pero algo se avecina.",
                "Otro día más en estas tierras inciertas.",
            ],
        }

        chosen = random.choice(lines.get(emotion, lines["neutral"]))

        # Pequeño sesgo de tono
        if tone_label in ["dark", "melancholic"]:
            chosen = chosen.replace("!", ".").replace("¡", "").replace("…", ".").capitalize()
        elif tone_label in ["hopeful", "bright"]:
            chosen += " 🌟"

        return chosen


# ------------------------------------------------------------
# 🧪 DEMO LOCAL
# ------------------------------------------------------------
if __name__ == "__main__":
    aad = AutoAdaptiveDialogue()
    for _ in range(5):
        print(aad.generate_dialogue("Elandra"))
