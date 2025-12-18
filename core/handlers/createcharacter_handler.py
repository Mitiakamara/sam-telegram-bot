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

logger = logging.getLogger("CreateCharacterHandler")

from core.character_builder.builder_interactive import CharacterBuilderInteractive
from core.character_builder.point_buy_system import PointBuySystem, ATTRIBUTES as ATTRIBUTE_NAMES

# Estados de conversación
(
    NAME,
    RACE,
    CLASS,
    BACKGROUND,
    ATTRIBUTE_METHOD,  # Choose point buy or standard array
    ALLOCATE_ATTRIBUTES,  # Point buy allocation
    SKILLS,
    CONFIRM,
) = range(8)

logger = logging.getLogger("CreateCharacterHandler")


def register_createcharacter_conversation(application, campaign_manager):
    builder = CharacterBuilderInteractive()
    
    async def _show_point_buy_interface(query, data: dict, context: ContextTypes.DEFAULT_TYPE):
        """Shows the point buy interface for current attribute."""
        point_buy: PointBuySystem = context.user_data.get("point_buy_system")
        if not point_buy:
            point_buy = PointBuySystem()
            context.user_data["point_buy_system"] = point_buy
        attributes = data.get("attributes", {})
        current_index = data.get("current_attr_index", 0)
        current_attr = ATTRIBUTE_NAMES[current_index]
        current_value = attributes.get(current_attr, 8)
        remaining_points = point_buy.get_remaining_points(attributes)
        
        # Build message
        message = f"💪 *Point Buy - {current_attr}*\n\n"
        message += f"Valor actual: *{current_value}*\n"
        message += f"Puntos restantes: *{remaining_points}/27*\n\n"
        
        # Show all attributes status
        message += "📊 Atributos:\n"
        for i, attr in enumerate(ATTRIBUTE_NAMES):
            value = attributes.get(attr, 8)
            cost = point_buy.get_cost(value)
            marker = "👉" if i == current_index else "  "
            message += f"{marker} {attr}: {value} ({cost} pts)\n"
        
        message += f"\nUsa los botones para ajustar {current_attr}."
        
        # Build keyboard
        keyboard = []
        
        # Decrease button
        if point_buy.can_decrease(current_value):
            keyboard.append([InlineKeyboardButton("➖ Reducir", callback_data=f"attr_dec_{current_attr}")])
        
        # Current value (info)
        keyboard.append([InlineKeyboardButton(f"Valor: {current_value} (Costo: {point_buy.get_cost(current_value)} pts)", callback_data="attr_info")])
        
        # Increase button
        if point_buy.can_increase(current_value, remaining_points):
            next_value = current_value + 1
            next_cost = point_buy.get_cost(next_value)
            keyboard.append([InlineKeyboardButton(f"➕ Aumentar ({next_cost} pts)", callback_data=f"attr_inc_{current_attr}")])
        
        # Navigation buttons
        nav_row = []
        if current_index > 0:
            nav_row.append(InlineKeyboardButton("◀️ Anterior", callback_data="attr_prev"))
        if current_index < len(ATTRIBUTE_NAMES) - 1:
            nav_row.append(InlineKeyboardButton("Siguiente ▶️", callback_data="attr_next"))
        if nav_row:
            keyboard.append(nav_row)
        
        # Done button (only if all attributes are set)
        # Permitir avanzar si estamos en el último atributo, incluso si quedan puntos
        # (el usuario puede ajustar otros atributos si necesita usar todos los puntos)
        if current_index == len(ATTRIBUTE_NAMES) - 1:
            if remaining_points == 0:
                keyboard.append([InlineKeyboardButton("✅ Confirmar Atributos", callback_data="attr_done")])
            elif remaining_points > 0:
                # Mostrar opción de confirmar con advertencia si quedan puntos
                # Pero permitir avanzar si el usuario quiere ajustar otros atributos
                keyboard.append([InlineKeyboardButton(f"✅ Confirmar ({remaining_points} pts restantes - puedes ajustar otros atributos)", callback_data="attr_done")])
                keyboard.append([InlineKeyboardButton("◀️ Volver a ajustar atributos anteriores", callback_data="attr_prev")])
        
        # Standard array option
        keyboard.append([InlineKeyboardButton("🔄 Usar Array Estándar", callback_data="attr_standard")])
        
        try:
            if hasattr(query, 'edit_message_text'):
                await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            else:
                # If it's a message update, send new message
                await query.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error showing point buy interface: {e}")
            # Fallback: send new message
            await query.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

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
        
        # Ask for attribute method
        keyboard = [
            [InlineKeyboardButton("📊 Point Buy (27 puntos)", callback_data="point_buy")],
            [InlineKeyboardButton("🎲 Array Estándar (15,14,13,12,10,8)", callback_data="standard_array")],
        ]
        await query.edit_message_text(
            "💪 ¿Cómo quieres asignar tus atributos?\n\n"
            "📊 *Point Buy*: Asigna 27 puntos (8-15 por atributo)\n"
            "🎲 *Array Estándar*: Usa valores predefinidos",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return ATTRIBUTE_METHOD

    async def attribute_method_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles choice between point buy and standard array."""
        query = update.callback_query
        await query.answer()
        data = context.user_data["character_data"]
        method = query.data
        
        if method == "standard_array":
            # Use standard array
            point_buy = PointBuySystem()
            data["attributes"] = point_buy.apply_standard_array()
            data["attribute_method"] = "standard_array"
            data["modifiers"] = {k: (v - 10) // 2 for k, v in data["attributes"].items()}
            
            race = data.get("race", "")
            if race:
                await query.edit_message_text(
                    f"✅ Array estándar aplicado.\n"
                    f"✨ Los bonos raciales de {race} se aplicarán automáticamente.\n\n"
                    f"{builder.get_prompt('skills', data)}"
                )
            else:
                await query.edit_message_text(
                    f"✅ Array estándar aplicado.\n\n"
                    f"{builder.get_prompt('skills', data)}"
                )
            return SKILLS
        
        elif method == "point_buy":
            # Initialize point buy
            data["attribute_method"] = "point_buy"
            data["attributes"] = {attr: 8 for attr in ATTRIBUTE_NAMES}  # Start at minimum
            data["current_attr_index"] = 0  # Start with STR
            context.user_data["point_buy_system"] = PointBuySystem()
            
            # Show point buy interface for first attribute
            await _show_point_buy_interface(query, data, context)
            return ALLOCATE_ATTRIBUTES
        
        return ATTRIBUTE_METHOD

    async def attributes_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles point buy attribute allocation via buttons."""
        query = update.callback_query
        await query.answer()
        data = context.user_data["character_data"]
        point_buy: PointBuySystem = context.user_data.get("point_buy_system", PointBuySystem())
        attributes = data.get("attributes", {})
        current_index = data.get("current_attr_index", 0)
        current_attr = ATTRIBUTE_NAMES[current_index]
        current_value = attributes.get(current_attr, 8)
        remaining_points = point_buy.get_remaining_points(attributes)
        
        callback_data = query.data
        
        # Handle attribute increase
        if callback_data.startswith("attr_inc_"):
            attr_name = callback_data.replace("attr_inc_", "")
            if attr_name == current_attr:
                next_value = current_value + 1
                next_cost = point_buy.get_cost(next_value)
                if remaining_points >= next_cost and next_value <= 15:
                    attributes[attr_name] = next_value
                    data["attributes"] = attributes
                    data["modifiers"] = {k: (v - 10) // 2 for k, v in attributes.items()}
                    await _show_point_buy_interface(query, data, context)
                else:
                    await query.answer("No tienes suficientes puntos o el valor es demasiado alto.", show_alert=True)
            return ALLOCATE_ATTRIBUTES
        
        # Handle attribute decrease
        elif callback_data.startswith("attr_dec_"):
            attr_name = callback_data.replace("attr_dec_", "")
            if attr_name == current_attr and current_value > 8:
                attributes[attr_name] = current_value - 1
                data["attributes"] = attributes
                data["modifiers"] = {k: (v - 10) // 2 for k, v in attributes.items()}
                await _show_point_buy_interface(query, data, context)
            return ALLOCATE_ATTRIBUTES
        
        # Handle navigation
        elif callback_data == "attr_prev":
            if current_index > 0:
                data["current_attr_index"] = current_index - 1
                await _show_point_buy_interface(query, data, context)
            return ALLOCATE_ATTRIBUTES
        
        elif callback_data == "attr_next":
            if current_index < len(ATTRIBUTE_NAMES) - 1:
                data["current_attr_index"] = current_index + 1
                await _show_point_buy_interface(query, data, context)
            return ALLOCATE_ATTRIBUTES
        
        # Handle done
        elif callback_data == "attr_done":
            # Validate allocation
            remaining = point_buy.get_remaining_points(attributes)
            is_valid, error = point_buy.validate_allocation(attributes)
            
            # Si la validación falla pero quedan 1-2 puntos, permitir avanzar con advertencia
            # (puede ser difícil usar exactamente todos los puntos)
            if not is_valid:
                if remaining > 0 and remaining <= 2:
                    # Permitir avanzar con advertencia
                    await query.answer(f"⚠️ Te quedan {remaining} puntos sin usar. Continuando...", show_alert=False)
                    # Continuar con el flujo normal (no retornar ALLOCATE_ATTRIBUTES)
                else:
                    # Otro tipo de error o quedan muchos puntos
                    await query.answer(error, show_alert=True)
                    return ALLOCATE_ATTRIBUTES
            elif remaining > 0 and remaining <= 2:
                # Si es válido pero quedan puntos, mostrar advertencia informativa
                await query.answer(f"⚠️ Te quedan {remaining} puntos sin usar.", show_alert=False)
            
            # Attributes are valid, move to skills
            race = data.get("race", "")
            if race:
                await query.edit_message_text(
                    f"✅ Atributos asignados correctamente.\n"
                    f"✨ Los bonos raciales de {race} se aplicarán automáticamente.\n\n"
                    f"{builder.get_prompt('skills', data)}"
                )
            else:
                await query.edit_message_text(
                    f"✅ Atributos asignados correctamente.\n\n"
                    f"{builder.get_prompt('skills', data)}"
                )
            return SKILLS
        
        # Handle standard array switch
        elif callback_data == "attr_standard":
            data["attributes"] = point_buy.apply_standard_array()
            data["attribute_method"] = "standard_array"
            data["modifiers"] = {k: (v - 10) // 2 for k, v in data["attributes"].items()}
            
            race = data.get("race", "")
            if race:
                await query.edit_message_text(
                    f"✅ Array estándar aplicado.\n"
                    f"✨ Los bonos raciales de {race} se aplicarán automáticamente.\n\n"
                    f"{builder.get_prompt('skills', data)}"
                )
            else:
                await query.edit_message_text(
                    f"✅ Array estándar aplicado.\n\n"
                    f"{builder.get_prompt('skills', data)}"
                )
            return SKILLS
        
        # Info button (no action)
        elif callback_data == "attr_info":
            await query.answer()
            return ALLOCATE_ATTRIBUTES
        
        return ALLOCATE_ATTRIBUTES

    # Old attributes_step removed - now handled by point buy system

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
        
        # Guardar en campaign_manager
        campaign_manager.add_player(
            telegram_id=user_id,
            player_name=character["name"],
            player_data=character,
        )
        
        # IMPORTANTE: También guardar en StoryDirector para que ProcessPlayerActionUseCase lo encuentre
        story_director = context.bot_data.get("story_director")
        if story_director:
            story_director.players[user_id] = character
            logger.info(f"[CreateCharacterHandler] Personaje {character['name']} también guardado en StoryDirector")
        
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
            ATTRIBUTE_METHOD: [CallbackQueryHandler(attribute_method_step)],
            ALLOCATE_ATTRIBUTES: [CallbackQueryHandler(attributes_step)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, skills_step)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_step)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        name="createcharacter_conversation",
        persistent=False,
    )

    application.add_handler(conv_handler)
    logger.info("[CreateCharacterHandler] Conversación /createcharacter registrada.")
