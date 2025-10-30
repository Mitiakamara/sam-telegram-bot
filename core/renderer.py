# ================================================================
# 🎨 RENDERER
# ================================================================
# Convierte la salida narrativa en texto Markdown listo
# para enviarse por Telegram. Versión simplificada y compatible
# con main.py (usa método render_scene()).
# ================================================================

import logging

logger = logging.getLogger("core.renderer")


class Renderer:
    """
    Convierte datos narrativos estructurados o texto puro en
    mensajes legibles para el jugador (Markdown).
    """

    def render_scene(self, scene) -> str:
        """
        Recibe dict o str y devuelve texto final.
        """
        if isinstance(scene, str):
            return scene

        title = scene.get("title", "Escena sin título")
        desc = scene.get("description", "")
        tone = scene.get("emotion", "neutral")
        scene_type = scene.get("scene_type", "generic")

        msg = f"*{title}*\n_{scene_type} | {tone}_\n\n{desc}"
        logger.info(f"[Renderer] Escena renderizada: {title} ({tone})")
        return msg
