import logging
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Importa el manejador de creación interactiva
from core.handlers.createcharacter_handler import register_createcharacter_conversation

logger = logging.getLogger("PlayerHandler")


# ============================================================
#  HANDLERS PRINCIPALES DE JUGADOR
# ============================================================

def register_player_handlers(application, campaign_manager):
    """
    Registra los comandos principales del jugador:
    /start, /join, /status, /progress, /scene
    Y la conversación interactiva /createcharacter.
    """

    # ------------------------------------------------------------
    # /start
    # ------------------------------------------------------------
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Initialize game if not already started
        game_service = context.bot_data.get("game_service")
        if game_service:
            # Check if game is already started, if not, start it
            state = await game_service.get_game_state()
            if not state.get("success"):
                # Game not started, initialize it
                await game_service.start_game()
        
        await update.message.reply_text(
            "🧙‍♂️ Bienvenido a SAM The Dungeon Bot\n"
            "DM automático para campañas SRD 5.2.1.\n\n"
            "📋 Comandos principales:\n"
            "• /createcharacter – crear tu personaje\n"
            "• /join – unirte a la campaña\n"
            "• /status – ver tu estado actual\n"
            "• /progress – ver progreso de la campaña\n"
            "• /scene – mostrar escena actual\n"
            "• /event <tipo> – ejecutar evento narrativo\n\n"
            "💬 Modo conversacional:\n"
            "Puedes usar lenguaje natural para interactuar:\n"
            "• \"Exploro la habitación\"\n"
            "• \"Ataco al goblin con mi espada\"\n"
            "• \"Lanzo bola de fuego a los orcos\"\n"
            "• \"Hablo con el mercader\"\n\n"
            "Versión: 7.10 – Modo conversacional activo 🎮"
        )

    # ------------------------------------------------------------
    # /join
    # ------------------------------------------------------------
    async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        player = campaign_manager.get_player_by_telegram_id(user_id)
        if not player:
            await update.message.reply_text(
                "⚠️ No tienes un personaje creado.\nUsa /createcharacter antes de unirte a la aventura."
            )
            return
        
        player_name = player['name']
        
        # Get current party size
        active_party = campaign_manager.get_active_party()
        current_party_size = len(active_party)
        
        # Check party size limit (2-8 players)
        if current_party_size >= 8:
            await update.message.reply_text(
                "⚠️ La party está completa (máximo 8 jugadores).\n"
                "Espera a que alguien salga o inicia una nueva campaña."
            )
            return
        
        # Add to local campaign (with chat_id for multi-player)
        campaign_manager.add_to_active_party(user_id, chat_id)
        
        # Also join GameAPI party
        game_service = context.bot_data.get("game_service")
        if game_service:
            result = await game_service.join_party(player_name)
            if not result.get("success"):
                error = result.get("error", "Error desconocido")
                if "Ya estás en el grupo" not in error:
                    await update.message.reply_text(f"⚠️ {error}")
        
        # Get updated party size
        new_party_size = len(campaign_manager.get_active_party())
        
        # Broadcast join message to all party members
        join_message = (
            f"🎲 *{player_name}* se ha unido a la campaña.\n"
            f"Party: {new_party_size}/8 jugadores\n\n"
            f"💬 Ahora puedes interactuar usando lenguaje natural:\n"
            f"• \"Exploro la habitación\"\n"
            f"• \"Ataco al goblin con mi espada\"\n"
            f"• \"Lanzo bola de fuego a los orcos\"\n"
            f"• \"Hablo con el mercader\""
        )
        
        # Send to the chat (in group chats, all see it; in private, just the player)
        await update.message.reply_text(join_message, parse_mode="Markdown")
        
        logger.info(f"[PlayerHandler] Jugador {player_name} se unió a la campaña (Party: {new_party_size}/8).")

    # ------------------------------------------------------------
    # /status
    # ------------------------------------------------------------
    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        player = campaign_manager.get_player_by_telegram_id(user_id)
        if not player:
            await update.message.reply_text("⚠️ No tienes un personaje creado aún.")
            return

        stats = player.get("attributes", {})
        msg = (
            f"📊 Estado de *{player['name']}*\n"
            f"Clase: {player['class']}, Raza: {player['race']}\n"
            f"Nivel: {player['level']}\n"
            f"Trasfondo: {player.get('background', 'Desconocido')}\n\n"
            f"Fuerza (STR): {stats.get('STR', 0)}\n"
            f"Destreza (DEX): {stats.get('DEX', 0)}\n"
            f"Constitución (CON): {stats.get('CON', 0)}\n"
            f"Inteligencia (INT): {stats.get('INT', 0)}\n"
            f"Sabiduría (WIS): {stats.get('WIS', 0)}\n"
            f"Carisma (CHA): {stats.get('CHA', 0)}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    # ------------------------------------------------------------
    # /progress
    # ------------------------------------------------------------
    async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chapter = campaign_manager.state.get("chapter", 1)
        current_scene = campaign_manager.state.get("current_scene", "Desconocida")
        await update.message.reply_text(
            f"📖 Progreso actual de la campaña:\n"
            f"Capítulo {chapter}: {current_scene}"
        )

    # ------------------------------------------------------------
    # /scene
    # ------------------------------------------------------------
    async def scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
        current_scene = campaign_manager.state.get("current_scene", "No hay escena activa.")
        await update.message.reply_text(f"🎭 Escena actual:\n{current_scene}")

    # ------------------------------------------------------------
    # REGISTRO DE HANDLERS
    # ------------------------------------------------------------
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("progress", progress))
    application.add_handler(CommandHandler("scene", scene))

    # conversación interactiva de creación de personaje
    register_createcharacter_conversation(application, campaign_manager)

    logger.info(
        "[PlayerHandler] Comandos /start, /createcharacter, /join, /status, /progress y /scene registrados."
    )
