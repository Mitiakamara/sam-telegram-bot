# ================================================================
# 🤖 SAM The Dungeon Bot – main.py
# Versión: 7.6.1 (SRD 5.1.2)
# Rol: Punto de entrada del bot de Telegram
# Objetivo:
#   - Actuar como DM para campañas SRD 5.1.2 precreadas
#   - Mantener coherencia narrativa entre escenas
#   - Permitir crear PJ desde el chat
#   - Permitir cambiar/cargar campañas
# ================================================================

import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ----------------------------------------------------------------
# 🔧 Logging básico
# ----------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------
# 📦 Core imports
# ----------------------------------------------------------------
try:
    # tu paquete real
    from core.story_director import StoryDirector
except ImportError as e:
    # Si esto falla, no tiene sentido seguir
    logger.error("No se pudo importar StoryDirector desde core.story_director: %s", e)
    raise

# ----------------------------------------------------------------
# 🧠 Instancia única del director de historia
# ----------------------------------------------------------------
story_director = StoryDirector()

# Si quieres restringir /loadcampaign a tu user_id de Telegram, ponlo aquí
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")


# ================================================================
# 🧵 HANDLERS DE COMANDOS
# ================================================================

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mensaje de bienvenida + recordatorio de comandos básicos.
    """
    text = (
        "🧙‍♂️ *Bienvenido a SAM The Dungeon Bot*\n"
        "DM automático para campañas SRD 5.1.2.\n\n"
        "Comandos útiles:\n"
        "• /createcharacter – crear tu PJ aquí mismo\n"
        "• /join – unirte a la campaña activa\n"
        "• /scene – mostrar/continuar la escena actual\n"
        "• /event <tipo> – forzar un evento narrativo (p.ej. `combat_victory`)\n"
        "• /status – ver tu estado dentro de la campaña\n"
        "• /progress – ver estado de la campaña\n"
        "• /restart – reiniciar la campaña actual\n"
        "• /loadcampaign <slug> – (admin) cargar otra campaña\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def createcharacter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Crea un PJ directamente desde el chat.
    Formatos aceptados:
      /createcharacter
      /createcharacter Nombre
      /createcharacter Nombre Clase Raza
    """
    user = update.effective_user
    args = context.args

    # valores por defecto muy SRD
    name = None
    char_class = "Fighter"
    race = "Human"

    if len(args) >= 1:
        name = args[0]
    if len(args) >= 2:
        char_class = args[1]
    if len(args) >= 3:
        race = args[2]

    if not name:
        await update.message.reply_text(
            "📜 Usa: `/createcharacter Nombre [Clase] [Raza]`\n"
            "Ejemplo: `/createcharacter Asterix Fighter Human`",
            parse_mode="Markdown",
        )
        return

    try:
        character_data = story_director.create_character(
            telegram_id=user.id,
            username=user.username or user.full_name,
            name=name,
            char_class=char_class,
            race=race,
        )
        await update.message.reply_text(
            f"✅ PJ creado: *{character_data.get('name', name)}* "
            f"({character_data.get('class', char_class)} {character_data.get('race', race)})",
            parse_mode="Markdown",
        )
    except AttributeError:
        # por si aún no implementaste create_character en StoryDirector
        await update.message.reply_text(
            "⚠️ La creación de personajes aún no está implementada en el director de historia."
        )


async def join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Une al jugador a la campaña activa.
    """
    user = update.effective_user
    try:
        result = story_director.join_player(
            telegram_id=user.id,
            username=user.username or user.full_name,
        )
        msg = result.get("message", "✅ Te uniste a la campaña actual.")
        await update.message.reply_text(msg)
    except AttributeError:
        await update.message.reply_text(
            "⚠️ El sistema de campañas no expone aún `join_player(...)` en StoryDirector."
        )


async def scene_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra o renderiza la escena actual.
    """
    try:
        rendered = story_director.render_current_scene()
        await update.message.reply_text(rendered, parse_mode="Markdown")
    except AttributeError:
        await update.message.reply_text("⚠️ No se pudo renderizar la escena actual.")


async def event_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fuerza un evento narrativo, que el TransitionEngine usará
    para decidir la próxima escena.
    Ejemplo: /event combat_victory
    """
    if not context.args:
        await update.message.reply_text(
            "Usa: `/event <tipo>`\nEj: `/event combat_victory` o `/event setback`",
            parse_mode="Markdown",
        )
        return

    event_type = context.args[0]
    try:
        rendered = story_director.trigger_event(event_type)
        await update.message.reply_text(rendered, parse_mode="Markdown")
    except AttributeError:
        await update.message.reply_text(
            f"⚠️ El director aún no implementa eventos. Recibí: `{event_type}`.",
            parse_mode="Markdown",
        )


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el estado del jugador (emocional, escena, etc.).
    """
    user = update.effective_user
    try:
        status = story_director.get_player_status(user.id)
        await update.message.reply_text(status, parse_mode="Markdown")
    except AttributeError:
        await update.message.reply_text("⚠️ El director no expone aún get_player_status().")


async def progress_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el progreso de la campaña actual (lo que ya te estaba
    sacando bien en /progress según tus logs).
    """
    try:
        progress = story_director.get_campaign_progress()
        await update.message.reply_text(progress, parse_mode="Markdown")
    except AttributeError:
        await update.message.reply_text("⚠️ No se pudo obtener el progreso de campaña.")


async def restart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Reinicia la campaña actual al capítulo 1/escena inicial.
    Útil si se corrompe el estado.
    """
    try:
        story_director.restart_campaign()
        await update.message.reply_text("🔄 Campaña reiniciada desde el inicio.")
    except AttributeError:
        await update.message.reply_text("⚠️ El director no expone aún restart_campaign().")


async def loadcampaign_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Carga otra campaña precreada.
    Pensado para que tú (admin) puedas ir cambiando de carpeta/campaign.json.
    Uso:
      /loadcampaign TheGeniesWishes
      /loadcampaign CurseOfTheDesert
    """
    user = update.effective_user
    if ADMIN_TELEGRAM_ID and str(user.id) != str(ADMIN_TELEGRAM_ID):
        await update.message.reply_text("🚫 No tienes permiso para cargar campañas.")
        return

    if not context.args:
        await update.message.reply_text("Usa: `/loadcampaign <slug>`", parse_mode="Markdown")
        return

    campaign_slug = context.args[0]
    try:
        story_director.load_campaign(campaign_slug)
        await update.message.reply_text(f"📦 Campaña cargada: *{campaign_slug}*", parse_mode="Markdown")
    except AttributeError:
        await update.message.reply_text(
            "⚠️ El director no expone aún load_campaign(slug). "
            "Asegúrate de tenerlo en core/story_director.",
        )
    except FileNotFoundError:
        await update.message.reply_text(f"⚠️ No encontré la campaña `{campaign_slug}`.")


# ================================================================
# 🚀 MAIN
# ================================================================
def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN no está definido en el entorno.")

    app = ApplicationBuilder().token(token).build()

    # Registro de comandos oficiales
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("createcharacter", createcharacter_handler))
    app.add_handler(CommandHandler("join", join_handler))
    app.add_handler(CommandHandler("scene", scene_handler))
    app.add_handler(CommandHandler("event", event_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("progress", progress_handler))
    app.add_handler(CommandHandler("restart", restart_handler))
    app.add_handler(CommandHandler("loadcampaign", loadcampaign_handler))

    logger.info("Bot listo. Esperando comandos...")
    app.run_polling()


if __name__ == "__main__":
    main()
