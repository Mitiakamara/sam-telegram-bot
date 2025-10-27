# sam-telegram-bot/core/story_director/director_link.py
"""
DirectorLink
-------------
Puente entre el motor de juego (GameService) y el StoryDirector.

Interpreta las respuestas del juego (acciones, resultados, eventos)
y decide cómo deben afectar la narrativa y el tono global de campaña.
"""

from core.renderer import render


class DirectorLink:
    """
    Interpreta resultados del GameService y los conecta con el StoryDirector.
    - Extrae emociones o temas de los resultados.
    - Informa al MoodManager para ajustar el tono global.
    - Devuelve texto narrativo adaptado.
    """

    def __init__(self, story_director):
        self.story_director = story_director
        # MoodManager opcional (si StoryDirector lo posee)
        self.mood_manager = getattr(story_director, "mood_manager", None)

    # ==========================================================
    # 🔹 PROCESAR RESULTADOS DEL MOTOR DE JUEGO
    # ==========================================================
    async def process_game_result(self, game_result: dict):
        """
        Recibe un resultado del GameService, analiza el contexto narrativo
        y adapta el texto según el tono actual.
        """
        try:
            # Estructura esperada de game_result:
            # {
            #   "action": "attack goblin",
            #   "outcome": "success",
            #   "emotion": "triumph",
            #   "description": "El golpe atraviesa la defensa del enemigo...",
            #   "event": {...} (opcional)
            # }

            action = game_result.get("action", "")
            outcome = game_result.get("outcome", "")
            emotion = game_result.get("emotion", "neutral")
            description = game_result.get("description", "")
            event = game_result.get("event", None)

            # --------------------------------------------------
            # 🎭 Ajustar el clima narrativo
            # --------------------------------------------------
            if self.mood_manager:
                try:
                    # Ajuste tonal automático según emoción detectada
                    delta = self._emotion_to_delta(emotion)
                    self.mood_manager.adjust_from_feedback(emotion, delta)
                except Exception:
                    pass

            # --------------------------------------------------
            # ✍️ Generar texto adaptado según tono
            # --------------------------------------------------
            adapted_text = description
            if hasattr(self.story_director, "tone_adapter"):
                adapted_text = self.story_director.tone_adapter.adapt_tone(
                    description=description,
                    emotion=emotion,
                    intensity=getattr(self.mood_manager, "mood_intensity", 0.5)
                    if self.mood_manager else 0.5,
                    genre=getattr(self.mood_manager, "genre_profile", "heroic")
                    if self.mood_manager else "heroic"
                )

            # --------------------------------------------------
            # 🔮 Procesar evento especial
            # --------------------------------------------------
            event_text = ""
            if event:
                title = event.get("event_title", "Evento")
                e_type = event.get("event_type", "general")
                narration = event.get("event_narration", "")
                event_text = f"\n\n🔮 *{title}* ({e_type.title()}):\n{narration}"

            # Texto final
            narrative = f"{adapted_text}{event_text}"

            return render(narrative)

        except Exception as e:
            return render(f"[Error en DirectorLink] No se pudo procesar el resultado del juego: {e}")

    # ==========================================================
    # 🔹 MAPEO DE EMOCIONES → AJUSTE DE TONO
    # ==========================================================
    def _emotion_to_delta(self, emotion: str) -> float:
        """
        Convierte una emoción del resultado del juego en un ajuste
        de intensidad tonal para el MoodManager.
        """
        mapping = {
            "triumph": +0.3,
            "hope": +0.2,
            "fear": +0.2,
            "tension": +0.1,
            "sadness": -0.2,
            "loss": -0.3,
            "anger": +0.1,
            "calm": -0.1,
            "neutral": 0.0
        }
        return mapping.get(emotion.lower(), 0.0)
