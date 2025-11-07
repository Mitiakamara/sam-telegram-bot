import logging
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from core.character_builder.builder import CharacterBuilder

logger = logging.getLogger("CreateCharacterHandler")

# Estados de conversación
STEP = range(1)

def register_createcharacter_conversation(application, campaign_manager):
    builder = CharacterBuilder()

    async def start_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["builder_data"] = {}
        context.user_data["current_step"] = "name"
        await update.message.reply_text(builder.get_prompt_for_step("name"))
        return STEP

    async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data.get("builder_data", {})
        step = context.user_data.get("current_step")
        text = update.message.text

        try:
            builder.process_step(step, text, data)
        except ValueError as e:
            await update.message.reply_text(f"⚠️ {str(e)}")
            return STEP

        next_step = builder.get_next_step(step)

        if next_step:
            context.user_data["current_step"] = next_step
            await update.message.reply_text(builder.get_prompt_for_step(next_step))
            return STEP
        else:
            character = builder.finalize_character(data)
            campaign_manager.add_player(
                player_name=character["name"],
                player_data=character
            )
            await update.message.reply_text(
                f"✅ Personaje *{character['name']}* creado y guardado en la campaña.",
                parse_mode="Markdown",
            )
            return ConversationHandler.END

    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("❌ Creación de personaje cancelada.")
        return ConversationHandler.END

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("createcharacter", start_creation)],
        states={STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    logger.info("[CreateCharacterHandler] Conversación registrada correctamente.")
