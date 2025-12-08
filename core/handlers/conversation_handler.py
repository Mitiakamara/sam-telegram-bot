"""
Conversational Message Handler
Handles free-form player messages (non-commands) and routes them to GameAPI
for natural language interpretation and narrative response.
"""
import logging
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters
from core.services.game_service import GameService
from core.campaign.campaign_manager import CampaignManager

logger = logging.getLogger("ConversationHandler")


class ConversationHandler:
    """
    Handles conversational gameplay - processes free-form player messages
    and routes them to GameAPI for AI interpretation.
    """

    def __init__(self, game_service: GameService, campaign_manager: CampaignManager):
        self.game_service = game_service
        self.campaign_manager = campaign_manager

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Processes a free-form message from a player.
        Routes it to GameAPI for natural language interpretation.
        """
        user = update.effective_user
        user_id = user.id
        message_text = update.message.text.strip()

        # Skip if message is too short or empty
        if len(message_text) < 2:
            return

        # Get player character from campaign
        player = self.campaign_manager.get_player_by_telegram_id(user_id)
        if not player:
            await update.message.reply_text(
                "⚠️ No tienes un personaje creado. Usa /createcharacter primero."
            )
            return

        player_name = player.get("name", user.first_name)

        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Process action through GameAPI (AI interprets natural language)
        result = await self.game_service.process_action(player_name, message_text)

        if not result.get("success"):
            error_msg = result.get("error", "Error desconocido")
            await update.message.reply_text(f"⚠️ {error_msg}")
            return

        # Get narrative response
        narrative = result.get("result", "")
        
        # Check if a dynamic event was triggered
        event = result.get("event")
        
        # Build response message
        response_text = narrative
        
        if event:
            event_title = event.get("event_title", "Evento")
            event_narration = event.get("event_narration", "")
            response_text += f"\n\n🔮 *{event_title}*\n{event_narration}"

        # Send response
        await update.message.reply_text(response_text, parse_mode="Markdown")

        # TODO: Multi-player broadcasting
        # For now, only the acting player sees the response
        # Future: Broadcast to all party members in the same chat
        # party = await self.game_service.get_party()
        # if party.get("success"):
        #     # Broadcast to all party members
        #     pass

        logger.info(f"[ConversationHandler] Processed action for {player_name}: {message_text[:50]}...")

    def register_handler(self, application):
        """
        Registers the conversation handler with the Telegram application.
        This handler processes all text messages that are NOT commands.
        """
        # Handler for text messages that are not commands
        # Filters.TEXT matches text, ~filters.COMMAND excludes commands
        handler = MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        )
        application.add_handler(handler)
        logger.info("[ConversationHandler] Conversational message handler registered.")


def register_conversation_handler(application, game_service: GameService, campaign_manager: CampaignManager):
    """
    Convenience function to register the conversation handler.
    """
    handler = ConversationHandler(game_service, campaign_manager)
    handler.register_handler(application)
