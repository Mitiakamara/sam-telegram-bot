import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=LOG_LEVEL,
)

logger = logging.getLogger(__name__)

# ================================================================
# 🧩 IMPORTS DEL SISTEMA SAM
# ================================================================
from core.scene_manager.scene_manager import SceneManager
from core.story_director.story_director import StoryDirector
from core.emotion.tone_adapter import ToneAdapter
from core.emotion.mood_manager import MoodManager
from core.action_handler.action_handler import ActionHandler
from core.renderer.renderer import Renderer
from core.emotion.emotional_feedback import EmotionalFeedbackLoop

# ================================================================
# 🧙‍♂️ INSTANCIAS CENTRALES DEL MOTOR NARRATIVO
# ================================================================

scene_manager = SceneManager()
story_director = StoryDirector()
tone_adapter = ToneAdapter()
mood_manager = MoodManager()
action_handler = ActionHandler()
renderer = Renderer()

# ================================================================
# 🧠 COMANDOS DEL BOT
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia una nueva sesión narrativa."""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 ¡Bienvenido, {user.first_name}! Soy S.A.M., tu Dungeon Master AI.\n"
        "Usa /newscene para iniciar la aventura o /help para ver comandos."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra los comandos disponibles."""
    await update.message.reply_text(
        "🎲 *Comandos disponibles:*\n"
        "/newscene – Inicia una nueva escena\n"
        "/end – Cierra la escena actual\n"
        "/summary – Muestra el estado emocional global\n"
        "/reset – Reinicia todo el historial\n"
        "/help – Muestra esta ayuda",
        parse_mode="Markdown"
    )


async def new_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea una nueva escena narrativa según el Story Director."""
    next_type = story_director.decide_next_scene_type()
    title = f"Escena {scene_manager.scene_counter + 1}: {next_type.title()}"
    description = f"El grupo se prepara para una nueva etapa de tipo '{next_type}'."

    scene = scene_manager.create_scene(title, description, scene_type=next_type)
    await update.message.reply_text(f"🎬 *{scene.title}* iniciada.\n\n{scene.description}", parse_mode="Markdown")


async def end_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finaliza la escena actual y procesa el ciclo emocional."""
    scene = scene_manager.get_current_scene()
    if not scene:
        await update.message.reply_text("⚠️ No hay ninguna escena activa para finalizar.")
        return

    # Registrar resultado y emociones
    story_director.evaluate_scene_outcome(player_success=0.7)  # aquí podrías basarlo en tiradas
    scene_manager.end_scene(tone_adapter, mood_manager, story_director, action_handler, renderer)

    # Procesar feedback loop emocional
    feedback = EmotionalFeedbackLoop(tone_adapter, mood_manager, story_director)
    result = feedback.process_feedback()

    # Mostrar resumen al usuario
    summary = result["summary"]
    await update.message.reply_text(
        f"📘 *Escena finalizada:* {scene.title}\n"
        f"🎭 Tono global: {result['tone_score']['label']}\n"
        f"📈 Tendencia: {result['trend']['direction']}\n"
        f"💫 Ajuste: {result['adjustment']['tone']}\n"
        f"🏷️ Próxima escena sugerida: {result['next_scene_type']}\n\n"
        f"_Total de escenas registradas: {summary['total_scenes']}_",
        parse_mode="Markdown",
    )


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra un resumen emocional global."""
    from core.emotion.emotional_tracker import get_emotional_summary
    summary = get_emotional_summary()
    await update.message.reply_text(
        f"📊 *Resumen emocional actual:*\n"
        f"- Total de escenas: {summary['total_scenes']}\n"
        f"- Emoción dominante: {summary['dominant_emotion']}\n"
        f"- Tono tendencia: {summary['tone_trend']}\n"
        f"- Balance emocional: {summary['emotion_balance']}",
        parse_mode="Markdown",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reinicia todo el sistema emocional."""
    from core.emotion.emotional_tracker import reset_history
    reset_history(confirm=True)
    scene_manager.reset_local_log()
    await update.message.reply_text("🧹 Historial de escenas y emociones reiniciado.")


# ================================================================
# 💬 MANEJO DE MENSAJES DE TEXTO (JUEGO EN CURSO)
# ================================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestiona mensajes del jugador durante la escena."""
    text = update.message.text.strip().lower()
    scene = scene_manager.get_current_scene()

    if not scene:
        await update.message.reply_text("❓ No hay una escena activa. Usa /newscene para comenzar.")
        return

    # Registrar acción del jugador
    action_handler.register_action(text)
    await update.message.reply_text(f"🗡️ Acción registrada: {text}")

    # (Opcional: respuesta narrativa dinámica)
    narrative = renderer.render_action(scene, text, mood_manager.current_tone)
    await update.message.reply_text(narrative)


# ================================================================
# 🚀 INICIALIZACIÓN DEL BOT
# ================================================================
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN no configurado en el entorno.")

    application = Application.builder().token(BOT_TOKEN).build()

    # Comandos principales
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("newscene", new_scene))
    application.add_handler(CommandHandler("end", end_scene))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("reset", reset))

    # Mensajes del jugador
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Ejecutar bot
    print("🤖 S.A.M. iniciado y listo para narrar aventuras...")
    application.run_polling()


# ================================================================
# 🧠 EJECUCIÓN DIRECTA
# ================================================================
if __name__ == "__main__":
    main()
