import os
import asyncio
import logging
import httpx
import json
import random
from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)

# ================================================================
# 🧩 Núcleo narrativo
# ================================================================
from core.orchestrator import run_pipeline
from core.models.action import Action, SceneContext, PCStats

# ================================================================
# 🌐 Módulos de juego y persistencia
# ================================================================
from core.handlers import (
    scene_commands,
    action_commands,
    session_commands,
    delete_session_commands,
    join_commands,
    kick_commands
)
from core.utils.logger import get_logger

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================
print("🧠 Booting S.A.M. background worker...", flush=True)
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = get_logger("sam_main")

# ================================================================
# 🧙 FUNCIONES BASE DEL DEMO "La Mina Olvidada"
# ================================================================
JSON_PATH = "adventures/demo_mine_v1.json"
if os.path.exists(JSON_PATH):
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        ADVENTURE = json.load(f)
    SCENES = {s["scene_id"]: s for s in ADVENTURE["scenes"]}
else:
    ADVENTURE = {}
    SCENES = {}

def roll_d20():
    roll = random.randint(1, 20)
    bonus = random.randint(1, 4)
    total = roll + bonus
    return total, roll, bonus

async def send_scene(update: Update, context: ContextTypes.DEFAULT_TYPE, scene_id: str):
    if scene_id not in SCENES:
        await update.message.reply_text("❌ No se encontró la escena solicitada.")
        return

    scene = SCENES[scene_id]
    context.user_data["scene_id"] = scene_id

    text = f"📍 *{scene['title']}*\n{scene['narration']}"
    buttons = [
        [InlineKeyboardButton(opt_text, callback_data=str(i+1))]
        for i, opt_text in enumerate(scene.get("options_text", []))
    ]
    markup = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

async def handle_demo_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    scene_id = context.user_data.get("scene_id", "mine_entrance")
    scene = SCENES.get(scene_id, {})
    choice = int(query.data) - 1
    opt = scene.get("options", [])[choice] if scene else {}
    opt_type = opt.get("type", "action")
    result_text = ""
    next_scene = None

    if opt_type == "skill_check":
        dc = opt.get("dc", 10)
        skill = opt.get("skill", "Habilidad")
        await query.message.reply_text(f"Intentas una prueba de *{skill}* (DC {dc})...", parse_mode="Markdown")
        total, roll, bonus = roll_d20()
        success = total >= dc
        msg = f"🎲 {roll} + {bonus} = {total} vs DC {dc} → {'✅ Éxito' if success else '❌ Fallo'}"
        await query.message.reply_text(msg, parse_mode="Markdown")
        next_scene = opt.get("success_scene") if success else opt.get("fail_scene")

    elif opt_type == "spell":
        spell = opt.get("spell_name", "hechizo")
        result_text = f"✨ Lanzas *{spell}*... una luz mágica se expande."
        next_scene = opt.get("success_scene")

    elif opt_type == "attack":
        result_text = "⚔️ Te lanzas al combate..."
        roll, _, _ = roll_d20()
        if roll >= 12:
            result_text += "\n✅ Impactas y los goblins retroceden."
            next_scene = "treasure_room"
        else:
            result_text += "\n❌ Fallas y los goblins contraatacan."
            next_scene = "end_fail"

    else:
        result_text = "🤔 Actúas con decisión..."
        next_scene = opt.get("success_scene", "end_fail")

    result_text = result_text or "..."
    await query.message.reply_text(result_text, parse_mode="Markdown")

    if next_scene and next_scene in SCENES:
        nxt = SCENES[next_scene]
        await query.message.reply_text(f"📍 *{nxt['title']}*\n{nxt['narration']}", parse_mode="Markdown")
    else:
        await query.message.reply_text("🌑 Fin de la aventura demo.", parse_mode="Markdown")

# ================================================================
# 🧠 FUNCIONES PRINCIPALES DEL BOT
# ================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 *Bienvenido a S.A.M.*, tu Dungeon Master virtual.\n\n"
        "Usa `/join <session_id>` para unirte a una aventura, o `/demo` para probar una historia corta.\n\n"
        "🧭 Comandos de juego:\n"
        "`/scene <id>` – muestra una escena\n"
        "`/action <session_id> <acción>` – ejecuta acciones SRD\n"
        "`/party <session_id>` – muestra los miembros actuales\n\n"
        "🎮 Comandos del Dungeon Master:\n"
        "`/newsession <campaign_id> <party_id>` – crea nueva sesión\n"
        "`/sessions` – lista todas las sesiones\n"
        "`/save <id>` y `/load <id>` – guarda o carga progreso\n"
        "`/deletesession <id|all>` – elimina partidas\n"
        "`/kick <session_id> <nombre>` – expulsa a un jugador\n\n"
        "Prepárate para adentrarte en un mundo de fantasía...",
        parse_mode="Markdown"
    )

# ================================================================
# 🚀 MAIN LOOP
# ================================================================
async def main_async():
    print("🚀 Lanzando S.A.M. Bot...", flush=True)
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("🧹 Webhook limpiado antes del polling.")
        await asyncio.sleep(10)
    except Exception as e:
        logging.warning(f"⚠️ No se pudo borrar webhook: {e}")

    app = Application.builder().token(BOT_TOKEN).build()

    # ------------------------------------------------------------
    # HANDLERS BASE (Demo + Acciones Libres)
    # ------------------------------------------------------------
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("demo", lambda u, c: send_scene(u, c, "mine_entrance")))
    app.add_handler(CallbackQueryHandler(handle_demo_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None))

    # ------------------------------------------------------------
    # HANDLERS PRINCIPALES DE JUEGO
    # ------------------------------------------------------------
    app.add_handler(CommandHandler("scene", scene_commands.scene_command))
    app.add_handler(CommandHandler("action", action_commands.action_command))
    app.add_handler(CommandHandler("join", join_commands.join_command))
    app.add_handler(CommandHandler("party", join_commands.party_command))
    app.add_handler(CommandHandler("kick", kick_commands.kick_command))

    # ------------------------------------------------------------
    # HANDLERS DE ADMINISTRACIÓN Y PERSISTENCIA
    # ------------------------------------------------------------
    app.add_handler(CommandHandler("save", scene_commands.save_command))
    app.add_handler(CommandHandler("load", scene_commands.load_command))
    app.add_handler(CommandHandler("newsession", session_commands.new_session_command))
    app.add_handler(CommandHandler("sessions", session_commands.list_sessions_command))
    app.add_handler(CommandHandler("deletesession", delete_session_commands.delete_session_command))
    app.add_handler(CallbackQueryHandler(delete_session_commands.handle_delete_confirmation,
                                         pattern=r"^(confirm_delete_|cancel_delete)"))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logging.info("🤖 S.A.M. Bot iniciado correctamente. Escuchando mensajes...")
    await asyncio.Event().wait()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logging.info("🛑 S.A.M. detenido manualmente.")
    except Exception as e:
        logging.error(f"❌ Error crítico al iniciar el bot: {e}", exc_info=True)

if __name__ == "__main__":
    main()
