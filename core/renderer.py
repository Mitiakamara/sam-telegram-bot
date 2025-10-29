import random
from datetime import datetime

# ================================================================
# 🎨 RENDERER — Narrador dinámico de S.A.M.
# ================================================================
# Genera descripciones y respuestas narrativas adaptadas al tono
# emocional global, los blends activos y el estilo narrativo
# evolutivo de la campaña.
# ================================================================

from core.dialogue.auto_adaptive_dialogue import AutoAdaptiveDialogue
#from core.renderer.style_evolution import NarrativeStyleEvolution


class Renderer:
    def __init__(self):
        self.adaptive_dialogue = AutoAdaptiveDialogue()
        self.last_summary = ""

    # ------------------------------------------------------------
    # 🏞️ Renderizar una nueva escena
    # ------------------------------------------------------------
    def render_scene(self, scene, tone: str = "neutral", mood_manager=None):
        """
        Genera la descripción inicial de una escena según el tono actual,
        integrando estilo narrativo evolutivo y diálogos adaptativos.
        """
        tone_map = {
            "dark": [
                "La penumbra domina el ambiente, cada sombra parece tener vida propia.",
                "El aire es denso y pesado, con el eco distante de pasos que no existen.",
                "Una calma tensa envuelve el lugar, como si el mundo contuviera el aliento."
            ],
            "melancholic": [
                "Un dejo de tristeza impregna el aire, mientras el viento susurra nombres olvidados.",
                "Todo parece detenido en un instante de melancolía, entre recuerdos y silencios.",
                "Las luces son suaves, pero hay algo doliente en la quietud del entorno."
            ],
            "neutral": [
                "El entorno permanece estable, sin sobresaltos, a la espera de lo inesperado.",
                "Todo está tranquilo, aunque una tensión sutil recorre el aire.",
                "Nada parece fuera de lugar, pero la sensación de anticipación persiste."
            ],
            "hopeful": [
                "Una brisa cálida anuncia que el peligro podría haber pasado.",
                "Los rayos del sol iluminan el camino con promesas de renovación.",
                "El grupo respira aliviado, sabiendo que aún hay motivos para avanzar."
            ],
            "bright": [
                "La alegría impregna el aire, risas y música acompañan el paso del grupo.",
                "Colores vivos y voces optimistas llenan el ambiente de energía.",
                "Es un momento de calma y celebración en medio de la incertidumbre."
            ],
            "tense": [
                "El aire vibra con expectación, cada paso suena más fuerte de lo normal.",
                "Una sensación de inminencia se apodera del ambiente.",
                "Los corazones laten al ritmo del peligro que se aproxima."
            ]
        }

        tone_descriptions = tone_map.get(tone, tone_map["neutral"])
        description = random.choice(tone_descriptions)

        # Generar diálogo adaptativo de NPC
        npc_line = self.adaptive_dialogue.generate_dialogue(
            random.choice(["Elandra", "Sir Aethan", "Kael"])
        )

        base_text = f"{description}\n\n{npc_line}"

        # Aplicar estilo narrativo evolutivo si hay MoodManager
        if mood_manager:
            style_engine = NarrativeStyleEvolution(mood_manager)
            styled_text = style_engine.stylize_text(base_text)
            self.last_summary = styled_text
            return styled_text

        self.last_summary = base_text
        return base_text

    # ------------------------------------------------------------
    # ⚔️ Renderizar respuesta a una acción del jugador
    # ------------------------------------------------------------
    def render_action(self, scene, action_text: str, tone: str = "neutral", mood_manager=None):
        """
        Crea una respuesta narrativa breve influida por el tono global y
        ajustada al estilo narrativo actual.
        """
        tone_effects = {
            "dark": [
                f"La acción '{action_text}' se ve envuelta por un silencio inquietante.",
                f"El eco de '{action_text}' resuena como un presagio en la oscuridad.",
                f"Algo invisible parece observar cada movimiento mientras intentas '{action_text}'."
            ],
            "melancholic": [
                f"'{action_text}' se realiza con un aire de resignación.",
                f"Cada gesto al intentar '{action_text}' parece más lento, como si pesara el pasado.",
                f"Una nostalgia sutil acompaña tu intento de '{action_text}'."
            ],
            "neutral": [
                f"Ejecutas '{action_text}' sin contratiempos visibles.",
                f"No ocurre nada fuera de lo común al intentar '{action_text}'.",
                f"El entorno responde con calma mientras realizas '{action_text}'."
            ],
            "hopeful": [
                f"'{action_text}' trae un soplo de confianza al grupo.",
                f"Tu intento de '{action_text}' ilumina el ambiente con determinación.",
                f"La energía del grupo se eleva mientras realizas '{action_text}'."
            ],
            "bright": [
                f"'{action_text}' genera risas y alivio entre tus compañeros.",
                f"El ambiente se llena de optimismo mientras ejecutas '{action_text}'.",
                f"Tu acción '{action_text}' inspira al resto del grupo. 🌟"
            ],
            "tense": [
                f"'{action_text}' interrumpe el silencio, haciendo que todos contengan la respiración.",
                f"Tu intento de '{action_text}' se siente precipitado, el aire se espesa.",
                f"El más leve error al intentar '{action_text}' podría costar caro."
            ]
        }

        result = random.choice(tone_effects.get(tone, tone_effects["neutral"]))

        # Aplicar evolución estilística
        if mood_manager:
            style_engine = NarrativeStyleEvolution(mood_manager)
            result = style_engine.stylize_text(result)

        self.last_summary = result
        return result

    # ------------------------------------------------------------
    # 🧾 Último resumen narrativo
    # ------------------------------------------------------------
    def get_last_summary(self) -> str:
        """Devuelve la última descripción o reacción registrada."""
        return self.last_summary
