import httpx
from uuid import uuid4
from aiocache import cached
from core.models.srd import SrdQuery, SrdResponse, SrdHit

SRD_SERVICE_URL = "https://sam-srdservice.onrender.com"


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
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(
                f"{SRD_SERVICE_URL}/search",
                params={"kind": kind, "q": q},
            )
            if r.status_code == 200:
                data = r.json()
            else:
                data = {}
    except Exception as e:
        print(f"[SRD Lookup Error] {e}")
        data = {}

    hits = []
    if "results" in data and isinstance(data["results"], list):
        for h in data["results"][: query.limit]:
            try:
                hits.append(SrdHit(**h))
            except Exception:
                pass

    # Si no hay resultados, crear respuesta vacía
    return SrdResponse(
        query_id=query.query_id,
        from_cache=False,
        source={"service_url": SRD_SERVICE_URL, "latency_ms": 0},
        hits=hits,
    )
