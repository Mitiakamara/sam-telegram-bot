from telegram import Update
from telegram.ext import ContextTypes
from core.scene_manager.scene_manager import SceneManager
from core.utils.logger import safe_logger
from core.utils.auth import is_admin
import os
import json

logger = safe_logger(__name__)
scene_manager = SceneManager()
SESSIONS_PATH = "core/data/sessions"


# ============================================================
# /join – une al jugador a una sesión persistente
# ============================================================
async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Permite que un jugador se una al grupo (party) de una sesión.
    Sintaxis:
      /join <session_id>
    Ejemplo:
      /join 87b1d2f9-93d1-4c3e-bb4a-68c41e07c2c5
    """
    try:
        args = context.args
        if len(args) == 0:
            await update.message.reply_text(
                "❗ Uso: `/join <session_id>` para unirte a una partida activa.",
                parse_mode="Markdown"
            )
            return

        session_id = args[0]
        session = scene_manager.load_session(session_id)

        if not session:
            await update.message.reply_text(
                f"⚠️ No se encontró la sesión `{session_id}`.",
                parse_mode="Markdown"
            )
            return

        user = update.effective_user
        user_name = user.first_name

        # Obtiene la lista actual de miembros
        party_state = session.get("party_state", {})
        members = party_state.get("members", [])

        # Verifica si el jugador ya pertenece
        if user_name in members:
            await update.message.reply_text(
                f"🧙‍♂️ {user_name}, ya formas parte de esta aventura. ¡No necesitas unirte de nuevo!"
            )
            return

        # Añade al jugador a la lista
        members.append(user_name)
        party_state["members"] = members
        session["party_state"] = party_state

        # Guarda el cambio
        scene_manager.save_progress(session)

        await update.message.reply_text(
            f"🎉 {user_name} se ha unido a la sesión `{session_id}`.\n"
            "Prepárate para la aventura... 🗺️",
            parse_mode="Markdown"
        )

        logger.info(f"{user_name} se unió al party de la sesión {session_id}")

    except Exception as e:
        logger.exception("Error en /join:")
        await update.message.reply_text(
            f"❌ Error al unirse a la sesión: {str(e)}", parse_mode="Markdown"
        )


# ============================================================
# /party – muestra los miembros actuales del grupo
# ============================================================
async def party_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra los jugadores registrados en una sesión.
    Sintaxis:
      /party <session_id>
    """
    try:
        if len(context.args) == 0:
            await update.message.reply_text(
                "❗ Uso: `/party <session_id>` para ver el grupo actual.",
                parse_mode="Markdown"
            )
            return

        session_id = context.args[0]
        session = scene_manager.load_session(session_id)

        if not session:
            await update.message.reply_text(
                f"⚠️ No se encontró la sesión `{session_id}`.",
                parse_mode="Markdown"
            )
            return

        members = session.get("party_state", {}).get("members", [])

        if not members:
            await update.message.reply_text("👥 Aún no hay aventureros en este grupo.")
            return

        members_text = "\n".join([f"• {m}" for m in members])
        await update.message.reply_text(
            f"🧭 *Miembros del grupo actual:*\n\n{members_text}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.exception("Error en /party:")
        await update.message.reply_text(
            f"❌ Error al mostrar el grupo: {str(e)}", parse_mode="Markdown"
        )
