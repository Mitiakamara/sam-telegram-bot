import asyncio
from core.scene_manager.scene_manager import SceneManager
from core.services.game_service import GameService
from core.services.state_service import StateService
from core.renderer import render


class Orchestrator:
    """
    Orquesta la narrativa del juego entre el motor (gameapi),
    el SceneManager (narrativa adaptativa) y la interfaz Telegram.
    """

    def __init__(self):
        self.scene_manager = SceneManager()
        self.game_service = GameService()
        self.state_service = StateService()

    # ==========================================================
    # 🔹 ACCIÓN PRINCIPAL: PROCESAR MENSAJES DEL JUGADOR
    # ==========================================================
    async def process_player_message(self, player_id: str, text: str):
        """
        Recibe mensajes del jugador, los analiza y decide la respuesta narrativa.
        Si el texto indica cierre o avance, dispara el StoryDirector.
        """
        text_lower = text.lower().strip()

        # Caso especial: el jugador pide avanzar la historia
        if text_lower in ["/continue", "continuar", "seguir", "avanzar"]:
            return await self.handle_continue(player_id)

        # Caso general: procesar interacción dentro de escena
        active_scene = self.scene_manager.get_active_scene()
        if not active_scene:
            return render("No hay ninguna escena activa en este momento.")

        # Enviar texto del jugador al GameService (combate, checks, etc.)
        game_response = await self.game_service.process_action(player_id, text)

        # Añadir reacción emocional según resultado
        scene_text = f"{active_scene['description_adapted']}\n\n{game_response}"
        self.state_service.save_scene(active_scene)

        return render(scene_text)

    # ==========================================================
    # 🔹 ACCIÓN /CONTINUE – AVANZAR HISTORIA
    # ==========================================================
    async def handle_continue(self, player_id: str):
        """
        Llamado cuando el jugador ejecuta /continue o indica avanzar.
        Cierra la escena actual y genera la siguiente automáticamente.
        """
        current_scene = self.scene_manager.get_active_scene()
        if not current_scene:
            return render("No hay ninguna escena activa para continuar.")

        resolution_text = f"Los aventureros deciden avanzar. {current_scene['title']} llega a su fin."
        transition_text = self.scene_manager.close_scene(resolution_text)

        next_scene = self.scene_manager.get_active_scene()
        message = (
            f"🧭 *Transición narrativa:*\n{transition_text}\n\n"
            f"🎭 *Nueva escena:* {next_scene['title']}\n"
            f"📖 {next_scene['description_adapted']}"
        )

        return render(message)

    # ==========================================================
    # 🔹 REINICIO / NUEVA PARTIDA
    # ==========================================================
    async def start_new_session(self):
        """
        Reinicia el estado de la historia y crea una escena inicial.
        """
        intro_scene = self.scene_manager.create_scene(
            title="El inicio de la aventura",
            description=(
                "Una brisa fría atraviesa el valle silencioso. "
                "El grupo observa las ruinas antiguas a lo lejos, "
                "sintiendo que su viaje apenas comienza."
            ),
            scene_type="exploration"
        )
        return render(intro_scene["description_adapted"])

    # ==========================================================
    # 🔹 RESUMEN ACTUAL
    # ==========================================================
    async def get_story_summary(self):
        """Devuelve el resumen del estado narrativo actual."""
        return render(self.scene_manager.summarize_scene())
