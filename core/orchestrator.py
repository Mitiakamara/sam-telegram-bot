import asyncio
import httpx
import logging
from typing import Dict, Any, Optional


class Orchestrator:
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
            if response.status_code == 404:
                self.log.warning("[GameAPI] /reset no disponible. Reinicio simulado localmente.")
                self.state = {"scene": {"title": "Inicio local", "emotion": "neutral"}}
                return
            response.raise_for_status()
            self.state = response.json()
            self.log.info("[Orchestrator] Mundo remoto reiniciado correctamente.")
        except Exception as e:
            self.log.error(f"[Orchestrator] Error al reiniciar mundo remoto: {e}")
            self.state = {}

    async def get_state(self) -> Dict[str, Any]:
        try:
            response = await self.session.get(f"{self.gameapi_url}/state")
            if response.status_code == 404:
                return self.state or {"scene": {"title": "Inicio local"}}
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

            if response.status_code == 404:
                self.log.warning("[GameAPI] Endpoint /action no encontrado, usando fallback local.")
                return self._fallback_local_action(action_text)

            response.raise_for_status()
            result = response.json()
            self.state = result
            return result
        except Exception as e:
            self.log.error(f"[Orchestrator] Error procesando acción: {e}")
            return self._fallback_local_action(action_text)

    def _fallback_local_action(self, text: str) -> Dict[str, Any]:
        """Respuesta de emergencia si GameAPI no responde o no existe el endpoint."""
        return {
            "title": "Acción narrativa local",
            "description": f"El mundo todavía no entiende bien cómo reaccionar a '{text}', "
                           "pero el eco de tus palabras resuena en la oscuridad.",
            "emotion": "neutral",
            "scene_type": "progress"
        }

    # ---------------------------------------------------------
    # 💬 Adaptadores síncronos para el bot
    # ---------------------------------------------------------
    def start_new_adventure(self, player_name: str) -> Dict[str, Any]:
        asyncio.get_event_loop().run_until_complete(self.reset_world())
        return {
            "title": f"Inicio de la aventura de {player_name}",
            "description": "Una brisa fría recorre el valle silencioso. El viaje comienza.",
            "emotion": "neutral",
            "scene_type": "intro"
        }

    def process_player_input(self, player_name: str, user_input: str) -> Dict[str, Any]:
        result = asyncio.get_event_loop().run_until_complete(
            self.process_player_action(user_input)
        )

        # fallback si la respuesta remota falla
        if not result or "description" not in result:
            result = self._fallback_local_action(user_input)

        return result

    def get_world_status(self) -> str:
        state = asyncio.get_event_loop().run_until_complete(self.get_state())
        scene = state.get("scene", {})
        title = scene.get("title", "Escena desconocida")
        emotion = scene.get("emotion", "neutral")
        return f"🌍 *Estado actual del mundo:*\nEscena: {title}\nEmoción: {emotion}"

    def reset_world_sync(self):
        asyncio.get_event_loop().run_until_complete(self.reset_world())

    async def close(self):
        await self.session.aclose()
        self.log.info("[Orchestrator] Sesión HTTP cerrada correctamente.")
