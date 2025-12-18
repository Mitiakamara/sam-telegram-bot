# ================================================================
# 🎯 CAMPAIGN HANDLER
# ================================================================
# Controla los comandos relacionados con la campaña:
#   /progress – muestra el estado actual de la campaña
#   /restart  – reinicia la campaña desde el inicio
#   /loadcampaign <slug> – cambia de campaña
# ================================================================

import logging
from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    summary = sd.get_campaign_progress()
    await update.message.reply_text(summary, parse_mode="Markdown")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    sd.restart_campaign()
    await update.message.reply_text("🔄 Campaña reiniciada desde el inicio.")

async def loadcampaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sd = context.bot_data.get("story_director")
    if not sd:
        await update.message.reply_text("⚠️ StoryDirector no disponible.")
        return
    
    if not context.args:
        # Listar aventuras disponibles
        from core.adventure.adventure_loader import AdventureLoader
        loader = AdventureLoader()
        available = loader.list_available_adventures()
        if available:
            await update.message.reply_text(
                f"📚 Aventuras disponibles:\n" + "\n".join(f"• {a}" for a in available) +
                f"\n\nUsa: `/loadcampaign <nombre>`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "⚠️ No hay aventuras disponibles.\n"
                "Coloca archivos JSON en la carpeta `adventures/`",
                parse_mode="Markdown"
            )
        return

    slug = context.args[0]
    try:
        logger.info(f"[CampaignHandler] Cargando campaña '{slug}'...")
        sd.load_campaign(slug)
        
        # IMPORTANTE: Guardar el slug en bot_data para recargar si es necesario
        context.bot_data["last_loaded_campaign"] = slug
        logger.info(f"[CampaignHandler] Slug guardado en bot_data")
        
        # Verificar que adventure_data se guardó correctamente
        adventure_data = sd.campaign_manager.state.get("adventure_data")
        current_scene_id = sd.campaign_manager.state.get("current_scene_id")
        adventure_title = sd.campaign_manager.state.get("campaign_title", slug)
        total_scenes = len(sd.campaign_manager.state.get("adventure_scenes", []))
        
        logger.info(f"[CampaignHandler] Después de load_campaign - adventure_data presente: {adventure_data is not None}, current_scene_id: {current_scene_id}, total_scenes: {total_scenes}")
        
        if not adventure_data:
            logger.error(f"[CampaignHandler] ERROR: adventure_data NO está presente después de load_campaign!")
            await update.message.reply_text(
                f"⚠️ Error: La aventura se cargó pero adventure_data no se guardó correctamente.\n"
                f"Intenta ejecutar `/loadcampaign {slug}` nuevamente.",
                parse_mode="Markdown"
            )
            return
        
        await update.message.reply_text(
            f"📦 *Campaña cargada*\n\n"
            f"🎭 {adventure_title}\n"
            f"📊 {total_scenes} escenas disponibles\n"
            f"📍 Escena inicial: {sd.campaign_manager.get_current_scene()}\n\n"
            f"Usa `/scene` para comenzar la aventura.",
            parse_mode="Markdown"
        )
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {str(e)}")
    except Exception as e:
        logger.exception(f"Error cargando campaña: {e}")
        await update.message.reply_text(f"⚠️ Error al cargar campaña: {e}")

def register_campaign_handlers(app):
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("loadcampaign", loadcampaign))
