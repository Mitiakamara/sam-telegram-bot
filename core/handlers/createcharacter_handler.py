from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import logging

from core.character_builder.builder_interactive import CharacterBuilderInteractive

# Estados de conversación
(
    NAME,
    RACE,
    CLASS,
    BACKGROUND,
    ATTRIBUTES,
    CONFIRM,
) = range(6)

logger = logging.getLogger("CreateCharacterHandler")


def register_createcharacter_conversation(application, campaign_manager):
    builder = CharacterBuilderInteractive()

    async def start_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["character_data"] = {}
        await update.message.reply_text(builder.get_prompt("name"))
        return NAME

    async def name_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        if not builder.process_step("name", update.message.text, data):
            await update.message.reply_text("❌ Nombre inválido. Intenta de nuevo.")
            return NAME
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in builder.get_options("race")]
        await update.message.reply_text(builder.get_prompt("race"), reply_markup=InlineKeyboardMarkup(keyboard))
        return RACE

    async def race_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        query = update.callback_query
        await query.answer()
        if not builder.process_step("race", query.data, data):
            await query.edit_message_text("❌ Selección inválida. Usa los botones.")
            return RACE
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in builder.get_options("class")]
        await query.edit_message_text(builder.get_prompt("class"), reply_markup=InlineKeyboardMarkup(keyboard))
        return CLASS

    async def class_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        query = update.callback_query
        await query.answer()
        if not builder.process_step("class", query.data, data):
            await query.edit_message_text("❌ Clase inválida.")
            return CLASS
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in builder.get_options("background")]
        await query.edit_message_text(builder.get_prompt("background"), reply_markup=InlineKeyboardMarkup(keyboard))
        return BACKGROUND

    async def background_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        query = update.callback_query
        await query.answer()
        if not builder.process_step("background", query.data, data):
            await query.edit_message_text("❌ Trasfondo inválido.")
            return BACKGROUND
        await query.edit_message_text(builder.get_prompt("attributes"))
        return ATTRIBUTES

    async def attributes_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        if not builder.process_step("attributes", update.message.text, data):
            await update.message.reply_text("❌ Formato inválido. Intenta de nuevo o deja vacío para usar el estándar.")
            return ATTRIBUTES
        await update.message.reply_text(builder.get_prompt("confirm"))
        return CONFIRM

    async def confirm_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        if not builder.process_step("confirm", update.message.text, data):
            await update.message.reply_text("❌ No confirmado. Creación cancelada.")
            return ConversationHandler.END

        character = builder.finalize_character(data)
        campaign_manager.add_player(
            player_name=character["name"],
            player_data=character,
        )
        await update.message.reply_text(f"✅ Personaje *{character['name']}* creado y guardado en la campaña.",
                                        parse_mode="Markdown")
        return ConversationHandler.END

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("createcharacter", start_creation)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_step)],
            RACE: [CallbackQueryHandler(race_step)],
            CLASS: [CallbackQueryHandler(class_step)],
            BACKGROUND: [CallbackQueryHandler(background_step)],
            ATTRIBUTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, attributes_step)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_step)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        name="createcharacter_conversation",
        persistent=False,
    )

    application.add_handler(conv_handler)
    logger.info("[CreateCharacterHandler] Conversación /createcharacter registrada.")
