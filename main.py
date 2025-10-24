# main.py
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from core.narrator import SAMNarrator
from core.party_events import PartyEventSystem

# ================================================================
# ⚙️ CONFIGURACIÓN INICIAL
# ================================================================
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SAM.Main")

# ================================================================
# 🧙‍♂️ SISTEMAS PRINCIPALES
# ================================================================
narrator = SAMNarrator()
party_events = PartyEventSystem(narrator=narrator)
party = []  # lista simple temporal, luego se integrará con DB

# ================================================================
# 🧩 COMANDOS DE PARTY
# ================================================================
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_name = update.effective_user.first_name
    if player_name in party:
        await update.message.reply_text(f"{player_name}, ya estás en el grupo.")
        return

    party.append(player_name)
    msg = party_events.on_player_join(len(party), player_name)
    await update.message.reply_text(msg or f"{player_name} se une al grupo.")

async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_name = update.effective_user.first_name
    if player_name not in party:
        await update.message.reply_text(f"{player_name}, no estás en el grupo.")
        return

    party.remove(player_name)
    msg = party_events.on_player_leave(len(party), player_name, kicked=False)
    await update.message.reply_text(msg or f"{player_name} deja el grupo.")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /kick <nombre>")
        return

    target = context.args[0]
    if target not in party:
        await update.message.reply_text(f"{target} no está en el grupo.")
        return

    party.remove(target)
    msg = party_events.on_player_leave(len(party), target, kicked=True)
    await update.message.reply_text(msg or f"{target} fue expulsado del grupo.")

async def list_party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not party:
        await update.message.reply_text("🎲 No hay aventureros en el grupo todavía.")
        return

    members = "\n".join(f"• {name}" for name in party)
    await update.message.reply_text(f"👥 *Grupo actual:*\n{members}", parse_mode="Markdown")

# ================================================================
# 🚀 INICIO DEL BOT
# ================================================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("leave", leave))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("party", list_party))

    logger.info("🤖 S.A.M. listo para narrar la aventura...")
    app.run_polling()

if __name__ == "__main__":
    main()
