import random
from core.emotion.emotional_continuity import EmotionalContinuity
from core.emotion.emotional_tracker import get_last_scene

# ================================================================
# 🧙‍♂️ ADAPTIVE NARRATOR PERSONA (Fase 6.18)
# ================================================================
# Define estilos narrativos dinámicos según el tono emocional
# global del mundo y la emoción dominante reciente.
# ================================================================


class AdaptiveNarratorPersona:
    def __init__(self):
        self.continuity = EmotionalContinuity()
        self.state = self.continuity.load_previous_state()
        self.baseline = self.continuity.get_emotional_baseline()
        self.voice_profile = self._select_voice(self.baseline.get("tone", "neutral"))

    # ------------------------------------------------------------
    # 🎭 Seleccionar voz narrativa según tono global
    # ------------------------------------------------------------
    def _select_voice(self, tone_label):
        voices = {
            "dark": {
                "name": "El Susurrante",
                "style": "poético, pausado, de tono bajo y ominoso",
                "intro": [
                    "Las sombras respiran entre las ruinas.",
                    "Todo parece detenido en un silencio que pesa como el plomo.",
                    "Las palabras se quiebran en la penumbra de la mente."
                ]
            },
            "melancholic": {
                "name": "El Cronista Silente",
                "style": "reflexivo, lírico y nostálgico",
                "intro": [
                    "El viento lleva consigo memorias de aquello que fue.",
                    "Cada paso parece un eco de tiempos mejores.",
                    "La tristeza camina a su lado, sin prisas."
                ]
            },
            "neutral": {
                "name": "El Relator",
                "style": "objetivo, equilibrado y descriptivo",
                "intro": [
                    "Los hechos se suceden sin dramatismo ni júbilo.",
                    "Nada en el aire indica peligro… aún.",
                    "El mundo gira, indiferente a la voluntad de los mortales."
                ]
            },
            "hopeful": {
                "name": "La Voz del Alba",
                "style": "vivaz, optimista y de ritmo ascendente",
                "intro": [
                    "El amanecer trae consigo nuevas promesas.",
                    "La esperanza florece incluso entre la piedra y la ceniza.",
                    "Una luz tenue guía sus pasos hacia un destino incierto, pero brillante."
                ]
            },
            "bright": {
                "name": "El Narrador Jubiloso",
                "style": "rápido, expresivo y lleno de energía",
                "intro": [
                    "¡El sol brilla alto y los corazones laten con fuerza!",
                    "Risas, pasos y ecos se mezclan en un coro de aventura.",
                    "Nada podrá detener a quienes sueñan en voz alta."
                ]
            }
        }
        return voices.get(tone_label, voices["neutral"])

    # ------------------------------------------------------------
    # 🧠 Generar introducción o transición narrativa adaptativa
    # ------------------------------------------------------------
    def narrate_intro(self):
        """Crea una narración de apertura con voz adaptativa."""
        scene = get_last_scene() or {}
        dominant_emotion = scene.get("dominant_emotion", "neutral")
        tone = self.baseline.get("tone", "neutral")

        intro = random.choice(self.voice_profile["intro"])
        bridge = self._emotion_bridge(dominant_emotion, tone)

        text = (
            f"🎙️ *{self.voice_profile['name']}* ({self.voice_profile['style']}):\n"
            f"{intro} {bridge}"
        )
        return text

    # ------------------------------------------------------------
    # 💬 Crear un “puente emocional” entre escenas
    # ------------------------------------------------------------
    def _emotion_bridge(self, emotion, tone):
        bridges = {
            "joy": {
                "dark": "La risa suena ajena en un lugar que olvidó la luz.",
                "melancholic": "Una sonrisa frágil rompe el velo del silencio.",
                "neutral": "Una leve alegría se cuela entre la rutina.",
                "hopeful": "El alma del grupo se enciende como una antorcha.",
                "bright": "El júbilo se desborda, imposible de contener."
            },
            "fear": {
                "dark": "El miedo es un compañero habitual en estas tierras.",
                "melancholic": "El temor y la tristeza se confunden en un mismo suspiro.",
                "neutral": "Una sombra de inquietud pasa, pero pronto se disipa.",
                "hopeful": "Incluso el miedo puede enseñar prudencia y valor.",
                "bright": "Una pizca de miedo aviva la chispa de la aventura."
            },
            "anger": {
                "dark": "La ira se convierte en un fuego que consume la cordura.",
                "melancholic": "El enojo se disuelve en amargura.",
                "neutral": "Un destello de frustración interrumpe la calma.",
                "hopeful": "El enojo se transforma en energía para seguir adelante.",
                "bright": "Una furia breve, chispeante, pero inofensiva."
            },
            "sadness": {
                "dark": "Las lágrimas se confunden con la lluvia.",
                "melancholic": "Cada lágrima es una historia sin final.",
                "neutral": "Un aire gris tiñe la jornada.",
                "hopeful": "Del dolor nace la fuerza de continuar.",
                "bright": "Incluso las lágrimas, hoy, brillan bajo el sol."
            },
            "neutral": {
                "dark": "Nada cambia, y en esa quietud hay algo inquietante.",
                "melancholic": "Todo sigue igual, pero el alma siente el peso del ayer.",
                "neutral": "El día transcurre sin sobresaltos.",
                "hopeful": "Una pausa antes del siguiente paso.",
                "bright": "Un respiro antes de la próxima carcajada."
            }
        }
        return bridges.get(emotion, bridges["neutral"]).get(tone, "")

    # ------------------------------------------------------------
    # 🧾 Acceso al perfil actual del narrador
    # ------------------------------------------------------------
    def get_persona_profile(self):
        """Devuelve el perfil actual de voz y estilo del narrador."""
        return self.voice_profile
