from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime
from core.models.base import Language

class SpellcastingData(BaseModel):
    """
    Datos de lanzamiento de hechizos del personaje.
    """
    class_: Optional[str] = None
    ability: Optional[str] = None
    slots: Dict[str, int] = {}
    known_spells: List[str] = []
    prepared_spells: List[str] = []


class PCStats(BaseModel):
    """
    Atributos, habilidades y estado de un personaje jugador.
    """
    abilities: Dict[str, int]
    proficiency_bonus: int
    skills: List[str]
    saving_throws: List[str]
    ac: int
    hp: Dict[str, int]
    speed: int
    conditions: List[str]
    spellcasting: Optional[SpellcastingData] = None


class SceneContext(BaseModel):
    """
    Contexto de la escena actual (ubicación, entorno, party, reglas activas).
    """
    scene_id: UUID
    location: str
    party: List[Dict[str, str]]
    pc_stats: Dict[str, PCStats]
    ruleset: str
    environment: Optional[Dict[str, Optional[str | bool]]] = None


class Action(BaseModel):
    """
    Acción libre del jugador (entrada principal del pipeline narrativo).
    """
    action_id: UUID
    session_id: UUID
    player_id: UUID
    lang: Language
    text: str
    timestamp: datetime
    scene_context: SceneContext
