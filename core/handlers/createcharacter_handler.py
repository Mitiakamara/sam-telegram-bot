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
    SKILLS,
    CONFIRM,
) = range(7)

logger = logging.getLogger("CreateCharacterHandler")


def register_createcharacter_conversation(application, campaign_manager):
    builder = CharacterBuilderInteractive()

    async def start_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["character_data"] = {}
        await update.message.reply_text(builder.get_prompt("name", {}))
        return NAME

    async def name_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        if not builder.process_step("name", update.message.text, data):
            await update.message.reply_text("❌ Nombre inválido. Intenta de nuevo.")
            return NAME
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in builder.get_options("race")]
        await update.message.reply_text(builder.get_prompt("race", data), reply_markup=InlineKeyboardMarkup(keyboard))
        return RACE

    async def race_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        query = update.callback_query
        await query.answer()
        if not builder.process_step("race", query.data, data):
            await query.edit_message_text("❌ Selección inválida. Usa los botones.")
            return RACE
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in builder.get_options("class")]
        await query.edit_message_text(builder.get_prompt("class", data), reply_markup=InlineKeyboardMarkup(keyboard))
        return CLASS

    async def class_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        query = update.callback_query
        await query.answer()
        if not builder.process_step("class", query.data, data):
            await query.edit_message_text("❌ Clase inválida.")
            return CLASS
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in builder.get_options("background")]
        await query.edit_message_text(builder.get_prompt("background", data), reply_markup=InlineKeyboardMarkup(keyboard))
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
        
        # Show attributes with racial bonuses preview
        race = data.get("race")
        if race:
            await update.message.reply_text(
                f"✨ Los bonos raciales de {race} se aplicarán automáticamente después."
            )
        
        await update.message.reply_text(builder.get_prompt("skills", data))
        return SKILLS

    async def skills_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        if not builder.process_step("skills", update.message.text, data):
            await update.message.reply_text("❌ Habilidades inválidas. Intenta de nuevo o deja vacío para usar las predeterminadas.")
            return SKILLS
        
        selected_skills = data.get("selected_skills", [])
        background_skills = builder.enhanced_builder.get_background_skills(data.get("background", ""))
        all_skills = list(set(selected_skills + background_skills))
        
        await update.message.reply_text(
            f"✅ Habilidades seleccionadas: {', '.join(all_skills)}\n\n"
            f"{builder.get_prompt('confirm', data)}"
        )
        return CONFIRM

    async def confirm_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data["character_data"]
        if not builder.process_step("confirm", update.message.text, data):
            await update.message.reply_text("❌ No confirmado. Creación cancelada.")
            return ConversationHandler.END

        # Show loading message
        await update.message.reply_text("🔄 Creando personaje con mejoras SRD... (esto puede tomar unos segundos)")

        # Finalize character with enhancements (async)
        character = await builder.finalize_character(data)
        user_id = update.effective_user.id
        
        # Add telegram_id to character
        character["telegram_id"] = user_id
        
        campaign_manager.add_player(
            telegram_id=user_id,
            player_name=character["name"],
            player_data=character,
        )
        
        # Build summary message
        race = character.get("race", "")
        class_name = character.get("class", "")
        attributes = character.get("attributes", {})
        skills = character.get("skills", [])
        spells = character.get("spells", [])
        background_feature = character.get("background_feature")
        
        summary = f"✅ *Personaje {character['name']} creado y guardado*\n\n"
        summary += f"🏹 Raza: {race}\n"
        summary += f"⚔️ Clase: {class_name}\n"
        summary += f"📊 Atributos (con bonos raciales):\n"
        for attr, value in attributes.items():
            modifier = character.get("modifiers", {}).get(attr, 0)
            summary += f"  • {attr}: {value} ({modifier:+d})\n"
        summary += f"\n📚 Habilidades: {', '.join(skills)}\n"
        
        if spells:
            summary += f"\n✨ Hechizos: {', '.join(spells[:5])}"
            if len(spells) > 5:
                summary += f" (+{len(spells) - 5} más)"
        
        if background_feature:
            summary += f"\n\n🎭 Característica de trasfondo: *{background_feature['name']}*\n"
            summary += f"{background_feature['description']}"
        
        await update.message.reply_text(summary, parse_mode="Markdown")
        return ConversationHandler.END

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("createcharacter", start_creation)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_step)],
            RACE: [CallbackQueryHandler(race_step)],
            CLASS: [CallbackQueryHandler(class_step)],
            BACKGROUND: [CallbackQueryHandler(background_step)],
            ATTRIBUTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, attributes_step)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, skills_step)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_step)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        name="createcharacter_conversation",
        persistent=False,
    )

    application.add_handler(conv_handler)
    logger.info("[CreateCharacterHandler] Conversación /createcharacter registrada.")
