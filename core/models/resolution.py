from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
from core.models.base import IntentType, CheckOutcome, ErrorModel


class Step(BaseModel):
    """
    Representa un paso en el proceso de resolución (check, ataque, daño, etc.).
    """
    kind: str                      # check | attack | damage | save | resource_update | state_change | rules_note
    desc: str                      # descripción narrativa o mecánica
    result_total: Optional[int] = None
    outcome: Optional[CheckOutcome] = None
    notes: Optional[str] = None


class Resolution(BaseModel):
    """
    Resultado final del motor de reglas tras procesar un Intent.
    """
    resolution_id: UUID
    action_id: UUID
    intent: IntentType
    steps: List[Step]
    outcome: CheckOutcome
    dice_log: List[Dict]            # lista reproducible de tiradas
    errors: Optional[List[ErrorModel]] = None
