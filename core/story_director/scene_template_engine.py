# sam-telegram-bot/core/story_director/scene_template_engine.py
"""
Scene Templates Engine
Genera escenas dinámicas a partir de plantillas SRD-safe, tono narrativo y contexto.
Usado por StoryDirector.generate_scene(template, cause)
"""

import json, os, random, datetime

TEMPLATES_DIR = os.path.join("core", "story_director", "scene_templates")

def load_template(template_name: str) -> dict | None:
    """Carga la plantilla JSON del tipo solicitado."""
    path = os.path.join(TEMPLATES_DIR, f"{template_name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def adapt_template_to_mood(template: dict, mood_state: str = "neutral", intensity: float = 0.5) -> dict:
    """
    Ajusta la descripción base de la plantilla al tono actual.
    mood_state: e.g. 'heroic', 'dark', 'mystery', 'comic', 'grim', etc.
    """
    base = template.copy()
    desc = base.get("description", "")

    if mood_state == "dark":
        desc = desc.replace(".", "…").replace("!", "…") + " La atmósfera se vuelve sombría."
    elif mood_state == "heroic":
        desc = "✨ " + desc + " El aire vibra con la energía de la victoria."
    elif mood_state == "mystery":
        desc += " Algo oculto parece observarte desde las sombras."
    elif mood_state == "comic":
        desc += " La situación tiene un giro inesperadamente gracioso."
    elif mood_state == "grim":
        desc += " Todo se tiñe de un tono trágico y pesado."

    base["description_adapted"] = desc
    base["emotion_intensity"] = round(intensity, 2)
    return base


def generate_scene_from_template(template_name: str, cause: str = "", mood: dict | None = None) -> dict:
    """
    Crea una nueva escena a partir de la plantilla y el mood actual.
    Retorna un diccionario compatible con SceneManager.add_scene().
    """
    template = load_template(template_name)
    if not template:
        template = {
            "title": f"Escena improvisada ({template_name})",
            "description": f"No existe plantilla para '{template_name}'. {cause}",
            "scene_type": "generic",
        }

    mood_state = mood.get("mood_state", "neutral") if mood else "neutral"
    mood_intensity = mood.get("mood_intensity", 0.5) if mood else 0.5

    scene = adapt_template_to_mood(template, mood_state, mood_intensity)

    # Adaptar placeholders
    if "{cause}" in scene["description"]:
        scene["description"] = scene["description"].replace("{cause}", cause)

    # Agregar metadatos
    scene["scene_id"] = f"scene_{random.randint(1000,9999)}"
    scene["status"] = "active"
    scene["created_at"] = datetime.datetime.now().isoformat()
    scene["cause"] = cause
    scene["mood_snapshot"] = mood_state

    return scene
