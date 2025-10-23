import os
import asyncio
import logging
import httpx
import json
import random
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
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================

print("🧠 Booting S.A.M. background worker...", flush=True)
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL", "https://sam-gameapi.onrender.com")
SRD_SERVICE_URL = os.getenv("SRD_SERVICE_URL", "https://sam-srdservice.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

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
        if "rewards" in nxt:
            xp = nxt["rewards"].get("xp_gain", 0)
            await query.message.reply_text(f"🏅 Has ganado {xp} XP", parse_mode="Markdown")
    else:
        await query.message.reply_text("🌑 Fin de la aventura demo.", parse_mode="Markdown")

# ================================================================
# 🧠 FUNCIONES PRINCIPALES DEL BOT
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 *Bienvenido a S.A.M.*, tu Dungeon Master virtual.\n\n"
        "Usa `/join` para unirte a la aventura o `/demo` para probar una historia corta.\n\n"
        "Ejemplos:\n"
        "➡️ `combat medium`\n"
        "➡️ `explore dungeon`\n"
        "➡️ `rest junto a la fogata`\n\n"
        "Prepárate para adentrarte en un mundo de fantasía...",
        parse_mode="Markdown"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(f"🧙‍♂️ {user}, te has unido a la partida. ¡Que comience la aventura!")

async def state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Estado de la partida: pronto disponible.")

# ================================================================
# 🚀 MAIN LOOP (con delay para evitar 409)
# ================================================================

async def main_async():
    print("🚀 Lanzando S.A.M. Bot...", flush=True)
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN no configurado.", flush=True)
        return

    bot = Bot(token=BOT_TOKEN)
    try:
        # 🧹 Limpieza del webhook
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("🧹 Webhook borrado antes del polling.")
        # 🕓 Espera para evitar conflicto con la instancia anterior
        await asyncio.sleep(10)
    except Exception as e:
        logging.warning(f"⚠️ No se pudo borrar webhook inicial: {e}")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("state", state))
    app.add_handler(CommandHandler("demo", lambda u, c: send_scene(u, c, "mine_entrance")))
    app.add_handler(CallbackQueryHandler(handle_demo_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: u.message.reply_text("🧩 Acción registrada.")))

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
