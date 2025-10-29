    @staticmethod
    def update_state(player_input: str) -> dict:
        """
        Analiza la entrada del jugador y devuelve un estado emocional simplificado.
        En modo campaña, solo detecta tono general (positivo, negativo o neutro).
        """
        if not player_input:
            return {"dominant_emotion": "neutral", "tone": "neutral"}

        text = player_input.lower()
        positive = ["alegría", "feliz", "risa", "éxito", "logrado", "bien"]
        negative = ["miedo", "triste", "fracaso", "sangre", "dolor", "ira", "odio"]

        emotion = "neutral"
        tone = "neutral"

        if any(word in text for word in positive):
            emotion, tone = "joy", "hopeful"
        elif any(word in text for word in negative):
            emotion, tone = "fear", "dark"

        # Registrar un pseudo vector de emociones básicas
        emotion_vector = {
            "joy": 1.0 if emotion == "joy" else 0.2,
            "fear": 1.0 if emotion == "fear" else 0.2,
            "anger": 0.1,
            "sadness": 0.1,
            "surprise": 0.3
        }

        result = {
            "dominant_emotion": emotion,
            "tone": tone,
            "emotion_vector": emotion_vector
        }

        # Guarda el registro en el historial
        EmotionalTracker.log_scene({
            "title": f"Entrada del jugador: {player_input[:40]}",
            "scene_type": "player_input",
            **result,
            "summary": player_input,
            "outcome": "neutral"
        })

        return result
