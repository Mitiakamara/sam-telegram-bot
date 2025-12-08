import os
import httpx
from dotenv import load_dotenv

# ================================================================
# ⚙️ Configuración base
# ================================================================
# NOTE: This module contains HTTP client functions for sam-gameapi.
# Currently not actively used, but kept for future integration.
# The GameService class in core/services/game_service.py provides
# similar functionality and may be the preferred approach.
# ================================================================

load_dotenv()

# Dirección del GameAPI (Render o local)
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com").strip("/")

# Token del bot (usado en main.py)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ================================================================
# 🔒 Cliente HTTPX con SSL verificado
# ================================================================

def get_http_client():
    """
    Devuelve un cliente HTTPX configurado para conexiones seguras (HTTPS)
    compatible con Render y entornos Windows.
    """
    return httpx.AsyncClient(
        timeout=60.0,
        verify=True,          # fuerza verificación SSL
        trust_env=True,       # usa certificados del sistema
        follow_redirects=True # sigue redirecciones HTTPS automáticamente
    )

# ================================================================
# 🧩 Funciones auxiliares de conexión
# ================================================================

async def send_action(player: str, action: str) -> dict:
    """Envía una acción al GameAPI y devuelve la respuesta procesada."""
    try:
        async with get_http_client() as client:
            payload = {"player": player, "action": action}
            url = f"{GAME_API_URL}/game/action"
            r = await client.post(url, json=payload)
            r.raise_for_status()
            return r.json()
    except httpx.ConnectError as e:
        return {"error": f"No se pudo conectar al GameAPI: problema SSL o red ({str(e)})"}
    except httpx.RequestError as e:
        return {"error": f"No se pudo conectar al GameAPI: {str(e)}"}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}

async def get_state() -> dict:
    """Obtiene el estado actual de la partida desde el GameAPI."""
    try:
        async with get_http_client() as client:
            url = f"{GAME_API_URL}/game/state"
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
    except httpx.ConnectError as e:
        return {"error": f"No se pudo conectar al GameAPI: problema SSL o red ({str(e)})"}
    except httpx.RequestError as e:
        return {"error": f"No se pudo conectar al GameAPI: {str(e)}"}
    except Exception as e:
        return {"error": f"Error al obtener estado: {str(e)}"}

# ================================================================
# 🚀 Función para iniciar partida (usada automáticamente por el bot)
# ================================================================

async def start_game():
    """Inicia una nueva partida en el GameAPI (si no hay partida activa)."""
    try:
        async with get_http_client() as client:
            payload = {"party_levels": [3, 3, 4]}  # grupo base de ejemplo
            url = f"{GAME_API_URL}/game/start"
            r = await client.post(url, json=payload)
            r.raise_for_status()
            return r.json()
    except httpx.ConnectError as e:
        return {"error": f"No se pudo conectar al GameAPI: problema SSL o red ({str(e)})"}
    except httpx.RequestError as e:
        return {"error": f"No se pudo conectar al GameAPI: {str(e)}"}
    except Exception as e:
        return {"error": f"Error iniciando partida: {str(e)}"}
