# ================================================================
# 🎬 NARRATIVE HANDLER
# ================================================================
# Controla los comandos narrativos:
#   /scene – muestra o continúa la escena actual
#   /event <tipo> – ejecuta un evento narrativo
# ================================================================

import logging
from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("[NarrativeHandler] /scene command received")
    sd = context.bot_data.get("story_director")
    if not sd:
        logger.error("[NarrativeHandler] StoryDirector not found in bot_data")
        await update.message.reply_text("⚠️ Error: StoryDirector no disponible.")
        return
    
    # Verificar directamente si hay adventure_data antes de llamar a render_current_scene
    # Esto funciona incluso si el código desplegado es antiguo
    campaign_manager = sd.campaign_manager
    adventure_data = campaign_manager.state.get("adventure_data")
    current_scene_id = campaign_manager.state.get("current_scene_id")
    campaign_name = campaign_manager.state.get("campaign_name", "")
    current_scene = campaign_manager.state.get("current_scene", "")
    
    logger.info(f"[NarrativeHandler] Direct check - adventure_data: {adventure_data is not None}, current_scene_id: {current_scene_id}, campaign_name: {campaign_name}, current_scene: {current_scene}")
    
    # Logging detallado del estado
    if adventure_data:
        logger.info(f"[NarrativeHandler] adventure_data type: {type(adventure_data)}, has 'scenes' key: {'scenes' in adventure_data if isinstance(adventure_data, dict) else False}")
        if isinstance(adventure_data, dict) and "scenes" in adventure_data:
            logger.info(f"[NarrativeHandler] adventure_data tiene {len(adventure_data.get('scenes', []))} escenas")
    else:
        logger.warning(f"[NarrativeHandler] adventure_data es None. Estado completo: campaign_name={campaign_name}, current_scene_id={current_scene_id}, current_scene={current_scene}")
    
    # Si adventure_data es None pero hay campaign_name, intentar recargar INMEDIATAMENTE
    # IMPORTANTE: Siempre recargar si campaign_name existe y no es un valor por defecto
    default_campaigns = ["TheGeniesWishes", "The Genie's Wishes – Chapter 1: Cold Open"]
    if not adventure_data and campaign_name and campaign_name not in default_campaigns:
        logger.warning(f"[NarrativeHandler] adventure_data es None pero campaign_name='{campaign_name}'. Recargando aventura...")
        try:
            sd.load_campaign(campaign_name)
            # Actualizar variables después de recargar
            adventure_data = campaign_manager.state.get("adventure_data")
            current_scene_id = campaign_manager.state.get("current_scene_id")
            logger.info(f"[NarrativeHandler] Después de recargar - adventure_data: {adventure_data is not None}, current_scene_id: {current_scene_id}")
            # Si después de recargar todavía no hay adventure_data, es un error crítico
            if not adventure_data:
                logger.error(f"[NarrativeHandler] ERROR CRÍTICO: Después de recargar '{campaign_name}', adventure_data sigue siendo None!")
                # Intentar una vez más como último recurso
                logger.warning(f"[NarrativeHandler] Intentando recargar '{campaign_name}' una vez más como último recurso...")
                sd.load_campaign(campaign_name)
                adventure_data = campaign_manager.state.get("adventure_data")
                current_scene_id = campaign_manager.state.get("current_scene_id")
                logger.info(f"[NarrativeHandler] Después de segunda recarga - adventure_data: {adventure_data is not None}, current_scene_id: {current_scene_id}")
        except Exception as e:
            logger.error(f"[NarrativeHandler] Error al recargar aventura: {e}", exc_info=True)
    
    # Si hay adventure_data, mostrar la escena directamente
    if adventure_data and current_scene_id:
        try:
            from core.adventure.adventure_loader import AdventureLoader
            loader = AdventureLoader()
            
            # Verificar que adventure_data tiene la estructura correcta
            if not isinstance(adventure_data, dict) or "scenes" not in adventure_data:
                logger.warning(f"[NarrativeHandler] adventure_data no tiene estructura válida. Tipo: {type(adventure_data)}, keys: {list(adventure_data.keys()) if isinstance(adventure_data, dict) else 'N/A'}")
                # Intentar recargar
                if campaign_name and campaign_name != "TheGeniesWishes":
                    logger.info(f"[NarrativeHandler] Recargando aventura '{campaign_name}' debido a estructura inválida")
                    sd.load_campaign(campaign_name)
                    adventure_data = campaign_manager.state.get("adventure_data")
                    current_scene_id = campaign_manager.state.get("current_scene_id")
            
            scene = loader.find_scene_by_id(adventure_data, current_scene_id)
            if scene:
                narration = scene.get("narration", "")
                title = scene.get("title", "Escena")
                options_text = scene.get("options_text", [])
                options_list = ""
                if options_text:
                    options_list = "\n\n*Opciones disponibles:*\n" + "\n".join(f"• {opt}" for opt in options_text)
                result = f"🎭 *{title}*\n\n{narration}{options_list}"
                logger.info(f"[NarrativeHandler] Found adventure scene directly: {title} (ID: {current_scene_id})")
                await update.message.reply_text(result, parse_mode="Markdown")
                return
            else:
                logger.warning(f"[NarrativeHandler] No se encontró escena con ID '{current_scene_id}' en adventure_data. Escenas disponibles: {[s.get('scene_id') for s in adventure_data.get('scenes', [])]}")
        except Exception as e:
            logger.error(f"[NarrativeHandler] Error showing adventure scene directly: {e}", exc_info=True)
    
    # Si no hay adventure_data pero hay campaign_name, intentar recargar
    # Esta es una segunda oportunidad después del primer intento
    if not adventure_data and campaign_name and campaign_name != "TheGeniesWishes" and campaign_name != "The Genie's Wishes – Chapter 1: Cold Open":
        logger.warning(f"[NarrativeHandler] adventure_data es None (segunda verificación), recargando '{campaign_name}'")
        try:
            sd.load_campaign(campaign_name)
            # Intentar de nuevo
            adventure_data = campaign_manager.state.get("adventure_data")
            current_scene_id = campaign_manager.state.get("current_scene_id")
            logger.info(f"[NarrativeHandler] Después de segunda recarga - adventure_data: {adventure_data is not None}, current_scene_id: {current_scene_id}")
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
                    result = f"🎭 *{title}*\n\n{narration}{options_list}"
                    logger.info(f"[NarrativeHandler] Found adventure scene after reload: {title}")
                    await update.message.reply_text(result, parse_mode="Markdown")
                    return
            else:
                logger.error(f"[NarrativeHandler] ERROR: Después de segunda recarga, adventure_data o current_scene_id siguen siendo None")
        except Exception as e:
            logger.error(f"[NarrativeHandler] Error recargando aventura: {e}", exc_info=True)
    
    # Fallback: usar render_current_scene()
    logger.info("[NarrativeHandler] Calling render_current_scene()")
    result = sd.render_current_scene()
    
    logger.info(f"[NarrativeHandler] render_current_scene returned: {result[:150]}...")
    
    # Verificar que el resultado tenga narración válida (no solo título)
    # Si el resultado es solo título sin narración, intentar obtener la escena directamente
    if result and ("🎭 *Escena actual*" in result or "🎭 Escena actual:" in result or 
                   (result.count("\n") < 2 and "narration" not in result.lower())):
        logger.warning(f"[NarrativeHandler] render_current_scene devolvió resultado sin narración completa: '{result[:100]}...'")
        
        # Intentar obtener la escena directamente una última vez
        adventure_data = campaign_manager.state.get("adventure_data")
        current_scene_id = campaign_manager.state.get("current_scene_id")
        
        if adventure_data and current_scene_id:
            logger.info(f"[NarrativeHandler] Último intento: obtener escena directamente con ID '{current_scene_id}'")
            try:
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
                    result = f"🎭 *{title}*\n\n{narration}{options_list}"
                    logger.info(f"[NarrativeHandler] Escena encontrada en último intento: {title}")
                    await update.message.reply_text(result, parse_mode="Markdown")
                    return
            except Exception as e:
                logger.error(f"[NarrativeHandler] Error en último intento: {e}", exc_info=True)
        
        # Si todo falla, mostrar mensaje de error útil
        current_scene_name = campaign_manager.state.get("current_scene", "Escena actual")
        if current_scene_name and not current_scene_name.endswith(".json") and current_scene_name != "Escena actual":
            result = f"🎭 *{current_scene_name}*\n\n⚠️ No se pudo cargar la narración de la escena. Intenta ejecutar `/loadcampaign demo_mine_v1` nuevamente."
        else:
            result = "🎭 *Escena actual*\n\n⚠️ No se pudo cargar la escena de la aventura. Intenta ejecutar `/loadcampaign demo_mine_v1` nuevamente."
    
    await update.message.reply_text(result, parse_mode="Markdown")

async def event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    if not context.args:
        await update.message.reply_text(
            "Usa: `/event <tipo>` (ej: `/event combat_victory`)", parse_mode="Markdown"
        )
        return
    result = sd.trigger_event(context.args[0])
    await update.message.reply_text(result, parse_mode="Markdown")

def register_narrative_handlers(app):
    app.add_handler(CommandHandler("scene", scene))
    app.add_handler(CommandHandler("event", event))
