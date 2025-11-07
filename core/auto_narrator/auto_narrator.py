from typing import Dict, Any


class AutoNarrator:
    """
    Narrador automático mínimo.
    Recibe una escena y devuelve un texto bonito.
    """

    def narrate_scene(self, scene: Dict[str, Any]) -> str:
        if not scene:
            return "El silencio del desierto lo cubre todo."
        title = scene.get("title", "Escena")
        desc = scene.get("description", "")
        return f"📜 *{title}*\n\n{desc}"
