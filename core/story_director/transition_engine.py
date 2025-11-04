# ================================================================
# 🔁 TRANSITION ENGINE – Fase 7.4
# ================================================================
# Decide la siguiente escena según el estado emocional global
# y el tipo de evento narrativo ocurrido.
# ================================================================

import random


class TransitionEngine:
    """
    Mapea emociones y eventos a posibles próximas escenas.
    """

    def __init__(self):
        # Mapa de transiciones posibles
        self.transition_map = {
            "progress": {
                "combat_victory": "triumph_scene.json",
                "setback": "tension_scene.json",
                "neutral": "progress_scene.json"
            },
            "tension": {
                "fear_trigger": "setback_scene.json",
                "success": "progress_scene.json",
                "neutral": "tension_scene.json"
            },
            "setback": {
                "rally": "progress_scene.json",
                "loss": "setback_scene.json",
                "neutral": "tension_scene.json"
            },
            "triumph": {
                "calm": "progress_scene.json",
                "loss": "setback_scene.json",
                "neutral": "triumph_scene.json"
            }
        }

    def get_next_scene(self, current_emotion: str, event_type: str) -> str:
        """
        Devuelve el nombre del archivo JSON de la próxima escena.
        Si no hay coincidencia directa, elige una aleatoria de fallback.
        """
        emotion_map = self.transition_map.get(current_emotion, {})
        next_scene = emotion_map.get(event_type)

        if not next_scene:
            # Fallback aleatorio entre opciones del mismo estado
            if emotion_map:
                next_scene = random.choice(list(emotion_map.values()))
            else:
                # fallback genérico
                next_scene = "progress_scene.json"

        return next_scene
