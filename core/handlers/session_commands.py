from telegram import Update
from telegram.ext import ContextTypes
from core.scene_manager.scene_manager import SceneManager
from core.utils.logger import safe_logger

logger = safe_logger(__name__)
scene_manager = SceneManager()


# ============================================================
# /newsession – crea una nueva sesión de campaña
# ============================================================
async def new_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Crea una nueva sesión de campaña en el sistema de persistencia.

    Uso:
      /newsession <campaign_id> <party_id> [dm_mode]
    Ejemplo:
      /newsession demo_campaign party_001 auto
    """
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "❗ Uso: `/newsession <campaign_id> <party_id> [dm_mode]`\n"
                "Ejemplo: `/newsession demo_campaign party_001 auto`",
                parse_mode="Markdown"
            )
            return

        campaign_id = args[0]
        party_id = args[1]
        dm_mode = args[2] if len(args) > 2 else "auto"

        session = scene_manager.create_session(campaign_id, party_id, dm_mode)
        session_id = session.get("session_id", "undefined")

        await update.message.reply_text(
            f"🆕 *Nueva sesión creada*\n\n"
            f"🎯 Campaña: `{campaign_id}`\n"
            f"👥 Party: `{party_id}`\n"
            f"🧠 Modo DM: `{dm_mode}`\n"
            f"💾 ID de sesión: `{session_id}`\n\n"
            f"Usa `/save {session_id}` o `/action {session_id} <acción>` para continuar.",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.exception("Error en /newsession:")
        await update.message.reply_text(
            f"❌ Error al crear nueva sesión: {str(e)}", parse_mode="Markdown"
        )


# ============================================================
# /sessions – lista las sesiones guardadas
# ============================================================
async def list_sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Lista todas las sesiones guardadas en /data/sessions/
    """
    try:
        import os

        sessions_dir = "core/data/sessions"
        if not os.path.exists(sessions_dir):
            await update.message.reply_text("⚠️ No hay sesiones guardadas todavía.")
            return

        files = [f for f in os.listdir(sessions_dir) if f.startswith("session_") and f.endswith(".json")]
        if not files:
            await update.message.reply_text("📭 No se encontraron sesiones guardadas.")
            return

        text = "📜 *Sesiones guardadas:*\n\n"
        for f in files:
            text += f"• `{f.replace('session_', '').replace('.json', '')}`\n"

        await update.message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        logger.exception("Error en /sessions:")
        await update.message.reply_text(
            f"❌ Error al listar sesiones: {str(e)}", parse_mode="Markdown"
        )
