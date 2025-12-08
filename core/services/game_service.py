import httpx
import os
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class GameService:
    """
    Servicio que conecta con la GameAPI externa (sam-gameapi)
    para procesar acciones de jugador, combates o verificaciones.
    Usa el AI engine del GameAPI para interpretar lenguaje natural.
    """

    def __init__(self):
        self.api_url = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com").strip("/")

    async def process_action(self, player_name: str, action_text: str, mode: str = "action") -> Dict[str, Any]:
        """
        Envía una acción del jugador al GameAPI.
        El GameAPI usa AI para interpretar el lenguaje natural y generar respuesta narrativa.
        
        Args:
            player_name: Nombre del jugador
            action_text: Acción en lenguaje natural (ej: "I hit the goblin with my axe")
            mode: "action" o "dialogue" (para interacciones con NPCs)
        
        Returns:
            Dict con "result" (narrativa) y opcionalmente "event" (evento dinámico)
        """
        endpoint = f"{self.api_url}/game/action"
        payload = {"player": player_name, "action": action_text}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # GameAPI retorna: {"player": "...", "result": "...", "event": {...} (opcional)}
                return {
                    "success": True,
                    "result": data.get("result", "No se obtuvo respuesta del motor de juego."),
                    "event": data.get("event"),  # Evento dinámico si se generó
                }
            except httpx.ConnectError as e:
                logger.error(f"Error de conexión con GameAPI: {e}")
                return {
                    "success": False,
                    "error": "No se pudo conectar al motor de juego. Verifica que el servicio esté activo.",
                }
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP del GameAPI: {e}")
                return {
                    "success": False,
                    "error": f"Error del servidor de juego: {e.response.status_code}",
                }
            except Exception as e:
                logger.error(f"Error inesperado al contactar GameAPI: {e}")
                return {
                    "success": False,
                    "error": f"Error inesperado: {str(e)}",
                }

    async def start_game(self, party_levels: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Inicia una nueva partida en el GameAPI.
        
        Args:
            party_levels: Lista de niveles de los jugadores (ej: [3, 3, 4])
        
        Returns:
            Dict con el estado inicial del juego
        """
        endpoint = f"{self.api_url}/game/start"
        payload = {"party_levels": party_levels or [1]}

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
            except Exception as e:
                logger.error(f"Error iniciando partida: {e}")
                return {"success": False, "error": str(e)}

    async def get_game_state(self) -> Dict[str, Any]:
        """Obtiene el estado actual del juego desde GameAPI."""
        endpoint = f"{self.api_url}/game/state"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(endpoint)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
            except Exception as e:
                logger.error(f"Error obteniendo estado: {e}")
                return {"success": False, "error": str(e)}

    async def join_party(self, player_name: str) -> Dict[str, Any]:
        """Agrega un jugador al grupo en GameAPI."""
        endpoint = f"{self.api_url}/party/join"
        payload = {"player": player_name}

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    return {"success": False, "error": "Ya estás en el grupo."}
                return {"success": False, "error": f"Error: {e.response.status_code}"}
            except Exception as e:
                logger.error(f"Error uniéndose al grupo: {e}")
                return {"success": False, "error": str(e)}

    async def get_party(self) -> Dict[str, Any]:
        """Obtiene la lista de jugadores en el grupo."""
        endpoint = f"{self.api_url}/party"

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(endpoint)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
            except Exception as e:
                logger.error(f"Error obteniendo grupo: {e}")
                return {"success": False, "error": str(e)}
