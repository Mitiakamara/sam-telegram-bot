from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
from .base import Language


class MessageBlock(BaseModel):
    """
    Bloque individual de texto dentro de un mensaje Telegram.
    Permite dividir narrativas largas y mostrar tiradas en línea.
    """
    text: str
    rolls_inline: Optional[List[str]] = None


class TelegramMessage(BaseModel):
    """
    Mensaje narrativo final, listo para enviar a Telegram.
    Cumple con los límites de MarkdownV2 (1200 caracteres por bloque).
    """
    message_id: UUID
    action_id: UUID
    lang: Language
    mode: str = "MarkdownV2"
    safe_len: int = 1200
    blocks: List[MessageBlock]
    meta: Optional[Dict] = None
