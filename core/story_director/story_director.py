import logging
from core.emotion.emotional_tracker import EmotionalTracker
from core.auto_narrator.auto_narrator import AutoNarrator
from core.campaign.campaign_manager import CampaignManager

logger = logging.getLogger("StoryDirector")


class StoryDirector:
    """
    Control central de la narrativa y el estado emocional del mundo.
    Coordina personajes, escenas y el tono narrativo global.
    """

    def __init__(self):
        self.players = {}
        self.emotion_tracker = EmotionalTracker()
        self.narrator = AutoNarrator()
        self.campaign_manager = CampaignManager()
        logger.info("[StoryDirector] Inicializado correctamente.")

    # ============================================================
    # 👥 Gestión de jugadores
    # ============================================================

    def add_player(self, player_data):
        """Agrega un jugador al registro de la historia."""
        player_id = player_data.get("id") or player_data.get("user_id")
        if not player_id:
            logger.warning("[StoryDirector] No se pudo agregar jugador: falta ID.")
            return False

        self.players[player_id] = player_data
        logger.info(f"[StoryDirector] Personaje añadido: {player_data.get('name', 'Desconocido')}")
        return True

    def get_player(self, player_id):
        return self.players.get(player_id)

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            logger.info(f"[StoryDirector] Jugador {player_id} eliminado de la campaña.")

    # ============================================================
    # 📖 Gestión de escenas y narrativa
    # ============================================================

    def get_current_scene(self):
        """Obtiene la escena activa desde CampaignManager."""
        state = self.campaign_manager.get_state()
        return state.get("current_scene") if state else None

    def set_scene(self, scene_id, scene_data):
        """Actualiza la escena activa en la campaña."""
        self.campaign_manager.update_scene(scene_id, scene_data)
        logger.info(f"[StoryDirector] Escena actualizada: {scene_id}")

    def generate_scene_description(self):
        """Genera una descripción adaptada según el estado emocional."""
        emotion = self.emotion_tracker.current_emotion or "neutral"
        base_scene = self.get_current_scene() or "No hay ninguna escena activa."
        description = self.narrator.generate_description(base_scene, emotion)
        logger.info(f"[StoryDirector] Descripción generada con emoción '{emotion}'.")
        return description

    # ============================================================
    # 💬 Estado del jugador
    # ============================================================

    def get_player_status(self, player_id):
        """Devuelve el estado actual del jugador con tono y emoción."""
        player = self.get_player(player_id)
        if not player:
            return "❌ No se encontró al jugador en la campaña."

        # Corregido: acceder al atributo directamente
        emotion = getattr(self.emotion_tracker, "current_emotion", "neutral") or "neutral"

        return (
            f"🧙 Personaje: {player.get('name', 'Desconocido')}\n"
            f"🎭 Estado emocional: {emotion}\n"
            f"⚔️ Clase: {player.get('class', '—')}\n"
            f"🎚 Nivel: {player.get('level', 1)}\n"
            f"❤️ HP: {player.get('hp', '—')}\n"
            f"💫 XP: {player.get('xp', 0)}"
        )

    # ============================================================
    # 🧭 Estado de la campaña
    # ============================================================

    def get_campaign_progress(self):
        """Devuelve información resumida sobre la campaña activa."""
        campaign = self.campaign_manager.get_state()
        if not campaign:
            return "❌ No hay campaña activa en este momento."

        chapter = campaign.get("chapter", "—")
        current_scene = campaign.get("current_scene", "Ninguna")
        completed = ", ".join(campaign.get("completed_scenes", [])) or "Ninguna"
        pending = ", ".join(campaign.get("pending_scenes", [])) or "Ninguna"
        active_players = ", ".join([p.get("name", "—") for p in self.players.values()]) or "Ninguno"

        return (
            f"📘 Campaña: {campaign.get('name', 'Sin nombre')}\n"
            f"📖 Capítulo: {chapter}\n"
            f"🎭 Escena activa: {current_scene}\n"
            f"🧙‍♂️ Personajes: {active_players}\n"
            f"✅ Completadas: {completed}\n"
            f"🗺️ Pendientes: {pending}"
        )

    # ============================================================
    # ⚙️ Persistencia
    # ============================================================

    def save_state(self):
        """Guarda el estado actual de la campaña."""
        try:
            self.campaign_manager.save_state()
            logger.info("[StoryDirector] Estado de campaña guardado correctamente.")
        except Exception as e:
            logger.error(f"[StoryDirector] Error al guardar el estado: {e}")

    def load_state(self):
        """Carga el estado guardado."""
        try:
            self.campaign_manager.load_state()
            logger.info("[StoryDirector] Estado de campaña cargado correctamente.")
        except Exception as e:
            logger.error(f"[StoryDirector] Error al cargar el estado: {e}")
