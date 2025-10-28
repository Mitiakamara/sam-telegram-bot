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
# 🧩 IMPORTS DEL SISTEMA S.A.M. (hasta Fase 6.30)
# ================================================================
from core.scene_manager.scene_manager import SceneManager
from core.story_director.story_director import StoryDirector
from core.story_director.narrative_persistence import NarrativePersistence
from core.emotion.tone_adapter import ToneAdapter
from core.mood_manager.mood_manager import MoodManager
from core.action_handler.action_handler import ActionHandler
from core.renderer import Renderer
from core.emotion.emotional_feedback import EmotionalFeedbackLoop
from core.emotion.player_resonance import PlayerResonance
from core.emotion.group_resonance import GroupResonance
from core.emotion.collective_memory import CollectiveEmotionalMemory
from core.emotion.worldstate_projection import EmotionalWorldstateProjection
from core.encounters.adaptive_encounter import AdaptiveEncounterDesigner
from core.emotion.emotional_reinforcement import EmotionalReinforcementLoop
from core.analytics.emotion_dashboard import EmotionDashboard
from core.reports.narrative_report import NarrativeReport

# ================================================================
# 🧙‍♂️ INSTANCIAS CENTRALES
# ================================================================
scene_manager = SceneManager()
story_director = StoryDirector()
tone_adapter = ToneAdapter()
mood_manager = MoodManager()
action_handler = ActionHandler()
renderer = Renderer()

# Módulos emocionales y analíticos
player_resonance = PlayerResonance()
group_resonance = GroupResonance()
collective_memory = CollectiveEmotionalMemory()
world_projection = EmotionalWorldstateProjection()
encounter_designer = AdaptiveEncounterDesigner(mood_manager)
reinforcement_loop = EmotionalReinforcementLoop()

# ================================================================
# 🧠 COMANDOS PRINCIPALES
# ================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bienvenida inicial."""
    await update.message.reply_text(
        "🎲 *Bienvenido a S.A.M. – Storytelling AI Dungeon Master.*\n"
        "Usa /newscene para iniciar una nueva escena o /resume para continuar tu campaña.",
        parse_mode="Markdown",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Comandos disponibles:*\n"
        "/newscene – Inicia una nueva escena\n"
        "/end – Finaliza la escena actual\n"
        "/nextencounter – Genera un encuentro adaptativo\n"
        "/summary – Muestra el estado emocional\n"
        "/dashboard – Muestra panel emocional\n"
        "/exportreport – Exporta informe narrativo\n"
        "/savesession – Guarda estado actual\n"
        "/resume – Reanuda la campaña\n"
        "/reset – Reinicia datos emocionales\n"
        "/help – Muestra esta ayuda",
        parse_mode="Markdown",
    )

# ================================================================
# 🎬 ESCENAS Y ENCUENTROS
# ================================================================
async def new_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia una nueva escena."""
    next_type = story_director.decide_next_scene_type()
    scene = scene_manager.create_scene(
        f"Escena {scene_manager.scene_counter + 1}: {next_type.title()}",
        f"El grupo entra en una nueva etapa de tipo '{next_type}'.",
        scene_type=next_type,
    )
    narrative = renderer.render_scene(scene, mood_manager.current_tone, mood_manager)
    await update.message.reply_text(f"🎬 *{scene.title}*\n{narrative}", parse_mode="Markdown")

async def next_encounter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera un encuentro adaptativo."""
    encounter = encounter_designer.generate_encounter(group_resonance.compute_cohesion())
    await update.message.reply_text(
        f"⚔️ *Nuevo encuentro:*\n"
        f"- Tipo: {encounter['type']}\n"
        f"- Tono: {encounter['tone']}\n"
        f"- Dificultad: {encounter['difficulty']}\n"
        f"- Proyección: {encounter['projection']}\n\n"
        f"{encounter['description']}",
        parse_mode="Markdown",
    )

# ================================================================
# 🧩 CIERRE DE ESCENA Y CICLO EMOCIONAL
# ================================================================
async def end_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finaliza escena, procesa emociones y refuerza narrativa."""
    scene = scene_manager.get_current_scene()
    if not scene:
        await update.message.reply_text("⚠️ No hay una escena activa.")
        return

    # Cerrar y analizar
    story_director.evaluate_scene_outcome(player_success=0.7)
    scene_manager.end_scene(tone_adapter, mood_manager, story_director, action_handler, renderer)

    # Procesar Feedback Loop
    feedback = EmotionalFeedbackLoop(tone_adapter, mood_manager, story_director)
    result = feedback.process_feedback()

    # Aplicar blend
    blend = result["adjustment"].get("blend")
    mood_manager.set_tone(mood_manager.current_tone, blend)

    # Registrar en memorias
    group_result = group_resonance.compute_cohesion()
    collective_memory.record_group_state(group_result)
    world_projection.project_future_state()
    reinforcement_loop.apply_reinforcement_to_director(story_director)

    await update.message.reply_text(
        f"📘 *Escena finalizada:* {scene.title}\n"
        f"🎭 Tono: {result['tone_score']['label']}  |  Matiz: {blend['label'] if blend else '—'}\n"
        f"📈 Tendencia: {result['trend']['direction']}  |  Próxima escena: {result['next_scene_type']}\n",
        parse_mode="Markdown",
    )

# ================================================================
# 💬 INTERACCIÓN DEL JUGADOR
# ================================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    player_name = update.effective_user.first_name or "Jugador"
    scene = scene_manager.get_current_scene()
    if not scene:
        await update.message.reply_text("❓ No hay una escena activa. Usa /newscene.")
        return

    # Analizar emoción individual y grupal
    emotion, strength = player_resonance.analyze_message(text)
    player_resonance.apply_to_mood(mood_manager)
    group_resonance.record_player_emotion(player_name, emotion, strength)
    group_result = group_resonance.compute_cohesion()
    group_resonance.apply_to_mood(mood_manager, group_result)

    # Registrar acción y responder
    action_handler.register_action(text)
    narrative = renderer.render_action(scene, text, mood_manager.current_tone, mood_manager)
    await update.message.reply_text(
        f"🧠 *Emoción de {player_name}:* {emotion} ({strength:.2f})\n"
        f"🎭 *Tono global:* {mood_manager.current_tone}\n\n{narrative}",
        parse_mode="Markdown",
    )

# ================================================================
# 🔮 DASHBOARD Y REPORTES
# ================================================================
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from core.emotion.emotional_tracker import get_emotional_summary
    summary = get_emotional_summary()
    mood_state = mood_manager.get_state()
    blend = mood_state.get("blend")
    blend_text = f"\n- Matiz activo: {blend['label']} ({blend['description']})" if blend else ""
    await update.message.reply_text(
        f"📊 *Resumen emocional actual:*\n"
        f"- Escenas: {summary['total_scenes']}\n"
        f"- Emoción dominante: {summary['dominant_emotion']}\n"
        f"- Tono tendencia: {summary['tone_trend']}\n"
        f"- Balance emocional: {summary['emotion_balance']}{blend_text}",
        parse_mode="Markdown",
    )

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dash = EmotionDashboard()
    md = dash.generate_markdown()
    dash.save_html()
    await update.message.reply_text(md, parse_mode="Markdown")

async def export_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    report = NarrativeReport()
    path = report.save_report()
    await update.message.reply_text(
        f"📜 Informe narrativo generado.\nArchivo: `{os.path.basename(path)}`",
        parse_mode="Markdown",
    )

# ================================================================
# 💾 SESIONES Y CONTINUIDAD
# ================================================================
async def resume_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    persistence = NarrativePersistence(mood_manager)
    persistence.restore_last_state()
    intro = persistence.generate_continuation_intro()
    await update.message.reply_text(intro, parse_mode="Markdown")

async def savesession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    persistence = NarrativePersistence(mood_manager)
    persistence.save_current_state()
    await update.message.reply_text("💾 Sesión emocional guardada correctamente.")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from core.emotion.emotional_tracker import reset_history
    reset_history(confirm=True)
    scene_manager.reset_local_log()
    mood_manager.current_tone = "neutral"
    mood_manager.last_blend = None
    await update.message.reply_text("🧹 Historial emocional reiniciado.")

# ================================================================
# 🚀 INICIALIZACIÓN DEL BOT
# ================================================================
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ Falta TELEGRAM_BOT_TOKEN.")
    app = Application.builder().token(BOT_TOKEN).build()

    # Comandos principales
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("newscene", new_scene))
    app.add_handler(CommandHandler("end", end_scene))
    app.add_handler(CommandHandler("nextencounter", next_encounter))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("exportreport", export_report))
    app.add_handler(CommandHandler("resume", resume_session))
    app.add_handler(CommandHandler("savesession", savesession))
    app.add_handler(CommandHandler("reset", reset))

    # Mensajes
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 S.A.M. iniciado — Fase 6.30: Narrativa persistente activa.")
    app.run_polling()

# ================================================================
# 🧠 EJECUCIÓN
# ================================================================
if __name__ == "__main__":
    main()
