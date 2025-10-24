from telegram import Update
from telegram.ext import ContextTypes
from core.scene_manager.scene_manager import SceneManager
from core.utils.logger import safe_logger
from core.utils.auth import is_admin, check_admin
import random
import os

logger = safe_logger(__name__)
scene_manager = SceneManager()
SESSIONS_PATH = "core/data/sessions"


# ============================================================
# /action – ejecuta una acción dentro de la escena actual
# ============================================================
async def action_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ejecuta una acción jugable dentro de la escena actual.
    Sintaxis:
      /action <session_id> <action_name>
    Ejemplo:
      /action 87b1d2f9-... investigate
    """

    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "❗ Uso: `/action <session_id> <action_name>`",
                parse_mode="Markdown"
            )
            return

        session_id, action_name = args[0], args[1]
        session = scene_manager.load_session(session_id)

        if not session:
            await update.message.reply_text(
                f"⚠️ No se encontró la sesión `{session_id}`.",
                parse_mode="Markdown"
            )
            return

        # =======================================================
        # 🔐 CONTROL DE ACCESO POR PARTY
        # =======================================================
        user = update.effective_user
        user_id = user.id
        user_name = user.first_name

        party_members = session.get("party_state", {}).get("members", [])
        admin_access = is_admin(user_id)

        # Si no es admin ni miembro del party, se le bloquea
        if not admin_access and user_name not in party_members:
            funny_denied = [
                f"🪄 {user_name} intenta moverse, pero una barrera mágica lo detiene.",
                f"👀 S.A.M. levanta una ceja: 'Disculpa, {user_name}, pero no estás en esta partida.'",
                f"💢 El hechizo falla: solo los héroes del grupo pueden actuar aquí, {user_name}.",
                f"🎭 S.A.M. te observa y dice: 'No puedes tomar turnos en esta escena, viajero.'"
            ]
            from random import choice
            await update.message.reply_text(choice(funny_denied))
            return

        # =======================================================
        # ⚙️ ACCIÓN JUGABLE
        # =======================================================
        current_scene_id = session.get("current_scene_id", "")
        if not current_scene_id:
            await update.message.reply_text(
                "⚠️ La sesión no tiene una escena activa.",
                parse_mode="Markdown"
            )
            return

        scene = scene_manager.load_scene(current_scene_id)
        available_actions = [a.get("command") for a in scene.get("available_actions", [])]

        if not available_actions:
            await update.message.reply_text(
                "📜 Esta escena no tiene acciones configuradas.",
                parse_mode="Markdown"
            )
            return

        # Acción reconocida
        if f"/{action_name}" in available_actions:
            await update.message.reply_text(
                f"🎲 Ejecutando acción: `{action_name}`", parse_mode="Markdown"
            )

            # --- Simulación de éxito o fallo ---
            success = random.choice([True, False])

            if success:
                await update.message.reply_text("✅ Éxito en la acción.", parse_mode="Markdown")
                trigger = f"success_{action_name}"
            else:
                await update.message.reply_text("❌ Fallo en la acción.", parse_mode="Markdown")
                trigger = f"failure_{action_name}"

            # Evaluar transición
            next_scene = scene_manager.transition_scene(session, trigger)
            if next_scene:
                await update.message.reply_text(
                    f"➡️ Transición a la siguiente escena: `{next_scene}`", parse_mode="Markdown"
                )
                # Guardado automático
                scene_manager.autosave(session)
            else:
                scene_manager.autosave(session)
                await update.message.reply_text("💾 Progreso guardado automáticamente.", parse_mode="Markdown")

        else:
            await update.message.reply_text(
                f"⚠️ Acción `{action_name}` no disponible en esta escena.\n"
                f"Acciones válidas: {', '.join(available_actions)}",
                parse_mode="Markdown"
            )

    except Exception as e:
        logger.exception("Error en /action:")
        await update.message.reply_text(
            f"❌ Error al ejecutar acción: {str(e)}", parse_mode="Markdown"
        )
