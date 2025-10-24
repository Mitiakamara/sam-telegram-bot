import json
from telegram import Update
from telegram.ext import ContextTypes

from core.scene_manager.scene_manager import SceneManager
from core.utils.logger import safe_logger

logger = safe_logger(__name__)

# Inicializa el manejador global del SceneManager
scene_manager = SceneManager()


# ============================================================
# /save – guarda el progreso actual de la sesión
# ============================================================
async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) == 0:
            await update.message.reply_text("❗ Debes indicar el ID de sesión. Ejemplo: `/save <session_id>`", parse_mode="Markdown")
            return

        session_id = context.args[0]
        session = scene_manager.load_session(session_id)

        if not session:
            await update.message.reply_text(f"⚠️ No se encontró la sesión `{session_id}`", parse_mode="Markdown")
            return

        scene_manager.save_progress(session)
        await update.message.reply_text(f"✅ Progreso de la sesión `{session_id}` guardado correctamente.", parse_mode="Markdown")

    except Exception as e:
        logger.exception("Error en /save:")
        await update.message.reply_text(f"❌ Error al guardar sesión: {str(e)}", parse_mode="Markdown")


# ============================================================
# /load – carga una sesión guardada
# ============================================================
async def load_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) == 0:
            await update.message.reply_text("❗ Debes indicar el ID de sesión. Ejemplo: `/load <session_id>`", parse_mode="Markdown")
            return

        session_id = context.args[0]
        session = scene_manager.load_session(session_id)

        if not session:
            await update.message.reply_text(f"⚠️ No se encontró la sesión `{session_id}`", parse_mode="Markdown")
            return

        text = f"🎮 Sesión `{session_id}` cargada.\n\nEscena actual: `{session.get('current_scene_id', 'N/A')}`"
        await update.message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        logger.exception("Error en /load:")
        await update.message.reply_text(f"❌ Error al cargar sesión: {str(e)}", parse_mode="Markdown")


# ============================================================
# /scene – muestra información de la escena actual
# ============================================================
async def scene_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) == 0:
            await update.message.reply_text("❗ Usa `/scene <scene_id>` para ver detalles.", parse_mode="Markdown")
            return

        scene_id = context.args[0]
        scene = scene_manager.load_scene(scene_id)

        if not scene:
            await update.message.reply_text(f"⚠️ No se encontró la escena `{scene_id}`", parse_mode="Markdown")
            return

        # Construir una vista resumida de la escena
        summary = f"🎭 *{scene.get('title', 'Sin título')}*\n"
        summary += f"\n{scene.get('description', 'Sin descripción disponible.')}\n"
        summary += f"\n🌍 Tipo: `{scene.get('scene_type', 'N/A')}` | Estado: `{scene.get('status', 'N/A')}`"
        summary += f"\n🎯 Objetivos: {len(scene.get('objectives', []))}"
        summary += f"\n🎲 Acciones disponibles: {len(scene.get('available_actions', []))}"

        await update.message.reply_text(summary, parse_mode="Markdown")

    except Exception as e:
        logger.exception("Error en /scene:")
        await update.message.reply_text(f"❌ Error al mostrar escena: {str(e)}", parse_mode="Markdown")
