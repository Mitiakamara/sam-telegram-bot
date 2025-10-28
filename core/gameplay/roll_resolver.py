# sam-telegram-bot/core/gameplay/roll_resolver.py
"""
Conecta el resultado de las tiradas con el Scene Manager y el Story Director.
Cada tirada puede generar una nueva escena según su resultado.
"""
from core.scene_manager.scene_manager import SceneManager
from core.dice_roller.parser import perform_roll
from core.dice_roller.intent_mapper import detect_attribute_from_text
from core.story_director.story_director import StoryDirector

scene_manager = SceneManager()
story_director = StoryDirector()  # genera nuevas escenas dinámicas

async def resolve_action(update, player_name: str, text: str, orchestrator):
    """
    Procesa la acción del jugador, realiza la tirada y genera
    una escena dinámica basada en el resultado.
    """
    # 1️⃣ Detectar atributo relevante
    ab_code = detect_attribute_from_text(text)
    if not ab_code:
        return None  # acción puramente narrativa, sin tirada

    # 2️⃣ Ejecutar tirada completa
    roll_msg = perform_roll(player_name, text)

    # 3️⃣ Extraer total numérico del resultado
    import re
    m = re.search(r"= (\d+)", roll_msg)
    total = int(m.group(1)) if m else 10

    # 4️⃣ Clasificar resultado
    if total >= 20:
        effect = "critical_success"
    elif total >= 15:
        effect = "success"
    elif total >= 10:
        effect = "partial_success"
    elif total >= 5:
        effect = "failure"
    else:
        effect = "critical_failure"

    # 5️⃣ Generar nueva escena según efecto
    new_scene = None
    if effect == "critical_success":
        new_scene = story_director.generate_scene(template="triumph_scene", cause=text)
    elif effect == "success":
        new_scene = story_director.generate_scene(template="progress_scene", cause=text)
    elif effect == "partial_success":
        new_scene = story_director.generate_scene(template="tension_scene", cause=text)
    elif effect == "failure":
        new_scene = story_director.generate_scene(template="setback_scene", cause=text)
    elif effect == "critical_failure":
        new_scene = story_director.generate_scene(template="complication_scene", cause=text)

    # 6️⃣ Actualizar Scene Manager
    if new_scene:
        scene_manager.add_scene(new_scene)
        orchestrator.set_active_scene(new_scene)
        msg_suffix = f"\n\n📜 *Nueva escena generada:* `{new_scene['title']}`"
    else:
        msg_suffix = "\n\n⚖️ La escena actual continúa en desarrollo."

    # 7️⃣ Ajustar mood global
    if hasattr(orchestrator, "apply_feedback"):
        if effect in ["critical_success", "success"]:
            orchestrator.apply_feedback("excited", +0.2)
        elif effect in ["failure", "critical_failure"]:
            orchestrator.apply_feedback("tension", +0.1)

    # 8️⃣ Responder al jugador
    await update.message.reply_markdown(roll_msg + msg_suffix)
    await orchestrator.sync_scene_state()
    return roll_msg + msg_suffix
