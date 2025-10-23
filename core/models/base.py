from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


class Language(str, Enum):
    """Idiomas soportados."""
    es = "es"
    en = "en"


class IntentType(str, Enum):
    """Tipos principales de intención detectada."""
    cast_spell = "cast_spell"
    skill_check = "skill_check"
    attack = "attack"
    interact = "interact"
    investigate = "investigate"
    move = "move"
    talk = "talk"


class Ability(str, Enum):
    """Atributos básicos de D&D 5e."""
    STR = "STR"
    DEX = "DEX"
    CON = "CON"
    INT = "INT"
    WIS = "WIS"
    CHA = "CHA"


class AdvState(str, Enum):
    """Estado de ventaja o desventaja."""
    none = "none"
    advantage = "advantage"
    disadvantage = "disadvantage"


class CheckOutcome(str, Enum):
    """Resultados posibles de un chequeo o evento."""
    success = "success"
    failure = "failure"
    critical_success = "critical_success"
    critical_failure = "critical_failure"
    mixed = "mixed"


class ErrorModel(BaseModel):
    """Estructura de error genérica."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
