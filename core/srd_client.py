import httpx
import os
import logging
from uuid import uuid4
from aiocache import cached
from core.models.srd import SrdQuery, SrdResponse, SrdHit

logger = logging.getLogger(__name__)

SRD_SERVICE_URL = os.getenv("SRD_SERVICE_URL", "https://sam-srdservice.onrender.com").strip("/")


@cached(ttl=3600)
async def lookup(kind: str, q: str, action_id):
    """
    Consulta el servicio SRD (hechizos, rasgos, condiciones, etc.)
    con caché TTL de 1 hora para evitar repeticiones.

    Args:
        kind: tipo de recurso ("spell", "feature", "condition", etc.)
        q: texto de búsqueda (nombre del hechizo u objeto)
        action_id: UUID de la acción actual (para trazas)
    Returns:
        SrdResponse con hits normalizados o vacío si falla.
    """
    query = SrdQuery(
        query_id=uuid4(),
        action_id=action_id,
        kind=kind,
        q=q,
        lang="es",
        limit=1,
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # SRD service uses /srd/{resource}?q=query format
            # Map kind to endpoint
            endpoint_map = {
                "spell": "spells",
                "monster": "monsters",
                "race": "races",
                "class": "classes",
                "feature": "classes",  # Features are in classes
                "condition": "conditions",
                "skill": "skills",
            }
            
            endpoint = endpoint_map.get(kind, "spells")
            url = f"{SRD_SERVICE_URL}/srd/{endpoint}"
            
            if q:
                # Use query parameter for search
                r = await client.get(url, params={"q": q})
            else:
                # Get all if no query
                r = await client.get(url)
            
            if r.status_code == 200:
                data = r.json()
                # Transform to expected format
                if "results" in data:
                    # Already in results format
                    pass
                elif isinstance(data, dict) and q:
                    # Convert dict to results format
                    results = []
                    for name, content in data.items():
                        if q.lower() in name.lower() or (isinstance(content, dict) and any(q.lower() in str(v).lower() for v in content.values() if isinstance(v, str))):
                            results.append({"name": name, "data": content})
                    data = {"results": results}
                else:
                    # Single item or list
                    data = {"results": [data] if not isinstance(data, list) else data}
            else:
                data = {}
    except Exception as e:
        print(f"[SRD Lookup Error] {e}")
        data = {}

    hits = []
    if "results" in data and isinstance(data["results"], list):
        for h in data["results"][: query.limit]:
            try:
                # Handle different response formats
                if isinstance(h, dict):
                    if "name" in h and "data" in h:
                        # Format: {"name": "...", "data": {...}}
                        hit_data = h["data"]
                        hit_name = h["name"]
                    else:
                        # Format: direct dict
                        hit_data = h
                        hit_name = h.get("name", h.get("title", "Unknown"))
                    
                    # Create SrdHit with available data
                    hits.append(SrdHit(
                        kind=kind,
                        name=hit_name,
                        slug=hit_name.lower().replace(" ", "-"),
                        summary=str(hit_data.get("description", hit_data.get("summary", "")))[:200],
                        details=hit_data if isinstance(hit_data, dict) else {}
                    ))
            except Exception as e:
                logger.warning(f"[SRD Lookup] Error parsing hit: {e}")
                pass

    # Si no hay resultados, crear respuesta vacía
    return SrdResponse(
        query_id=query.query_id,
        from_cache=False,
        source={"service_url": SRD_SERVICE_URL, "latency_ms": 0},
        hits=hits,
    )
