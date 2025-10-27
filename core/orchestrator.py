# sam-telegram-bot/core/orchestrator.py
"""
Orchestrator
------------
Control central de la narrativa. Coordina la comunicación entre:

- GameService (acciones de jugador)
- SceneManager (gestión de escenas)
- StoryDirector (motor narrativo adaptativo)
- DirectorLink (puente entre resultados de juego y decisiones narrativas)

El objetivo es mantener una historia coherente y emocionalmente dinámica.
"""

import asyncio
from core.scene_manager.scene_manager import SceneManager
from core.services.game_service import GameService
from core.services.state_service import StateService
from core.renderer import render
from core.story_director.director_link import DirectorLink


class Orchestrator:
    """
    Orquesta la narrativa del juego entre el motor de juego (GameAPI),
    el SceneManager (narrativa adaptativa) y la interfaz Telegram.
    """

    def __init__(self):
        self.scene_manager = SceneManager()
        self.game_service = GameService()
        self.state_service = StateService()
        self.story_director = self.scene_manager.story_director  # referencia directa
        self.director_link = DirectorLink(self.story_director)

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

        # Caso general: procesar interacción dentro de la escena
        active_scene = self.scene_manager.get_active_scene()
        if not active_scene:
            return render("No hay ninguna escena activa en este momento.")

        # Enviar acción al GameService
        game_response = await self.game_service.process_action(player_id, text)

        # Si el GameService devuelve un dict, conectar con el StoryDirector
        if isinstance(game_response, dict):
            scene_text = await self.director_link.process_game_result(game_response)
        else:
            # fallback: si GameAPI devolvió un texto plano
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
    # 🔹 INICIO DE NUEVA SESIÓN
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
    # 🔹 RESUMEN DEL ESTADO ACTUAL
    # ==========================================================
    async def get_story_summary(self):
        """Devuelve el resumen narrativo del estado actual."""
        return render(self.scene_manager.summarize_scene())
