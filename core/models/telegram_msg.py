# ================================================================
# 📦 TELEGRAM MESSAGE MODEL (SAM compatible)
# ================================================================
# Modelo flexible y seguro para el envío de mensajes al usuario
# a través de Telegram. Compatible con la arquitectura de SAM 6.30+
# y el sistema de render narrativo adaptativo.
# ================================================================

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4
from datetime import datetime


class MessageBlock(BaseModel):
    """
    Un bloque estructurado opcional dentro de un mensaje.
    Puede representar un párrafo narrativo, una acción o un diálogo.
    """
    type: str = Field(default="text", description="Tipo de bloque (text, action, npc, etc.)")
    content: str = Field(default="", description="Contenido textual del bloque")
    emotion: Optional[str] = Field(default=None, description="Emoción asociada (si aplica)")
    tone: Optional[str] = Field(default=None, description="Tono narrativo (opcional)")


class TelegramMessage(BaseModel):
    """
    Modelo principal del mensaje enviado al jugador.
    Simplificado para aceptar texto plano o estructura narrativa.
    """

    message_id: str = Field(default_factory=lambda: str(uuid4()), description="ID único del mensaje")
    action_id: str = Field(default="rendered_output", description="Identificador de la acción o respuesta generada")
    lang: str = Field(default="es", description="Idioma del mensaje (por defecto: español)")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Fecha UTC de creación")

    # Contenido principal
    text: str = Field(default="", description="Texto completo a enviar al jugador")
    blocks: List[MessageBlock] = Field(default_factory=list, description="Bloques estructurados opcionales")

    # Metadatos narrativos opcionales
    tone: Optional[str] = Field(default=None, description="Tono narrativo detectado o aplicado")
    emotion: Optional[str] = Field(default=None, description="Emoción dominante asociada")
    scene_type: Optional[str] = Field(default=None, description="Tipo de escena narrativa (progress, tension, etc.)")
    outcome: Optional[str] = Field(default=None, description="Resultado narrativo (success, failure, mixed)")

    def summary(self) -> str:
        """
        Retorna un resumen legible del mensaje (para logs o depuración).
        """
        return (
            f"[{self.timestamp}] ({self.lang.upper()}) "
            f"{self.action_id} → {self.text[:100]}..."
        )
