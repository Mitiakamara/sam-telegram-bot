import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from core.utils.logger import safe_logger
from core.utils.auth import is_admin

logger = safe_logger(__name__)
SESSIONS_PATH = "core/data/sessions"


# ============================================================
# /deletesession – requiere permiso de administrador
# ============================================================
async def delete_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ No tienes permiso para ejecutar este comando.")
        return

    try:
        if len(context.args) == 0:
            await update.message.reply_text(
                "❗ Uso: `/deletesession <session_id>` o `/deletesession all`",
                parse_mode="Markdown"
            )
            return

        target = context.args[0].strip().lower()
        context.user_data["delete_target"] = target

        if target == "all":
            text = (
                "⚠️ *Confirmación requerida*\n\n"
                "¿Seguro que deseas eliminar **todas las sesiones guardadas**?\n"
                "Esta acción *no se puede deshacer*."
            )
        else:
            text = (
                f"⚠️ *Confirmación requerida*\n\n"
                f"¿Seguro que deseas eliminar la sesión `{target}`?\n"
                "Esta acción *no se puede deshacer*."
            )

        buttons = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_delete_{target}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_delete")
            ]
        ]
        markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

    except Exception as e:
        logger.exception("Error en /deletesession (fase de confirmación):")
        await update.message.reply_text(f"❌ Error al solicitar confirmación: {str(e)}", parse_mode="Markdown")


# ============================================================
# 🔘 Callback: confirmación o cancelación
# ============================================================
async def handle_delete_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.edit_message_text("⛔ No tienes permiso para realizar esta acción.")
        return

    target = data.replace("confirm_delete_", "", 1) if data.startswith("confirm_delete_") else None

    try:
        if data == "cancel_delete":
            await query.edit_message_text("❎ Eliminación cancelada. No se borró ninguna sesión.")
            return

        if not os.path.exists(SESSIONS_PATH):
            await query.edit_message_text("⚠️ No se encontró el directorio de sesiones.")
            return

        # 🧹 Eliminar todas las sesiones
        if target == "all":
            count = 0
            for f in os.listdir(SESSIONS_PATH):
                if f.startswith("session_") or f.startswith("autosave_"):
                    os.remove(os.path.join(SESSIONS_PATH, f))
                    count += 1
            await query.edit_message_text(f"🗑️ Todas las sesiones eliminadas ({count} archivos).")
            logger.info(f"Eliminadas {count} sesiones.")
            return

        # 🗂️ Eliminar una sesión específica
        session_file = os.path.join(SESSIONS_PATH, f"session_{target}.json")
        autosave_file = os.path.join(SESSIONS_PATH, f"autosave_{target}.json")

        deleted = False
        for path in [session_file, autosave_file]:
            if os.path.exists(path):
                os.remove(path)
                deleted = True
                logger.info(f"Eliminada sesión: {path}")

        if deleted:
            await query.edit_message_text(f"🗑️ Sesión `{target}` eliminada correctamente.", parse_mode="Markdown")
        else:
            await query.edit_message_text(f"⚠️ No se encontró ninguna sesión con ID `{target}`.", parse_mode="Markdown")

    except Exception as e:
        logger.exception("Error en confirmación de borrado:")
        await query.edit_message_text(f"❌ Error al eliminar sesiones: {str(e)}", parse_mode="Markdown")
