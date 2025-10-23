from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
from .base import ErrorModel


class SrdQuery(BaseModel):
    """
    Representa una consulta al servicio SRD.
    """
    query_id: UUID
    action_id: UUID
    kind: str                     # spell | feature | condition | item | rule | monster | skill | ability
    q: str                        # texto buscado
    limit: int = 1
    lang: str = "es"
    cache_ttl_seconds: int = 3600


class SrdHit(BaseModel):
    """
    Representa un resultado individual del SRD.
    """
    kind: str
    name: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    details: Optional[Dict[str, Optional[str]]] = {}


class SrdResponse(BaseModel):
    """
    Estructura estandarizada para las respuestas SRD.
    """
    query_id: UUID
    from_cache: bool
    source: Dict[str, str]
    hits: List[SrdHit] = []
    errors: Optional[List[ErrorModel]] = None
