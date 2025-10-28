# sam-telegram-bot/core/gameplay/roll_resolver.py
"""
Integra el resultado de una tirada con el Scene Manager y el Story Director.
Permite que las acciones exitosas o fallidas modifiquen el estado narrativo.
"""
from core.scene_manager.scene_manager import SceneManager
from core.dice_roller.parser import perform_roll
from core.dice_roller.intent_mapper import detect_attribute_from_text

scene_manager = SceneManager()  # instancia compartida del motor de escenas

async def resolve_action(update, player_name: str, text: str, orchestrator):
    """
    Procesa una acción del jugador, realiza la tirada adecuada
    y actualiza la escena en función del resultado.
    """
    # 1️⃣ Detectar atributo
    ab_code = detect_attribute_from_text(text)
    if not ab_code:
        # Si no hay tirada relevante, devolver al orquestador normal
        msg = await orchestrator.handle_action(player_name, text)
        return msg

    # 2️⃣ Realizar tirada
    roll_msg = perform_roll(player_name, text)

    # 3️⃣ Extraer total de la tirada
    import re
    m = re.search(r"= (\d+)", roll_msg)
    total = int(m.group(1)) if m else 10

    # 4️⃣ Determinar efecto narrativo
    effect = "neutral"
    if total >= 18:
        effect = "critical_success"
    elif total >= 14:
        effect = "success"
    elif total >= 10:
        effect = "partial_success"
    elif total >= 5:
        effect = "failure"
    else:
        effect = "critical_failure"

    # 5️⃣ Actualizar escena actual
    scene = scene_manager.get_active_scene()
    if not scene:
        return roll_msg  # sin escena activa

    # Cambiar estado o iniciar transición según resultado
    if effect in ["critical_success", "success"]:
        scene["status"] = "resolved"
        scene["description_adapted"] = f"La acción tiene éxito: {text}."
        new_scene = scene_manager.transition_to("success_event")
        await update.message.reply_text("🌟 Tu acción cambia el curso de los acontecimientos...")
        return roll_msg + f"\n\n📜 La historia progresa hacia una nueva escena: *{new_scene['title']}*"

    elif effect in ["failure", "critical_failure"]:
        scene["status"] = "complication"
        scene["description_adapted"] = f"El intento falla: {text}."
        new_scene = scene_manager.transition_to("complication_event")
        await update.message.reply_text("⚠️ Tu fallo tiene consecuencias inesperadas...")
        return roll_msg + f"\n\n💥 La tensión aumenta: *{new_scene['title']}*"

    # Parcial o neutral: mantener la misma escena pero actualizar estado
    scene["status"] = "ongoing"
    scene["description_adapted"] = f"La acción de {player_name} continúa sin resultados definitivos."
    scene_manager.update_scene(scene)

    return roll_msg + "\n\n⚖️ La escena continúa en desarrollo..."
