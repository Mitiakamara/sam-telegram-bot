import logging
import inspect
from typing import Any

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logger = logging.getLogger("PlayerHandler")

# Estado del ConversationHandler para /createcharacter
CHARACTER_NAME = 1


# ---------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🧙‍♂️ Bienvenido a SAM The Dungeon Bot\n"
        "DM automático para campañas SRD 5.1.2.\n\n"
        "Comandos principales:\n"
        "• /createcharacter – crear tu personaje\n"
        "• /join – unirte a la campaña\n"
        "• /scene – mostrar o continuar la escena\n"
        "• /status – ver tu estado actual\n"
        "• /progress – ver progreso de la campaña\n\n"
        "Versión estable: 7.9 – Integración narrativa funcional"
    )
    await update.message.reply_text(text)


# ---------------------------------------------------------------------
# /createcharacter
# ---------------------------------------------------------------------
async def createcharacter_entry(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text("🧙‍♂️ Vamos a crear tu personaje.\n\n¿Cómo se llamará?")
    return CHARACTER_NAME


async def createcharacter_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    character_name = update.message.text.strip()
    user = update.effective_user
    context.user_data["character_name"] = character_name

    campaign_manager = context.application.bot_data.get("campaign_manager")

    if campaign_manager is not None:
        saved = False
        for method_name in (
            "add_or_update_player",
            "add_player",
            "register_player",
            "set_player_character",
        ):
            if hasattr(campaign_manager, method_name):
                method = getattr(campaign_manager, method_name)
                try:
                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    if params and params[0] == "self":
                        params = params[1:]

                    # Detectamos la firma y llamamos correctamente
                    if len(params) == 2:
                        # (user_id, character_name)
                        method(user.id, character_name)
                    elif len(params) == 3:
                        # (user_id, username, character_name)
                        method(user.id, user.username or user.full_name, character_name)
                    else:
                        # fallback genérico con kwargs
                        method(
                            user_id=user.id,
                            username=user.username or user.full_name,
                            character_name=character_name,
                        )
                    saved = True
                    break
                except Exception as e:
                    logger.warning(
                        "[PlayerHandler] No se pudo guardar personaje con %s: %s",
                        method_name,
                        e,
                    )

        if saved:
            await update.message.reply_text(
                f"✅ Personaje **{character_name}** creado y guardado en la campaña.",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(
                f"✅ Personaje **{character_name}** creado.\n"
                "⚠️ No pude guardarlo en la campaña porque el CampaignManager no tiene el método esperado.",
                parse_mode="Markdown",
            )
    else:
        await update.message.reply_text(
            f"✅ Personaje **{character_name}** creado (solo en esta sesión).",
            parse_mode="Markdown",
        )

    return ConversationHandler.END


async def createcharacter_cancel(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text("❌ Creación de personaje cancelada.")
    return ConversationHandler.END


# ---------------------------------------------------------------------
# /join
# ---------------------------------------------------------------------
async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    campaign_manager = context.application.bot_data.get("campaign_manager")

    if campaign_manager is None:
        await update.message.reply_text(
            "⚠️ No pude acceder al estado de la campaña. Intenta más tarde."
        )
        return

    joined = False
    error_msg = None
    char_name = context.user_data.get("character_name", "Sin nombre")

    for method_name in ("add_player", "join_player", "join", "add_or_update_player"):
        if hasattr(campaign_manager, method_name):
            method = getattr(campaign_manager, method_name)
            try:
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                if params and params[0] == "self":
                    params = params[1:]

                if len(params) == 2:
                    # (user_id, character_name)
                    method(user.id, char_name)
                elif len(params) == 3:
                    # (user_id, username, character_name)
                    method(user.id, user.username or user.full_name, char_name)
                else:
                    method(
                        user_id=user.id,
                        username=user.username or user.full_name,
                        character_name=char_name,
                    )
                joined = True
                break
            except Exception as e:
                error_msg = str(e)
                logger.warning("[PlayerHandler] No se pudo unir jugador: %s", e)

    if joined:
        await update.message.reply_text(f"✅ Te uniste a la campaña como **{char_name}**.")
    else:
        await update.message.reply_text(
            "⚠️ No pude unirte a la campaña. "
            f"{'Detalle: ' + error_msg if error_msg else ''}"
        )


# ---------------------------------------------------------------------
# /status
# ---------------------------------------------------------------------
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    campaign_manager = context.application.bot_data.get("campaign_manager")

    if campaign_manager is not None:
        player_info = None
        for method_name in ("get_player", "get_player_by_id", "fetch_player"):
            if hasattr(campaign_manager, method_name):
                try:
                    player_info = getattr(campaign_manager, method_name)(user.id)
                    break
                except Exception:
                    pass

        if player_info:
            char_name = player_info.get("character_name") or "Sin nombre"
            await update.message.reply_text(
                f"🧙‍♂️ Estado de {char_name}\n"
                f"Jugador: {user.username or user.full_name}\n"
                f"ID: {user.id}"
            )
            return

    # fallback
    character_name = context.user_data.get("character_name")
    if character_name:
        await update.message.reply_text(
            f"🧙‍♂️ Estado de {character_name}\n"
            f"Jugador: {user.username or user.full_name}\n"
            f"ID: {user.id}\n"
            "⚠️ (no se encontró en la campaña persistida)"
        )
    else:
        await update.message.reply_text("❌ No se encontró al jugador en la campaña.")


# ---------------------------------------------------------------------
# /progress
# ---------------------------------------------------------------------
async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    campaign_manager = context.application.bot_data.get("campaign_manager")
    if campaign_manager is None:
        await update.message.reply_text(
            "⚠️ Ocurrió un error al obtener el progreso de la campaña."
        )
        return

    campaign_name = getattr(campaign_manager, "campaign_name", "Desconocida")
    current_chapter = getattr(campaign_manager, "current_chapter", "Desconocido")
    current_scene = getattr(campaign_manager, "current_scene_title", "Desconocida")

    players_text = "Ninguno"
    for attr in ("players", "players_state", "registered_players"):
        if hasattr(campaign_manager, attr):
            players_val = getattr(campaign_manager, attr)
            if isinstance(players_val, dict):
                players_text = ", ".join(
                    p.get("character_name") or p.get("username") or str(pid)
                    for pid, p in players_val.items()
                ) or "Ninguno"
            elif isinstance(players_val, list):
                players_text = (
                    ", ".join(str(p) for p in players_val) if players_val else "Ninguno"
                )
            break

    await update.message.reply_text(
        "📖 Campaña: {c}\n"
        "🗺️ Capítulo: {ch}\n"
        "🎭 Escena actual: {s}\n"
        "👥 Jugadores: {p}".format(
            c=campaign_name, ch=current_chapter, s=current_scene, p=players_text
        )
    )


# ---------------------------------------------------------------------
# /scene
# ---------------------------------------------------------------------
async def scene_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    campaign_manager = context.application.bot_data.get("campaign_manager")
    if campaign_manager is None:
        await update.message.reply_text("⚠️ No pude mostrar la escena actual.")
        return

    scene_text = None
    for method_name in ("get_current_scene_text", "get_scene_text", "get_current_scene"):
        if hasattr(campaign_manager, method_name):
            try:
                scene_text = getattr(campaign_manager, method_name)()
                break
            except Exception:
                pass

    if scene_text:
        await update.message.reply_text(scene_text)
    else:
        title = getattr(campaign_manager, "current_scene_title", "Escena desconocida")
        await update.message.reply_text(
            f"📜 {title}\n\nEl sol del desierto cae sin piedad. "
            "Ustedes han llegado a un oasis medio abandonado..."
        )


# ---------------------------------------------------------------------
# REGISTRO DE HANDLERS
# ---------------------------------------------------------------------
def register_player_handlers(application: Application, campaign_manager: Any) -> None:
    """Registra todos los comandos y guarda el CampaignManager para los handlers."""
    application.bot_data["campaign_manager"] = campaign_manager

    # /start
    application.add_handler(CommandHandler("start", start_command))

    # /createcharacter
    createcharacter_conv = ConversationHandler(
        entry_points=[CommandHandler("createcharacter", createcharacter_entry)],
        states={
            CHARACTER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, createcharacter_name)
            ]
        },
        fallbacks=[CommandHandler("cancel", createcharacter_cancel)],
    )
    application.add_handler(createcharacter_conv)

    # /join
    application.add_handler(CommandHandler("join", join_command))

    # /status
    application.add_handler(CommandHandler("status", status_command))

    # /progress
    application.add_handler(CommandHandler("progress", progress_command))

    # /scene
    application.add_handler(CommandHandler("scene", scene_command))

    logger.info(
        "[PlayerHandler] Comandos /start, /createcharacter, /join, /status, /progress y /scene registrados."
    )
