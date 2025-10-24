import os
from telegram import Update
from telegram.ext import ContextTypes
from core.utils.logger import safe_logger

logger = safe_logger(__name__)

SESSIONS_PATH = "core/data/sessions"


# ============================================================
# /deletesession – elimina una o todas las sesiones
# ============================================================
async def delete_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Borra una sesión específica o todas las sesiones guardadas.

    Uso:
      /deletesession <session_id>     → elimina una sesión concreta
      /deletesession all              → elimina todas las sesiones
    """
    try:
        if not os.path.exists(SESSIONS_PATH):
            await update.message.reply_text("⚠️ No se encontró el directorio de sesiones.")
            return

        # No se pasó argumento
        if len(context.args) == 0:
            await update.message.reply_text(
                "❗ Uso: `/deletesession <session_id>` o `/deletesession all`",
                parse_mode="Markdown"
            )
            return

        target = context.args[0].strip().lower()

        # 🧹 Borrar todas las sesiones
        if target == "all":
            count = 0
            for f in os.listdir(SESSIONS_PATH):
                if f.startswith("session_") or f.startswith("autosave_"):
                    os.remove(os.path.join(SESSIONS_PATH, f))
                    count += 1
            await update.message.reply_text(f"🗑️ Todas las sesiones eliminadas ({count} archivos).")
            logger.info(f"Eliminadas {count} sesiones en {SESSIONS_PATH}")
            return

        # 🗂️ Borrar una sesión específica
        session_file = os.path.join(SESSIONS_PATH, f"session_{target}.json")
        autosave_file = os.path.join(SESSIONS_PATH, f"autosave_{target}.json")

        deleted = False
        for path in [session_file, autosave_file]:
            if os.path.exists(path):
                os.remove(path)
                deleted = True
                logger.info(f"Eliminada sesión: {path}")

        if deleted:
            await update.message.reply_text(f"🗑️ Sesión `{target}` eliminada correctamente.", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"⚠️ No se encontró ninguna sesión con ID `{target}`.", parse_mode="Markdown")

    except Exception as e:
        logger.exception("Error en /deletesession:")
        await update.message.reply_text(f"❌ Error al eliminar sesiones: {str(e)}", parse_mode="Markdown")
