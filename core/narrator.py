# core/narrator.py
import logging

class SAMNarrator:
    """Narrador principal del sistema S.A.M., maneja la voz narrativa del juego."""

    def __init__(self):
        self.logger = logging.getLogger("SAM.Narrator")

    def speak(self, text: str):
        """Muestra o envía un mensaje narrativo."""
        # Aquí podrías integrarlo con Telegram, Discord, etc.
        formatted = f"*S.A.M.*: {text}"
        self.logger.info(formatted)
        print(formatted)
        return formatted
