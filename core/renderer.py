import random
from datetime import datetime

from core.dialogue.auto_adaptive_dialogue import AutoAdaptiveDialogue

# ================================================================
# 🎨 RENDERER (Narrador de S.A.M.)
# ================================================================
# Genera descripciones y respuestas narrativas adaptadas al tono
# y emoción actuales. Integra Auto-Adaptive Dialogue (Fase 6.17).
# ================================================================


class Renderer:
    def __init__(self):
        self.adaptive_dialogue = AutoAdaptiveDialogue()
        self.last_summary = ""

    # ------------------------------------------------------------
    # 🏞️ Renderizar una nueva escena
    # ------------------------------------------------------------
    def render_scene(self, scene, tone: str = "neutral") -> str:
        """
        Genera la descripción inicial de una escena según el tono actual.
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
        }

        tone_descriptions = tone_map.get(tone, tone_map["neutral"])
        description = random.choice(tone_descriptions)
        npc_line = self.adaptive_dialogue.generate_dialogue(random.choice(["Elandra", "Sir Aethan", "Kael"]))

        result = f"{description}\n\n{npc_line}"
        self.last_summary = description
        return result

    # ------------------------------------------------------------
    # ⚔️ Renderizar respuesta a una acción
    # ------------------------------------------------------------
    def render_action(self, scene, action_text: str, tone: str = "neutral") -> str:
        """
        Crea una respuesta narrativa breve al input del jugador, influida por el tono global.
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
        }

        result = random.choice(tone_effects.get(tone, tone_effects["neutral"]))
        self.last_summary = result
        return result

    # ------------------------------------------------------------
    # 🧾 Resumen de la última escena
    # ------------------------------------------------------------
    def get_last_summary(self) -> str:
        """Devuelve la última descripción registrada."""
        return self.last_summary
