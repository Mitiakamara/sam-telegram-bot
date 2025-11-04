import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from dotenv import load_dotenv

# ============================================================
# 🧩 IMPORTACIONES DEL MOTOR NARRATIVO SAM
# ============================================================
from core.story_director import StoryDirector

# ============================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ============================================================
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "REEMPLAZAR_CON_TOKEN")
APP_NAME = "SamTheDungeonBot"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ============================================================
# 🎭 INSTANCIA GLOBAL DEL DIRECTOR NARRATIVO
# ============================================================
story_director = StoryDirector()

# ============================================================
# 🧙‍♂️ COMANDOS DE JUEGO
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de bienvenida e inicio."""
    await update.message.reply_text(
        "👋 ¡Bienvenido a *SAM*, tu Dungeon Master AI!\n\n"
        "Usa /createcharacter para crear tu personaje o /join para unirte a la campaña.",
        parse_mode="Markdown"
    )


async def create_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simula la creación de personaje y genera perfil narrativo."""
    user = update.effective_user

    # Atributos de ejemplo — normalmente provienen del builder o parser de hoja
    example_attributes = {
        "strength": 15,
        "dexterity": 12,
        "constitution": 13,
        "intelligence": 10,
        "wisdom": 14,
        "charisma": 8
    }

    # Simulación de grupo con un solo jugador
    story_director.initialize_session([example_attributes], [user.first_name])

    await update.message.reply_text(
        f"🧙‍♂️ Has creado tu personaje, *{user.first_name}*.\n"
        "Se ha generado tu perfil narrativo y se ha inicializado la campaña.\n"
        f"`{story_director.get_current_profile()}`",
        parse_mode="Markdown"
    )


async def start_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia una escena narrativa adaptada."""
    scene = story_director.start_scene("progress_scene.json")
    await update.message.reply_text(scene["description_adapted"])


async def event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ejecuta un evento narrativo (p. ej., combate o descubrimiento)."""
    args = context.args
    if not args:
        await update.message.reply_text("Usa /event <tipo> — ejemplos: combat_victory, setback, rally, calm")
        return

    event_type = args[0]
    story_director.handle_event(event_type)
    await update.message.reply_text(story_director.summarize_scene())


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el estado actual del grupo y la emoción narrativa."""
    profile = story_director.get_current_profile()
    summary = story_director.summarize_scene()
    await update.message.reply_text(
        f"🎭 *Perfil del grupo:* `{profile}`\n\n"
        f"📖 *Escena actual:*\n{summary}",
        parse_mode="Markdown"
    )


async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el estado actual de la campaña."""
    summary = story_director.get_campaign_summary()
    await update.message.reply_text(summary, parse_mode="Markdown")


# ============================================================
# 🚀 CONFIGURACIÓN DEL BOT
# ============================================================
def main():
    logging.info("Iniciando aplicación de Telegram SAM...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Comandos principales
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("createcharacter", create_character))
    app.add_handler(CommandHandler("scene", start_scene))
    app.add_handler(CommandHandler("event", event))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("progress", progress))

    logging.info("Bot listo. Esperando comandos...")
    app.run_polling()


# ============================================================
# PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    main()
