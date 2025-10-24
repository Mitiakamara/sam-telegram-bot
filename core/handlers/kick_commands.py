from telegram import Update
from telegram.ext import ContextTypes
from core.scene_manager.scene_manager import SceneManager
from core.utils.logger import safe_logger
from core.utils.auth import check_admin

logger = safe_logger(__name__)
scene_manager = SceneManager()


# ============================================================
# /kick – expulsa a un jugador del grupo (solo admin)
# ============================================================
async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Expulsa a un jugador del grupo (party) de una sesión activa.
    Sintaxis:
      /kick <session_id> <nombre_jugador>
    Ejemplo:
      /kick 87b1d2f9-93d1-4c3e-bb4a-68c41e07c2c5 Valen
    """
    if not await check_admin(update):
        return

    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "❗ Uso: `/kick <session_id> <nombre_jugador>`",
                parse_mode="Markdown"
            )
            return

        session_id, player_name = args[0], " ".join(args[1:])
        session = scene_manager.load_session(session_id)

        if not session:
            await update.message.reply_text(
                f"⚠️ No se encontró la sesión `{session_id}`.",
                parse_mode="Markdown"
            )
            return

        # Obtiene los miembros actuales
        party_state = session.get("party_state", {})
        members = party_state.get("members", [])

        # Verifica si el jugador está en el grupo
        if player_name not in members:
            await update.message.reply_text(
                f"🤔 No encontré a *{player_name}* en el grupo de esta sesión.",
                parse_mode="Markdown"
            )
            return

        # Expulsa al jugador
        members.remove(player_name)
        party_state["members"] = members
        session["party_state"] = party_state

        # Guarda cambios
        scene_manager.save_progress(session)

        # Respuesta narrativa
        dramatic_lines = [
            f"💨 *S.A.M. pronuncia un conjuro de destierro...* {player_name} desaparece entre una nube de datos digitales.",
            f"⚡ Una energía arcana envuelve a *{player_name}*. Cuando el humo se disipa... ya no está.",
            f"📜 *S.A.M. tacha el nombre de {player_name} del pergamino del destino.*",
            f"🪄 'Adiós, {player_name}.' — susurra S.A.M. mientras un portal se cierra tras de ti."
        ]

        from random import choice
        await update.message.reply_text(choice(dramatic_lines), parse_mode="Markdown")

        logger.info(f"{player_name} fue expulsado del party en la sesión {session_id}")

    except Exception as e:
        logger.exception("Error en /kick:")
        await update.message.reply_text(
            f"❌ Error al expulsar jugador: {str(e)}", parse_mode="Markdown"
        )
