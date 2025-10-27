"""
DirectorLink
-------------
Conecta los resultados del motor de juego (GameAPI) con el StoryDirector.
Permite que la narrativa se adapte a las acciones, tiradas o eventos
registrados por los jugadores.

Ejemplo:
- Un éxito crítico => intensifica la curva dramática y genera tono heroico.
- Un fallo grave => añade tensión y elige un nodo de traición o peligro.
- Descubrimiento o evento de descanso => activa nodo de calma o reflexión.
"""

from core.story_director.story_director import StoryDirector
from core.services.state_service import StateService
from core.services.emotion_service import EmotionService


class DirectorLink:
    def __init__(self, story_director: StoryDirector):
        self.story_director = story_director
        self.state_service = StateService()
        self.emotion_service = EmotionService()

    # ==========================================================
    # 🔹 PROCESAMIENTO DE RESULTADOS DE JUEGO
    # ==========================================================
    async def process_game_result(self, game_result: dict) -> str:
        """
        Recibe la respuesta JSON del GameAPI después de una acción del jugador
        y traduce su impacto narrativo para el StoryDirector.
        """
        if not game_result:
            return "El eco de tus acciones se desvanece sin respuesta del mundo."

        text_output = game_result.get("result", "")
        event_info = game_result.get("event", {})
        tone_modifier = 0

        # 1️⃣ Analizar éxito o fracaso
        success = game_result.get("success")
        if success is True:
            tone_modifier -= 1  # tono más esperanzador
        elif success is False:
            tone_modifier += 1  # tono más tenso o desesperado

        # 2️⃣ Analizar tipo de evento
        if event_info:
            event_type = event_info.get("event_type", "").lower()
            if "combate" in event_type:
                tone_modifier += 1
            elif "descubrimiento" in event_type:
                tone_modifier -= 1
            elif "traicion" in event_type:
                tone_modifier += 2

        # 3️⃣ Determinar nueva emoción global
        current_state = self.state_service.load_state()
        base_emotion = current_state.get("emotion_intensity", 3)
        new_emotion = max(1, min(5, base_emotion + tone_modifier))

        # 4️⃣ Actualizar estado emocional
        self.state_service.update_emotion_level(new_emotion)

        # 5️⃣ Generar transición adaptativa
        transition_text = self.story_director.generate_transition()

        return (
            f"{text_output}\n\n"
            f"🧭 *Cambio narrativo:*\n{transition_text}\n\n"
            f"💫 Intensidad emocional actual: {new_emotion}"
        )
