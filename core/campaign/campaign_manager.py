import json
import os
import logging
from typing import Any, Dict, Optional


class CampaignManager:
    """
    Administra el estado de la campaña:
    - datos de campaña (nombre, capítulo, escena)
    - jugadores
    Se persiste en un JSON (por defecto: data/campaign_state.json)
    """

    def __init__(self, state_path: str = "data/campaign_state.json") -> None:
        self.logger = logging.getLogger("core.campaign.campaign_manager")
        self.state_path = state_path
        self.state: Dict[str, Any] = {
            "campaign_name": "TheGeniesWishes",
            "chapter": 1,
            "current_scene": "Oasis perdido",
            "players": {}
        }
        self._ensure_dir()
        self._load_state()
        self.logger.info("[CampaignManager] Estado cargado en %s", self.state_path)

    # ---------------------------------------------------------
    # Inicialización y persistencia
    # ---------------------------------------------------------
    def _ensure_dir(self) -> None:
        directory = os.path.dirname(self.state_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _load_state(self) -> None:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception as e:
                self.logger.warning("[CampaignManager] No pude leer el JSON, uso estado por defecto: %s", e)
        else:
            self._save_state()

        # asegurar claves mínimas
        self.state.setdefault("players", {})
        self.state.setdefault("campaign_name", "TheGeniesWishes")
        self.state.setdefault("chapter", 1)
        self.state.setdefault("current_scene", "Oasis perdido")

    def _save_state(self) -> None:
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error("[CampaignManager] Error guardando estado: %s", e)

    # ---------------------------------------------------------
    # API pública que usan los handlers
    # ---------------------------------------------------------
    def add_player(self, *args, **kwargs) -> str:
        """
        Compatibilidad con dos formas vistas en tus logs:

        1) Forma nueva (la que está usando tu createcharacter_handler.py):
            add_player(player_name="Jose", player_data={...})

        2) Forma vieja (la que aparecía como error antes):
            add_player(telegram_id, player_name, player_data)

        Guardamos siempre en self.state["players"] con una key string.
        Si tenemos telegram_id, lo guardamos dentro del jugador.
        """
        telegram_id: Optional[int] = None
        player_name: Optional[str] = None
        player_data: Optional[Dict[str, Any]] = None

        if args:
            # puede venir: (telegram_id, player_name, player_data)
            # o (player_name, player_data)
            if len(args) == 3:
                telegram_id, player_name, player_data = args
            elif len(args) == 2:
                player_name, player_data = args
            else:
                raise TypeError("add_player() recibió una cantidad inesperada de argumentos posicionales")
        else:
            # forma con kwargs: add_player(player_name=..., player_data=..., telegram_id=...)
            telegram_id = kwargs.get("telegram_id")
            player_name = kwargs.get("player_name")
            player_data = kwargs.get("player_data")

        if not player_name or player_data is None:
            raise ValueError("add_player() requiere al menos player_name y player_data")

        players: Dict[str, Any] = self.state.setdefault("players", {})

        # clave del jugador en el dict
        if telegram_id is not None:
            player_key = str(telegram_id)
        else:
            # autoincremental si no hay telegram_id
            player_key = str(len(players) + 1)

        # construimos el registro
        player_entry = {
            "name": player_name,
            **player_data,
        }
        if telegram_id is not None:
            player_entry["telegram_id"] = telegram_id

        players[player_key] = player_entry

        self._save_state()
        self.logger.info("[CampaignManager] Personaje %s agregado con éxito (key=%s).", player_name, player_key)
        return player_key

    # ---------------------------------------------------------
    # Lecturas usadas por /status, /progress, /scene
    # ---------------------------------------------------------
    def get_player_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        players = self.state.get("players", {})
        for p in players.values():
            if p.get("telegram_id") == telegram_id:
                return p
        return None

    def get_players(self) -> Dict[str, Any]:
        return self.state.get("players", {})

    def get_campaign_name(self) -> str:
        return self.state.get("campaign_name", "Campaña sin nombre")

    def get_current_chapter(self) -> int:
        return self.state.get("chapter", 1)

    def get_current_scene(self) -> str:
        return self.state.get("current_scene", "Escena no definida")

    def set_current_scene(self, scene_name: str) -> None:
        self.state["current_scene"] = scene_name
        self._save_state()

    def get_progress(self) -> Dict[str, Any]:
        """
        Útil si un handler quiere todo junto.
        """
        return {
            "campaign_name": self.get_campaign_name(),
            "chapter": self.get_current_chapter(),
            "current_scene": self.get_current_scene(),
            "players": self.get_players(),
        }

    def add_to_active_party(self, telegram_id: int) -> None:
        """
        Añade un jugador a la party activa de la campaña.
        """
        if "active_party" not in self.state:
            self.state["active_party"] = []
        if telegram_id not in self.state["active_party"]:
            self.state["active_party"].append(telegram_id)
            self._save_state()
            self.logger.info(f"[CampaignManager] Jugador {telegram_id} añadido a la party activa.")

    def get_active_party(self) -> list:
        """Retorna la lista de IDs de telegram de la party activa."""
        return self.state.get("active_party", [])

    def get_active_scene(self) -> Optional[Dict[str, Any]]:
        """
        Retorna la escena activa como diccionario.
        Si no hay escena activa, retorna None.
        """
        scene_name = self.get_current_scene()
        if not scene_name or scene_name == "Escena no definida":
            return None
        return {
            "title": scene_name,
            "description": scene_name,
            "scene_type": "active",
            "status": "active"
        }

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Carga el estado desde un diccionario.
        Útil para restaurar desde StoryDirector.
        """
        if data:
            self.state.update(data)
            self._save_state()
            self.logger.info("[CampaignManager] Estado cargado desde diccionario.")

    def to_dict(self) -> Dict[str, Any]:
        """
        Exporta el estado como diccionario.
        Útil para guardar desde StoryDirector.
        """
        return self.state.copy()
