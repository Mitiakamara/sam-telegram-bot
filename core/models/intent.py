from pydantic import BaseModel
from typing import Optional, Dict, List
from uuid import UUID
from .base import IntentType, ErrorModel


class Intent(BaseModel):
    """
    Representa la intención interpretada a partir del texto del jugador.
    Producida por el módulo NLP (nlp_intent.py).
    """
    action_id: UUID
    intent: IntentType
    confidence: float
    requires_srd: bool = False
    entities: Dict[str, Optional[str]] = {}
    errors: Optional[List[ErrorModel]] = None
