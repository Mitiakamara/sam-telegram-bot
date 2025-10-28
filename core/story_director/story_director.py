# sam-telegram-bot/core/story_director/story_director.py
"""
Story Director: coordina la creación dinámica de escenas y
la coherencia narrativa general del mundo.
"""

import os
import logging
from core.story_director.scene_template_engine import generate_scene_from_template

logger = logging.getLogger("SAM.StoryDirector")

class StoryDirector:
    def __init__(self, mood_manager=None):
        """
        mood_manager: objeto con get_current_mood() -> dict
        """
        self.mood_manager = mood_manager

    # ================================================================
    # 🎬 GENERACIÓN DE ESCENAS DINÁMICAS
    # ================================================================
    def generate_scene(self, template: str, cause: str = "") -> dict:
        """
        Genera una escena dinámica desde una plantilla, adaptando
        su tono según el mood global (heroic, dark, comic, etc.)
        """
        # 1️⃣ Obtener mood actual
        mood = None
        mood_state = "neutral"
        if self.mood_manager and hasattr(self.mood_manager, "get_current_mood"):
            mood = self.mood_manager.get_current_mood()
            mood_state = mood.get("mood_state", "neutral")

        # 2️⃣ Buscar plantilla adaptada al tono (por ejemplo: tension_scene_dark.json)
        base_name = template
        specialized_template = f"{template}_{mood_state}"
        templates_dir = os.path.join("core", "story_director", "scene_templates")
        specialized_path = os.path.join(templates_dir, f"{specialized_template}.json")

        # 3️⃣ Verificar si existe versión adaptada
        if os.path.exists(specialized_path):
            selected_template = specialized_template
            logger.info(f"🎭 Usando plantilla adaptada al tono: {specialized_template}")
        else:
            selected_template = base_name
            logger.info(f"🎭 Usando plantilla base: {template}")

        # 4️⃣ Generar escena desde el motor de plantillas
        scene = generate_scene_from_template(selected_template, cause, mood)

        # 5️⃣ Ajuste de narrativa tonal adicional (intensidad)
        if mood and "mood_intensity" in mood:
            if mood["mood_intensity"] > 0.7:
                scene["description_adapted"] += " La atmósfera se siente cargada de energía."
            elif mood["mood_intensity"] < 0.3:
                scene["description_adapted"] += " Todo parece calmo, casi en exceso."

        # 6️⃣ Registrar escena
        logger.info(f"🎬 Nueva escena generada ({scene['scene_id']}): {scene['title']}")
        return scene

    # ================================================================
    # 🔧 (Opcional) ENLACE CON ORCHESTRATOR
    # ================================================================
    def link_orchestrator(self, orchestrator):
        """
        Permite que el Story Director acceda al Orchestrator para sincronizar
        cambios de estado, emociones o transiciones complejas.
        """
        self.orchestrator = orchestrator
        logger.info("🔗 Story Director vinculado al Orchestrator.")

    # ================================================================
    # 🧭 (Opcional) FUTURO: RAMIFICACIÓN NARRATIVA
    # ================================================================
    def suggest_next_scene_type(self, last_effect: str) -> str:
        """
        Determina el tipo probable de la próxima escena según el resultado anterior.
        """
        mapping = {
            "critical_success": "progress_scene",
            "success": "progress_scene",
            "partial_success": "tension_scene",
            "failure": "setback_scene",
            "critical_failure": "complication_scene",
        }
        return mapping.get(last_effect, "progress_scene")
