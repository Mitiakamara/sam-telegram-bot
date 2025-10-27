import httpx
import os

class GameService:
    """
    Servicio que conecta con la GameAPI externa (sam-gameapi)
    para procesar acciones de jugador, combates o verificaciones.
    """

    def __init__(self):
        self.api_url = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")

    async def process_action(self, player_id: str, action_text: str):
        """Envía una acción del jugador al GameAPI."""
        endpoint = f"{self.api_url}/game/action"
        payload = {"player_id": player_id, "action": action_text}

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("result", "No se obtuvo respuesta del motor de juego.")
            except Exception as e:
                return f"⚠️ Error al contactar GameAPI: {e}"
