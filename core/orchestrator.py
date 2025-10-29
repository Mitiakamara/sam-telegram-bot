# =============================================================
# SAM Orchestrator - Remote Mode (Render Microservices)
# =============================================================
# Coordina toda la narrativa de SAM conectando con GameAPI y SRDService
# mediante HTTP remoto. No almacena archivos locales.
# =============================================================

import asyncio
import httpx
import logging
from typing import Dict, Any, Optional


class Orchestrator:
    """
    El Orchestrator actúa como el "director narrativo" principal de SAM.
    Gestiona el flujo emocional, la narrativa y las interacciones del jugador,
    delegando lógica y datos a los servicios remotos (GameAPI y SRDService).
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
        self._initialized = True

        # Inicializa el mundo remoto
        asyncio.get_event_loop().create_task(self.reset_world())

    # ---------------------------------------------------------
    # 🌍 Funciones principales
    # ---------------------------------------------------------
    async def reset_world(self) -> None:
        """
        Reinicia el estado narrativo del mundo en GameAPI remoto.
        """
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
        """
        Obtiene el estado narrativo actual desde GameAPI remoto.
        """
        try:
            response = await self.session.get(f"{self.gameapi_url}/state")
            response.raise_for_status()
            self.state = response.json()
            return self.state
        except Exception as e:
            self.log.error(f"[Orchestrator] Error al obtener estado: {e}")
            return self.state or {}

    async def process_player_action(self, action_text: str) -> Dict[str, Any]:
        """
        Envía la acción del jugador al GameAPI remoto y obtiene la respuesta narrativa.
        """
        payload = {"action": action_text}

        try:
            self.log.info(f"[Orchestrator] Enviando acción: {action_text}")
            response = await self.session.post(f"{self.gameapi_url}/action", json=payload)
            response.raise_for_status()
            result = response.json()
            self.state = result
            return result
        except httpx.HTTPStatusError as e:
            self.log.error(f"[GameAPI] Error HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            self.log.error(f"[GameAPI] Error de conexión: {e}")
        except Exception as e:
            self.log.exception(f"[GameAPI] Excepción inesperada: {e}")

        return {"error": "No se pudo procesar la acción.", "scene": {}, "emotion": {}}

    # ---------------------------------------------------------
    # 📖 SRD Queries (datos del sistema de reglas)
    # ---------------------------------------------------------
    async def query_srd(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Consulta el SRDService remoto (razas, clases, conjuros, etc.).
        """
        try:
            response = await self.session.post(
                f"{self.srdservice_url}/query",
                json={"query": query},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log.error(f"[SRDService] Error en query SRD: {e}")
            return None

    # ---------------------------------------------------------
    # 💬 Generación narrativa y tono
    # ---------------------------------------------------------
    async def generate_scene_description(self) -> str:
        """
        Solicita una descripción narrativa adaptativa al GameAPI remoto.
        """
        try:
            response = await self.session.get(f"{self.gameapi_url}/narrate")
            response.raise_for_status()
            data = response.json()
            description = data.get("description", "")
            self.log.info(f"[Orchestrator] Narrativa recibida: {description[:80]}...")
            return description
        except Exception as e:
            self.log.error(f"[Narrative] Error al generar descripción: {e}")
            return "El entorno se mantiene en silencio, a la espera de nuevas acciones."

    # ---------------------------------------------------------
    # 🧹 Limpieza
    # ---------------------------------------------------------
    async def close(self):
        """
        Cierra la sesión HTTP asíncrona.
        """
        await self.session.aclose()
        self.log.info("[Orchestrator] Sesión HTTP cerrada correctamente.")

    # ---------------------------------------------------------
    # 🧠 Helpers sincrónicos (para compatibilidad)
    # ---------------------------------------------------------
    def reset_world_sync(self):
        asyncio.get_event_loop().run_until_complete(self.reset_world())

    def process_player_action_sync(self, action_text: str):
        return asyncio.get_event_loop().run_until_complete(self.process_player_action(action_text))

    def get_state_sync(self):
        return asyncio.get_event_loop().run_until_complete(self.get_state())
