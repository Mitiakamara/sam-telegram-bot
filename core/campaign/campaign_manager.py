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
        # Start with default structure
        default_state = {
            "campaign_name": "TheGeniesWishes",
            "chapter": 1,
            "current_scene": "Oasis perdido",
            "players": {},
            "active_party": [],
            "party_chats": {}
        }
        self.state = default_state.copy()
        
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    loaded_state = json.load(f)
                    
                    # Migrate old format to new format
                    if "campaign_id" in loaded_state:
                        # Old format - migrate
                        self.state["campaign_name"] = loaded_state.get("campaign_title", loaded_state.get("campaign_id", "TheGeniesWishes"))
                        self.state["chapter"] = loaded_state.get("current_chapter", 1)
                        self.state["current_scene"] = loaded_state.get("active_scene", "Oasis perdido")
                        self.logger.info("[CampaignManager] Migrated old campaign state format")
                    
                    # Preserve ALL other keys from loaded state (including adventure data)
                    for key, value in loaded_state.items():
                        if key not in ["campaign_id", "campaign_title", "current_chapter", "active_scene"]:
                            # Preserve all other keys, including adventure_data, current_scene_id, etc.
                            self.state[key] = value
                    
                    # Explicitly preserve these critical keys if they exist
                    if "players" in loaded_state and isinstance(loaded_state["players"], dict):
                        self.state["players"] = loaded_state["players"]
                    
                    if "active_party" in loaded_state:
                        self.state["active_party"] = loaded_state["active_party"]
                    
                    if "party_chats" in loaded_state:
                        self.state["party_chats"] = loaded_state["party_chats"]
                    
                    if "adventure_data" in loaded_state:
                        self.state["adventure_data"] = loaded_state["adventure_data"]
                    
                    if "current_scene_id" in loaded_state:
                        self.state["current_scene_id"] = loaded_state["current_scene_id"]
                    
                    if "adventure_scenes" in loaded_state:
                        self.state["adventure_scenes"] = loaded_state["adventure_scenes"]
                    
                    if "campaign_title" in loaded_state:
                        self.state["campaign_title"] = loaded_state["campaign_title"]
                    
                    # Logging para verificar que adventure_data se cargó
                    loaded_adventure_data = self.state.get("adventure_data")
                    loaded_scene_id = self.state.get("current_scene_id")
                    self.logger.info(f"[CampaignManager] Estado cargado. adventure_data presente: {loaded_adventure_data is not None}, current_scene_id: {loaded_scene_id}")
                    if loaded_adventure_data:
                        # Verificar estructura
                        if isinstance(loaded_adventure_data, dict) and "scenes" in loaded_adventure_data:
                            scene_count = len(loaded_adventure_data.get("scenes", []))
                            self.logger.info(f"[CampaignManager] adventure_data tiene estructura válida con {scene_count} escenas")
                        else:
                            self.logger.warning(f"[CampaignManager] adventure_data no tiene estructura válida. Tipo: {type(loaded_adventure_data)}, keys: {list(loaded_adventure_data.keys()) if isinstance(loaded_adventure_data, dict) else 'N/A'}")
                    
            except Exception as e:
                self.logger.warning("[CampaignManager] No pude leer el JSON, uso estado por defecto: %s", e)
        else:
            self._save_state()

        # Ensure critical keys exist (safety check)
        self.state.setdefault("players", {})
        self.state.setdefault("campaign_name", "TheGeniesWishes")
        self.state.setdefault("chapter", 1)
        self.state.setdefault("current_scene", "Oasis perdido")
        self.state.setdefault("active_party", [])
        self.state.setdefault("party_chats", {})
        
        # CORRECCIÓN CRÍTICA: Si current_scene es un nombre de archivo JSON, corregirlo
        current_scene = self.state.get("current_scene", "")
        if current_scene and current_scene.endswith(".json"):
            self.logger.warning(f"[CampaignManager] current_scene tiene nombre de archivo JSON: '{current_scene}'. Corrigiendo...")
            # Si hay adventure_data, usar el título de la escena actual
            adventure_data = self.state.get("adventure_data")
            current_scene_id = self.state.get("current_scene_id")
            if adventure_data and current_scene_id:
                try:
                    from core.adventure.adventure_loader import AdventureLoader
                    loader = AdventureLoader()
                    scene = loader.find_scene_by_id(adventure_data, current_scene_id)
                    if scene:
                        self.state["current_scene"] = scene.get("title", "Escena actual")
                        self.logger.info(f"[CampaignManager] current_scene corregido a: {self.state['current_scene']}")
                    else:
                        self.state["current_scene"] = "Escena actual"
                        self.logger.warning(f"[CampaignManager] No se encontró escena con ID '{current_scene_id}', usando 'Escena actual'")
                except Exception as e:
                    self.logger.error(f"[CampaignManager] Error al corregir current_scene: {e}")
                    self.state["current_scene"] = "Escena actual"
            else:
                # Fallback: usar un nombre genérico
                self.state["current_scene"] = "Escena actual"
                self.logger.info(f"[CampaignManager] current_scene corregido a: Escena actual (no hay adventure_data)")
            # Guardar el estado corregido
            self._save_state()
        
        # VERIFICACIÓN ADICIONAL: Si hay campaign_name pero no adventure_data, intentar recargar
        campaign_name = self.state.get("campaign_name", "")
        adventure_data = self.state.get("adventure_data")
        if campaign_name and campaign_name != "TheGeniesWishes" and not adventure_data:
            self.logger.warning(f"[CampaignManager] campaign_name='{campaign_name}' pero adventure_data es None. Esto sugiere que el estado no se guardó correctamente.")
            # Intentar recargar la aventura desde el StoryDirector (si está disponible)
            # Nota: No podemos acceder a StoryDirector desde aquí, así que solo logueamos
            self.logger.info(f"[CampaignManager] Se recomienda ejecutar /loadcampaign {campaign_name} para recargar la aventura")

    def _save_state(self) -> None:
        try:
            # Verificar que adventure_data está presente antes de guardar
            has_adventure_data = "adventure_data" in self.state and self.state.get("adventure_data") is not None
            current_scene_id = self.state.get("current_scene_id")
            campaign_name = self.state.get("campaign_name", "")
            
            if has_adventure_data:
                adventure_data = self.state.get("adventure_data")
                if isinstance(adventure_data, dict):
                    scene_count = len(adventure_data.get("scenes", []))
                    self.logger.info(f"[CampaignManager] _save_state - Guardando estado con adventure_data ({scene_count} escenas), current_scene_id: {current_scene_id}, campaign_name: {campaign_name}")
                else:
                    self.logger.warning(f"[CampaignManager] _save_state - adventure_data no es un dict: {type(adventure_data)}")
            else:
                self.logger.warning(f"[CampaignManager] _save_state - adventure_data NO está presente. campaign_name: {campaign_name}, current_scene_id: {current_scene_id}")
            
            # Intentar serializar para verificar que no hay problemas
            try:
                json_str = json.dumps(self.state, ensure_ascii=False, indent=2)
                json_size = len(json_str)
                self.logger.debug(f"[CampaignManager] Estado serializado correctamente. Tamaño: {json_size} bytes")
            except Exception as e:
                self.logger.error(f"[CampaignManager] Error al serializar estado: {e}", exc_info=True)
                raise
            
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            
            # Verificar que se guardó correctamente leyendo el archivo
            if has_adventure_data:
                try:
                    with open(self.state_path, "r", encoding="utf-8") as f:
                        saved_data = json.load(f)
                        saved_has_adventure = "adventure_data" in saved_data and saved_data.get("adventure_data") is not None
                        if saved_has_adventure:
                            saved_adventure = saved_data.get("adventure_data")
                            if isinstance(saved_adventure, dict):
                                saved_scene_count = len(saved_adventure.get("scenes", []))
                                self.logger.info(f"[CampaignManager] Estado guardado y verificado. adventure_data en archivo: True ({saved_scene_count} escenas), current_scene_id guardado: {saved_data.get('current_scene_id')}")
                            else:
                                self.logger.warning(f"[CampaignManager] adventure_data guardado pero no es un dict: {type(saved_adventure)}")
                        else:
                            self.logger.error(f"[CampaignManager] ERROR: adventure_data NO se guardó en el archivo aunque estaba presente antes de guardar!")
                except Exception as e:
                    self.logger.warning(f"[CampaignManager] No se pudo verificar el archivo guardado: {e}", exc_info=True)
        except Exception as e:
            self.logger.error("[CampaignManager] Error guardando estado: %s", e, exc_info=True)

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

    def add_to_active_party(self, telegram_id: int, chat_id: int = None) -> None:
        """
        Añade un jugador a la party activa de la campaña.
        
        Args:
            telegram_id: ID de Telegram del jugador
            chat_id: ID del chat donde está el jugador (opcional, para multi-player)
        """
        if "active_party" not in self.state:
            self.state["active_party"] = []
        if "party_chats" not in self.state:
            self.state["party_chats"] = {}  # Maps telegram_id -> chat_id
        
        if telegram_id not in self.state["active_party"]:
            self.state["active_party"].append(telegram_id)
            if chat_id:
                self.state["party_chats"][str(telegram_id)] = chat_id
            self._save_state()
            self.logger.info(f"[CampaignManager] Jugador {telegram_id} añadido a la party activa (chat: {chat_id}).")
    
    def get_party_chat_id(self, telegram_id: int) -> Optional[int]:
        """
        Obtiene el ID del chat donde está un jugador.
        """
        party_chats = self.state.get("party_chats", {})
        chat_id = party_chats.get(str(telegram_id))
        return chat_id if chat_id else None
    
    def get_all_party_chat_ids(self) -> list:
        """
        Obtiene todos los IDs de chat únicos donde hay jugadores de la party.
        """
        party_chats = self.state.get("party_chats", {})
        return list(set(party_chats.values()))

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
            # Preservar adventure_data y campos relacionados si existen
            adventure_data = data.get("adventure_data")
            current_scene_id = data.get("current_scene_id")
            adventure_scenes = data.get("adventure_scenes")
            campaign_title = data.get("campaign_title")
            
            self.state.update(data)
            
            # Asegurar que adventure_data se preserve
            if adventure_data:
                self.state["adventure_data"] = adventure_data
            if current_scene_id:
                self.state["current_scene_id"] = current_scene_id
            if adventure_scenes:
                self.state["adventure_scenes"] = adventure_scenes
            if campaign_title:
                self.state["campaign_title"] = campaign_title
            
            self._save_state()
            self.logger.info(f"[CampaignManager] Estado cargado desde diccionario. adventure_data: {adventure_data is not None}, current_scene_id: {current_scene_id}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Exporta el estado como diccionario.
        Útil para guardar desde StoryDirector.
        Asegura que todos los campos, incluyendo adventure_data, se incluyan.
        """
        state_copy = self.state.copy()
        # Asegurar que adventure_data y campos relacionados se incluyan
        if "adventure_data" in self.state:
            state_copy["adventure_data"] = self.state["adventure_data"]
        if "current_scene_id" in self.state:
            state_copy["current_scene_id"] = self.state["current_scene_id"]
        if "adventure_scenes" in self.state:
            state_copy["adventure_scenes"] = self.state["adventure_scenes"]
        if "campaign_title" in self.state:
            state_copy["campaign_title"] = self.state["campaign_title"]
        has_adventure = 'adventure_data' in state_copy
        scene_id = state_copy.get('current_scene_id')
        if has_adventure:
            adventure = state_copy.get('adventure_data')
            if isinstance(adventure, dict):
                scene_count = len(adventure.get('scenes', []))
                self.logger.info(f"[CampaignManager] to_dict() - adventure_data presente: True ({scene_count} escenas), current_scene_id: {scene_id}")
            else:
                self.logger.warning(f"[CampaignManager] to_dict() - adventure_data presente pero no es dict: {type(adventure)}")
        else:
            self.logger.warning(f"[CampaignManager] to_dict() - adventure_data NO presente, current_scene_id: {scene_id}")
        return state_copy
