from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
from core.models.base import Language


class MessageBlock(BaseModel):
    text: str
    rolls_inline: Optional[List[str]] = None


class TelegramMessage(BaseModel):
    message_id: UUID
    action_id: UUID
    lang: Language
    mode: str = "MarkdownV2"
    safe_len: int = 1200
    blocks: List[MessageBlock]
    meta: Optional[Dict] = None
