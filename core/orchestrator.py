# =============================================================
# SAM Orchestrator - Remote Mode (Render Microservices)
# =============================================================
# Coordina la narrativa de SAM conectando con GameAPI y SRDService
# mediante HTTP remoto. Adaptado al flujo síncrono del bot Telegram.
# =============================================================

import asyncio
import httpx
import logging
from typing import Dict, Any, Optional


class Orchestrator:
    """
    Orchestrator actúa como el "director narrativo" de SAM.
    Gestiona el flujo emocional, la narrativa y las interacciones
    del jugador con los servicios remotos GameAPI y SRDService.
    """

    def __init__(
        self,
        gameapi_url: str = "https://sam-gameapi.onrender.com",
        srdservice_url: str = "https://sam-srdservice.onrender.com",
        timeout: int = 20,
    ):
        self.log = logging.getLogger("core.orchestrator")
        self.gameapi_url = gameapi_url.rstrip("/")
        self.srdservice_url = srdservice_url.rstrip("/")
        self.timeout = timeout

        self.state: Dict[str, Any] = {}
        self.session = httpx.AsyncClient(timeout=self.timeout)

        self.log.info("[Orchestrator] Inicializando módulos narrativos...")
        asyncio.get_event_loop().create_task(self.reset_world())

    # ---------------------------------------------------------
    # 🌍 Funciones asíncronas base
    # ---------------------------------------------------------
    async def reset_world(self) -> None:
        self.log.warning("[Orchestrator] Reiniciando mundo narrativo remoto...")
        try:
            response = await self.session.post(f"{self.gameapi_url}/reset")
            response.raise_for_status()
            self.state = response.json()
            self.log.info("[Orchestrator] Mundo remoto reiniciado correctamente.")
        except Exception as e:
            self.log.error(f"[Orchestrator] Error al reiniciar mundo remoto: {e}")
            self.state = {}

    async def get_state(self) -> Dict[str, Any]:
        try:
            response = await self.session.get(f"{self.gameapi_url}/state")
            response.raise_for_status()
            self.state = response.json()
            return self.state
        except Exception as e:
            self.log.error(f"[Orchestrator] Error al obtener estado: {e}")
            return self.state or {}

    async def process_player_action(self, action_text: str) -> Dict[str, Any]:
        payload = {"action": action_text}
        try:
            self.log.info(f"[Orchestrator] Enviando acción: {action_text}")
            response = await self.session.post(f"{self.gameapi_url}/action", json=payload)
            response.raise_for_status()
            result = response.json()
            self.state = result
            return result
        except Exception as e:
            self.log.error(f"[Orchestrator] Error procesando acción: {e}")
            return {"error": "No se pudo procesar la acción.", "scene": {}, "emotion": {}}

    # ---------------------------------------------------------
    # 📖 SRD Queries
    # ---------------------------------------------------------
    async def query_srd(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            response = await self.session.post(
                f"{self.srdservice_url}/query", json={"query": query}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log.error(f"[SRDService] Error en query SRD: {e}")
            return None

    # ---------------------------------------------------------
    # 💬 Adaptadores síncronos para el bot
    # ---------------------------------------------------------
    def start_new_adventure(self, player_name: str) -> Dict[str, Any]:
        """
        Inicializa una nueva aventura para el jugador.
        Devuelve la escena inicial en formato dict.
        """
        result = asyncio.get_event_loop().run_until_complete(self.reset_world())
        return {
            "title": f"Inicio de la aventura de {player_name}",
            "description": "Una brisa fría recorre el valle silencioso. El viaje comienza.",
            "emotion": "neutral",
            "scene_type": "intro"
        }

    def process_player_input(self, player_name: str, user_input: str) -> Dict[str, Any]:
        """
        Procesa una acción del jugador de forma síncrona.
        """
        result = asyncio.get_event_loop().run_until_complete(
            self.process_player_action(user_input)
        )

        # fallback en caso de error remoto
        if not result or "description" not in result:
            result = {
                "title": f"Acción de {player_name}",
                "description": f"{player_name} intenta {user_input.lower()}, "
                               "mientras el destino observa en silencio.",
                "emotion": "neutral",
                "scene_type": "progress"
            }

        return result

    def get_world_status(self) -> str:
        """
        Devuelve un resumen textual del estado actual del mundo.
        """
        state = asyncio.get_event_loop().run_until_complete(self.get_state())
        scene = state.get("scene", {})
        title = scene.get("title", "Escena desconocida")
        emotion = scene.get("emotion", "neutral")
        return f"🌍 *Estado actual del mundo:*\nEscena: {title}\nEmoción: {emotion}"

    def reset_world_sync(self):
        asyncio.get_event_loop().run_until_complete(self.reset_world())

    # ---------------------------------------------------------
    # 🧹 Limpieza
    # ---------------------------------------------------------
    async def close(self):
        await self.session.aclose()
        self.log.info("[Orchestrator] Sesión HTTP cerrada correctamente.")
