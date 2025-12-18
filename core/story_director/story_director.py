import json
import os
import logging
from typing import Dict, Any, Optional

from core.campaign.campaign_manager import CampaignManager
from core.auto_narrator import AutoNarrator
from core.character_builder import CharacterBuilder
from core.story_director.scene_template_engine import generate_scene_from_template
from core.story_director.transition_engine import TransitionEngine

logger = logging.getLogger(__name__)


class EmotionalTracker:
    """
    Versión mínima para no romper cuando el handler llama a get_current_emotion().
    """
    def __init__(self) -> None:
        self.current_emotion = "neutral"
        logger.info("[EmotionalTracker] Inicializado correctamente.")

    def get_current_emotion(self) -> str:
        return self.current_emotion

    def set_emotion(self, emotion: str) -> None:
        self.current_emotion = emotion


class StoryDirector:
    """
    Orquesta la historia, los jugadores y la campaña.
    """

    STATE_PATH = "data/story_director_state.json"

    def __init__(self) -> None:
        self.emotion_tracker = EmotionalTracker()
        self.campaign_manager = CampaignManager()
        self.auto_narrator = AutoNarrator()
        self.character_builder = CharacterBuilder()
        self.transition_engine = TransitionEngine()
        self.players: Dict[int, Dict[str, Any]] = {}
        self.last_decision: Optional[Dict[str, Any]] = None

        # intentar cargar estado previo
        self._ensure_data_dir()
        self._load_state()

    # ------------------------------------------------------------------
    # Persistencia básica
    # ------------------------------------------------------------------
    def _ensure_data_dir(self) -> None:
        os.makedirs("data", exist_ok=True)

    def _load_state(self) -> None:
        if os.path.exists(self.STATE_PATH):
            try:
                with open(self.STATE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.players = data.get("players", {})
                campaign_data = data.get("campaign", {})
                
                # Verificar que adventure_data esté en campaign_data antes de cargar
                adventure_data_in_file = 'adventure_data' in campaign_data and campaign_data.get('adventure_data') is not None
                campaign_name_in_file = campaign_data.get('campaign_name', '')
                current_scene_id_in_file = campaign_data.get('current_scene_id')
                
                if adventure_data_in_file:
                    adventure = campaign_data.get('adventure_data')
                    if isinstance(adventure, dict) and "scenes" in adventure:
                        scene_count = len(adventure.get('scenes', []))
                        logger.info(f"[StoryDirector] _load_state - adventure_data presente en archivo ({scene_count} escenas), campaign_name: {campaign_name_in_file}, current_scene_id: {current_scene_id_in_file}")
                    else:
                        logger.warning(f"[StoryDirector] _load_state - adventure_data en archivo pero no tiene estructura válida")
                else:
                    logger.warning(f"[StoryDirector] _load_state - adventure_data NO presente en archivo. campaign_name: {campaign_name_in_file}, current_scene_id: {current_scene_id_in_file}")
                
                self.campaign_manager.load_from_dict(campaign_data)
                
                # Verificar y corregir current_scene si tiene un nombre de archivo JSON
                current_scene = self.campaign_manager.state.get("current_scene", "")
                if current_scene and current_scene.endswith(".json"):
                    logger.warning(f"[StoryDirector] current_scene tiene nombre de archivo JSON: {current_scene}. Corrigiendo...")
                    # Si hay adventure_data, usar el título de la escena actual
                    adventure_data = self.campaign_manager.state.get("adventure_data")
                    current_scene_id = self.campaign_manager.state.get("current_scene_id")
                    if adventure_data and current_scene_id:
                        from core.adventure.adventure_loader import AdventureLoader
                        loader = AdventureLoader()
                        scene = loader.find_scene_by_id(adventure_data, current_scene_id)
                        if scene:
                            self.campaign_manager.state["current_scene"] = scene.get("title", "Escena")
                            logger.info(f"[StoryDirector] current_scene corregido a: {self.campaign_manager.state['current_scene']}")
                    else:
                        # Fallback: usar un nombre genérico
                        self.campaign_manager.state["current_scene"] = "Escena actual"
                        logger.info(f"[StoryDirector] current_scene corregido a: Escena actual")
                
                logger.info("[StoryDirector] Estado cargado correctamente.")
            except Exception as e:
                logger.warning(f"[StoryDirector] No se pudo cargar el estado: {e}")

    def _save_state(self) -> None:
        campaign_dict = self.campaign_manager.to_dict()
        
        # Verificar que adventure_data está en el diccionario antes de guardar
        adventure_data_in_dict = 'adventure_data' in campaign_dict and campaign_dict.get('adventure_data') is not None
        current_scene_id_in_dict = campaign_dict.get('current_scene_id')
        campaign_name_in_dict = campaign_dict.get('campaign_name', '')
        
        if adventure_data_in_dict:
            adventure = campaign_dict.get('adventure_data')
            if isinstance(adventure, dict):
                scene_count = len(adventure.get('scenes', []))
                logger.info(f"[StoryDirector] _save_state - adventure_data presente en to_dict() ({scene_count} escenas), current_scene_id: {current_scene_id_in_dict}, campaign_name: {campaign_name_in_dict}")
            else:
                logger.warning(f"[StoryDirector] _save_state - adventure_data en to_dict() pero no es dict: {type(adventure)}")
        else:
            logger.error(f"[StoryDirector] _save_state - ERROR: adventure_data NO está en to_dict()! campaign_name: {campaign_name_in_dict}, current_scene_id: {current_scene_id_in_dict}")
        
        data = {
            "players": self.players,
            "campaign": campaign_dict,
        }
        
        try:
            # Intentar serializar para verificar que no hay problemas
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            json_size = len(json_str)
            logger.info(f"[StoryDirector] Estado serializado correctamente. Tamaño: {json_size} bytes")
            
            with open(self.STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Verificar que se guardó correctamente
            if adventure_data_in_dict:
                try:
                    with open(self.STATE_PATH, "r", encoding="utf-8") as f:
                        saved_data = json.load(f)
                        saved_campaign = saved_data.get("campaign", {})
                        saved_has_adventure = 'adventure_data' in saved_campaign and saved_campaign.get('adventure_data') is not None
                        if saved_has_adventure:
                            saved_adventure = saved_campaign.get('adventure_data')
                            if isinstance(saved_adventure, dict):
                                saved_scene_count = len(saved_adventure.get('scenes', []))
                                logger.info(f"[StoryDirector] Estado guardado y verificado. adventure_data en archivo: True ({saved_scene_count} escenas)")
                            else:
                                logger.warning(f"[StoryDirector] adventure_data guardado pero no es dict: {type(saved_adventure)}")
                        else:
                            logger.error(f"[StoryDirector] ERROR: adventure_data NO se guardó en el archivo aunque estaba presente antes de guardar!")
                except Exception as e:
                    logger.warning(f"[StoryDirector] No se pudo verificar el archivo guardado: {e}", exc_info=True)
            
            logger.info("[StoryDirector] Estado guardado.")
        except Exception as e:
            logger.error(f"[StoryDirector] No se pudo guardar el estado: {e}", exc_info=True)

    # ------------------------------------------------------------------
    # Gestión de jugadores
    # ------------------------------------------------------------------
    def create_player_character(self, user_id: int, name: str) -> Dict[str, Any]:
        """
        Crea un PJ con el CharacterBuilder y lo asocia al user_id.
        """
        character = self.character_builder.create_character(name)
        self.players[user_id] = character
        # lo añadimos a la campaña
        self.campaign_manager.add_player(user_id, name)
        self._save_state()
        logger.info(f"[StoryDirector] Personaje creado para {user_id}: {name}")
        return character

    def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.players.get(user_id)

    def get_player_status(self, user_id: int) -> Dict[str, Any]:
        """
        Devuelve algo seguro aunque no exista el jugador.
        """
        player = self.players.get(user_id)
        emotion = self.emotion_tracker.get_current_emotion()
        if not player:
            return {
                "found": False,
                "message": "No se encontró al jugador en la campaña.",
                "emotion": emotion,
            }
        return {
            "found": True,
            "player": player,
            "emotion": emotion,
        }

    # ------------------------------------------------------------------
    # Narrativa / campaña
    # ------------------------------------------------------------------
    def get_current_scene(self) -> Dict[str, Any]:
        """
        Obtiene la escena actual, ya sea de una aventura cargada o generada.
        """
        # Primero verificar si hay una aventura cargada
        adventure_data = self.campaign_manager.state.get("adventure_data")
        current_scene_id = self.campaign_manager.state.get("current_scene_id")
        campaign_name = self.campaign_manager.state.get("campaign_name", "")
        
        logger.info(f"[StoryDirector] get_current_scene - campaign_name: {campaign_name}, adventure_data exists: {adventure_data is not None}, current_scene_id: {current_scene_id}")
        
        # Si adventure_data es None pero hay campaign_name, intentar recargar inmediatamente
        # IMPORTANTE: Recargar si campaign_name existe y no es un valor por defecto
        default_campaigns = ["TheGeniesWishes", "The Genie's Wishes – Chapter 1: Cold Open"]
        if not adventure_data and campaign_name and campaign_name not in default_campaigns:
            logger.warning(f"[StoryDirector] adventure_data es None pero campaign_name='{campaign_name}'. Recargando aventura...")
            try:
                self.load_campaign(campaign_name)
                # Actualizar variables después de recargar
                adventure_data = self.campaign_manager.state.get("adventure_data")
                current_scene_id = self.campaign_manager.state.get("current_scene_id")
                logger.info(f"[StoryDirector] Después de recargar - adventure_data: {adventure_data is not None}, current_scene_id: {current_scene_id}")
                if not adventure_data:
                    logger.error(f"[StoryDirector] ERROR CRÍTICO: Después de recargar '{campaign_name}', adventure_data sigue siendo None!")
            except Exception as e:
                logger.error(f"[StoryDirector] Error al recargar aventura en get_current_scene: {e}", exc_info=True)
        
        if adventure_data and current_scene_id:
            # Buscar la escena en la aventura
            from core.adventure.adventure_loader import AdventureLoader
            loader = AdventureLoader()
            scene = loader.find_scene_by_id(adventure_data, current_scene_id)
            if scene:
                logger.info(f"[StoryDirector] Found adventure scene: {scene.get('title', 'Unknown')} (ID: {current_scene_id})")
                # NO pasar por auto_narrator para escenas de aventura - usar narración directa
                return {
                    "found": True,
                    "scene": scene,
                    "narrated": "",  # No usar auto_narrator para aventuras
                    "from_adventure": True,
                }
            else:
                logger.warning(f"[StoryDirector] Scene ID '{current_scene_id}' not found in adventure data. Available scenes: {[s.get('scene_id') for s in adventure_data.get('scenes', [])]}")
        elif campaign_name and campaign_name not in default_campaigns:
            # Hay una campaña cargada pero no hay adventure_data - intentar recargar
            logger.warning(f"[StoryDirector] Campaign '{campaign_name}' está cargada pero no hay adventure_data. Intentando recargar...")
            try:
                self.load_campaign(campaign_name)
                # Intentar de nuevo
                adventure_data = self.campaign_manager.state.get("adventure_data")
                current_scene_id = self.campaign_manager.state.get("current_scene_id")
                logger.info(f"[StoryDirector] Después de recargar (segunda verificación) - adventure_data: {adventure_data is not None}, current_scene_id: {current_scene_id}")
                if adventure_data and current_scene_id:
                    from core.adventure.adventure_loader import AdventureLoader
                    loader = AdventureLoader()
                    scene = loader.find_scene_by_id(adventure_data, current_scene_id)
                    if scene:
                        logger.info(f"[StoryDirector] Recargada aventura y encontrada escena: {scene.get('title', 'Unknown')}")
                        return {
                            "found": True,
                            "scene": scene,
                            "narrated": "",
                            "from_adventure": True,
                        }
                else:
                    logger.error(f"[StoryDirector] ERROR: Después de recargar '{campaign_name}', adventure_data o current_scene_id siguen siendo None")
            except Exception as e:
                logger.error(f"[StoryDirector] Error al recargar aventura: {e}", exc_info=True)
        
        # Fallback: escena del campaign manager
        # Pero primero verificar si hay una escena guardada en el estado
        current_scene_name = self.campaign_manager.state.get("current_scene", "")
        
        # Si current_scene_name es "progress_scene.json" o similar, es un error
        if current_scene_name and current_scene_name.endswith(".json"):
            logger.warning(f"[StoryDirector] current_scene tiene un nombre de archivo JSON: {current_scene_name}. Esto es un error.")
            # Intentar recargar la aventura si hay campaign_name
            default_campaigns = ["TheGeniesWishes", "The Genie's Wishes – Chapter 1: Cold Open"]
            if campaign_name and campaign_name not in default_campaigns:
                try:
                    logger.info(f"[StoryDirector] Intentando recargar aventura '{campaign_name}' para corregir current_scene")
                    self.load_campaign(campaign_name)
                    # Intentar de nuevo después de recargar
                    adventure_data = self.campaign_manager.state.get("adventure_data")
                    current_scene_id = self.campaign_manager.state.get("current_scene_id")
                    logger.info(f"[StoryDirector] Después de recargar (tercera verificación) - adventure_data: {adventure_data is not None}, current_scene_id: {current_scene_id}")
                    if adventure_data and current_scene_id:
                        from core.adventure.adventure_loader import AdventureLoader
                        loader = AdventureLoader()
                        scene = loader.find_scene_by_id(adventure_data, current_scene_id)
                        if scene:
                            logger.info(f"[StoryDirector] Recargada aventura y encontrada escena: {scene.get('title', 'Unknown')}")
                            return {
                                "found": True,
                                "scene": scene,
                                "narrated": "",
                                "from_adventure": True,
                            }
                    else:
                        logger.error(f"[StoryDirector] ERROR: Después de recargar '{campaign_name}' (tercera verificación), adventure_data o current_scene_id siguen siendo None")
                except Exception as e:
                    logger.error(f"[StoryDirector] Error al recargar aventura: {e}", exc_info=True)
        
        if current_scene_name and current_scene_name != "Escena no definida" and not current_scene_name.endswith(".json"):
            # Intentar construir una escena básica desde el nombre
            scene = {
                "title": current_scene_name,
                "description": f"Escena: {current_scene_name}",
            }
            narrated = self.auto_narrator.narrate_scene(scene)
            # Verificar que narrated no contenga "progress_scene.json"
            if "progress_scene.json" in narrated:
                logger.warning(f"[StoryDirector] auto_narrator devolvió 'progress_scene.json', usando título directo")
                narrated = f"📜 *{current_scene_name}*\n\n{current_scene_name}"
            return {
                "found": True,
                "scene": scene,
                "narrated": narrated,
                "from_adventure": False,
            }
        
        # Último fallback: get_active_scene del campaign manager
        scene = self.campaign_manager.get_active_scene()
        if not scene:
            return {
                "found": False,
                "message": "No hay ninguna escena activa.",
            }
        # Podríamos pasarla por el auto narrador
        narrated = self.auto_narrator.narrate_scene(scene)
        # Verificar que narrated no contenga "progress_scene.json"
        if "progress_scene.json" in narrated:
            logger.warning(f"[StoryDirector] auto_narrator devolvió 'progress_scene.json' en fallback, usando título de escena")
            scene_title = scene.get("title", "Escena")
            narrated = f"📜 *{scene_title}*\n\n{scene.get('description', scene_title)}"
        return {
            "found": True,
            "scene": scene,
            "narrated": narrated,
            "from_adventure": False,
        }

    def get_campaign_progress(self) -> Dict[str, Any]:
        return self.campaign_manager.get_progress()

    # ------------------------------------------------------------------
    # Utilidades llamadas por handlers
    # ------------------------------------------------------------------
    def ensure_player(self, user_id: int, username: str) -> Dict[str, Any]:
        """
        Si el jugador no existe, se crea rápido con su username.
        Útil para /join.
        """
        if user_id not in self.players:
            self.create_player_character(user_id, username)
        return self.players[user_id]

    # ------------------------------------------------------------------
    # Métodos requeridos por los handlers
    # ------------------------------------------------------------------
    def render_current_scene(self) -> str:
        """
        Renderiza la escena actual como texto para mostrar al usuario.
        Retorna un string formateado.
        """
        # PRIMERO: Verificar directamente si hay adventure_data y current_scene_id
        # Esto evita problemas de persistencia
        adventure_data = self.campaign_manager.state.get("adventure_data")
        current_scene_id = self.campaign_manager.state.get("current_scene_id")
        campaign_name = self.campaign_manager.state.get("campaign_name", "")
        
        # Si hay adventure_data, intentar mostrar la escena directamente
        if adventure_data and current_scene_id:
            from core.adventure.adventure_loader import AdventureLoader
            loader = AdventureLoader()
            scene = loader.find_scene_by_id(adventure_data, current_scene_id)
            if scene:
                narration = scene.get("narration", "")
                title = scene.get("title", "Escena")
                options_text = scene.get("options_text", [])
                options_list = ""
                if options_text:
                    options_list = "\n\n*Opciones disponibles:*\n" + "\n".join(f"• {opt}" for opt in options_text)
                return f"🎭 *{title}*\n\n{narration}{options_list}"
        
        # Si no hay adventure_data pero hay campaign_name, intentar recargar
        default_campaigns = ["TheGeniesWishes", "The Genie's Wishes – Chapter 1: Cold Open"]
        if not adventure_data and campaign_name and campaign_name not in default_campaigns:
            logger.warning(f"[StoryDirector] render_current_scene: adventure_data es None, recargando '{campaign_name}'")
            try:
                self.load_campaign(campaign_name)
                # Intentar de nuevo
                adventure_data = self.campaign_manager.state.get("adventure_data")
                current_scene_id = self.campaign_manager.state.get("current_scene_id")
                logger.info(f"[StoryDirector] render_current_scene: Después de recargar - adventure_data: {adventure_data is not None}, current_scene_id: {current_scene_id}")
                if adventure_data and current_scene_id:
                    from core.adventure.adventure_loader import AdventureLoader
                    loader = AdventureLoader()
                    scene = loader.find_scene_by_id(adventure_data, current_scene_id)
                    if scene:
                        narration = scene.get("narration", "")
                        title = scene.get("title", "Escena")
                        options_text = scene.get("options_text", [])
                        options_list = ""
                        if options_text:
                            options_list = "\n\n*Opciones disponibles:*\n" + "\n".join(f"• {opt}" for opt in options_text)
                        return f"🎭 *{title}*\n\n{narration}{options_list}"
                else:
                    logger.error(f"[StoryDirector] ERROR: Después de recargar '{campaign_name}' en render_current_scene, adventure_data o current_scene_id siguen siendo None")
            except Exception as e:
                logger.error(f"[StoryDirector] Error al recargar aventura en render_current_scene: {e}", exc_info=True)
        
        # Fallback: usar get_current_scene()
        scene_data = self.get_current_scene()
        if not scene_data.get("found"):
            return f"🎭 *Escena actual*\n\n{scene_data.get('message', 'No hay escena activa.')}"
        
        scene = scene_data.get("scene", {})
        
        # Si es de una aventura, usar la narración de la aventura
        if scene_data.get("from_adventure"):
            narration = scene.get("narration", "")
            title = scene.get("title", "Escena")
            
            # Mostrar opciones si existen
            options_text = scene.get("options_text", [])
            options_list = ""
            if options_text:
                options_list = "\n\n*Opciones disponibles:*\n" + "\n".join(f"• {opt}" for opt in options_text)
            
            return f"🎭 *{title}*\n\n{narration}{options_list}"
        
        # Escena generada (fallback)
        narrated = scene_data.get("narrated", "")
        if narrated and narrated.strip():
            # Si la narración contiene "progress_scene.json", es un error - usar título de escena
            if "progress_scene.json" in narrated:
                logger.warning(f"[StoryDirector] render_current_scene recibió 'progress_scene.json' en narrated, usando título de escena")
                title = scene.get("title", "Escena")
                # Si el título también es "progress_scene.json", usar current_scene del estado
                if title == "progress_scene.json" or title.endswith(".json"):
                    current_scene_name = self.campaign_manager.state.get("current_scene", "Escena actual")
                    if current_scene_name and not current_scene_name.endswith(".json"):
                        title = current_scene_name
                    else:
                        title = "Escena actual"
                desc = scene.get("description", scene.get("description_adapted", ""))
                if not desc or desc == "progress_scene.json" or desc.endswith(".json"):
                    desc = title
                return f"🎭 *{title}*\n\n{desc}" if desc else f"🎭 *{title}*"
            return narrated
        
        title = scene.get("title", "Escena")
        # Si el título es "progress_scene.json", usar current_scene del estado
        if title == "progress_scene.json" or title.endswith(".json"):
            current_scene_name = self.campaign_manager.state.get("current_scene", "Escena actual")
            if current_scene_name and not current_scene_name.endswith(".json"):
                title = current_scene_name
            else:
                title = "Escena actual"
        desc = scene.get("description", scene.get("description_adapted", ""))
        if not desc or desc == "progress_scene.json" or desc.endswith(".json"):
            desc = title
        return f"🎭 *{title}*\n\n{desc}" if desc else f"🎭 *{title}*"

    def trigger_event(self, event_type: str) -> str:
        """
        Dispara un evento narrativo y genera la siguiente escena.
        Retorna un string con la descripción del evento y la nueva escena.
        """
        current_emotion = self.emotion_tracker.get_current_emotion()
        
        # Usar el transition engine para decidir la próxima escena
        next_scene_template = self.transition_engine.get_next_scene(current_emotion, event_type)
        # Remover .json si está presente
        template_name = next_scene_template.replace(".json", "")
        
        # Generar la nueva escena
        mood = {
            "mood_state": current_emotion,
            "mood_intensity": 0.7
        }
        new_scene = generate_scene_from_template(template_name, cause=event_type, mood=mood)
        
        # Actualizar la escena en el campaign manager
        scene_title = new_scene.get("title", "Nueva escena")
        self.campaign_manager.set_current_scene(scene_title)
        
        # Actualizar emoción si es necesario
        if event_type in ["combat_victory", "triumph"]:
            self.emotion_tracker.set_emotion("triumph")
        elif event_type in ["setback", "loss"]:
            self.emotion_tracker.set_emotion("setback")
        elif event_type == "rally":
            self.emotion_tracker.set_emotion("progress")
        
        self._save_state()
        
        # Renderizar la nueva escena
        return self.render_current_scene()

    def restart_campaign(self) -> None:
        """
        Reinicia la campaña desde el inicio.
        """
        self.campaign_manager.state.update({
            "campaign_name": "TheGeniesWishes",
            "chapter": 1,
            "current_scene": "Oasis perdido",
            "active_party": []
        })
        self.emotion_tracker.set_emotion("neutral")
        self._save_state()
        logger.info("[StoryDirector] Campaña reiniciada.")

    def load_campaign(self, slug: str) -> None:
        """
        Carga una campaña por su slug desde archivos JSON en adventures/.
        Inicializa el estado del juego con las escenas y datos de la aventura.
        """
        from core.adventure.adventure_loader import AdventureLoader
        
        loader = AdventureLoader()
        adventure_data = loader.load_adventure(slug)
        
        if not adventure_data:
            raise ValueError(f"Aventura '{slug}' no encontrada. Aventuras disponibles: {', '.join(loader.list_available_adventures())}")
        
        # Validar estructura
        is_valid, error = loader.validate_adventure(adventure_data)
        if not is_valid:
            raise ValueError(f"Aventura '{slug}' inválida: {error}")
        
        # Obtener información de la aventura
        info = loader.get_adventure_info(adventure_data)
        
        # Actualizar estado de campaña
        self.campaign_manager.state["campaign_name"] = slug
        self.campaign_manager.state["campaign_title"] = info["title"]
        self.campaign_manager.state["chapter"] = 1
        self.campaign_manager.state["adventure_data"] = adventure_data  # Guardar datos completos
        
        # Obtener escena inicial
        initial_scene = loader.get_initial_scene(adventure_data)
        if initial_scene:
            scene_title = initial_scene.get("title", "Inicio")
            scene_id = initial_scene.get("scene_id")
            # Asegurar que current_scene sea el título, no un ID o nombre de archivo
            self.campaign_manager.state["current_scene"] = scene_title
            self.campaign_manager.state["current_scene_id"] = scene_id
            self.campaign_manager.state["adventure_scenes"] = adventure_data.get("scenes", [])
            logger.info(f"[StoryDirector] Escena inicial configurada: {scene_title} (ID: {scene_id})")
            logger.info(f"[StoryDirector] Verificación: current_scene='{self.campaign_manager.state['current_scene']}', current_scene_id='{scene_id}'")
        else:
            self.campaign_manager.state["current_scene"] = "Inicio"
            logger.warning(f"[StoryDirector] No se encontró escena inicial en la aventura")
        
        # Guardar estado en CampaignManager (que persiste en JSON)
        # IMPORTANTE: Guardar adventure_data completo
        self.campaign_manager._save_state()
        
        # Verificar que adventure_data se guardó correctamente
        adventure_data_saved = 'adventure_data' in self.campaign_manager.state
        current_scene_id_saved = self.campaign_manager.state.get('current_scene_id')
        logger.info(f"[StoryDirector] Estado guardado en CampaignManager. adventure_data: {adventure_data_saved}, current_scene_id: {current_scene_id_saved}")
        
        # También guardar en StoryDirector (que usa campaign_manager.to_dict())
        self._save_state()
        
        # Verificar que se guardó en ambos lugares
        logger.info(f"[StoryDirector] Campaña '{slug}' cargada: {info['title']} ({info['total_scenes']} escenas)")
        logger.info(f"[StoryDirector] Verificación: adventure_data en state: {'adventure_data' in self.campaign_manager.state}, current_scene_id: {self.campaign_manager.state.get('current_scene_id')}")

    def decide_next_scene_type(self) -> str:
        """
        Decide el tipo de la próxima escena basándose en el estado actual.
        Retorna un string con el tipo de escena (ej: "progress_scene", "tension_scene").
        """
        current_emotion = self.emotion_tracker.get_current_emotion()
        # Por defecto, usar progress_scene
        next_type = self.transition_engine.get_next_scene(current_emotion, "neutral")
        # Remover .json si está presente
        return next_type.replace(".json", "")

    def generate_scene(self, template: str, cause: str = "") -> Dict[str, Any]:
        """
        Genera una nueva escena a partir de una plantilla.
        Retorna un diccionario con la escena generada.
        """
        current_emotion = self.emotion_tracker.get_current_emotion()
        mood = {
            "mood_state": current_emotion,
            "mood_intensity": 0.7
        }
        scene = generate_scene_from_template(template, cause=cause, mood=mood)
        
        # Actualizar la escena en el campaign manager
        scene_title = scene.get("title", "Nueva escena")
        self.campaign_manager.set_current_scene(scene_title)
        self._save_state()
        
        return scene

