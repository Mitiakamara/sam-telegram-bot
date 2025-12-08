"""
Conversational Message Handler
Handles free-form player messages (non-commands) and routes them to GameAPI
for natural language interpretation and narrative response.
Supports multi-player broadcasting in group chats (2-8 players).
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
    Supports multi-player broadcasting in group chats.
    """

    def __init__(self, game_service: GameService, campaign_manager: CampaignManager):
        self.game_service = game_service
        self.campaign_manager = campaign_manager

    async def _get_party_members_in_chat(self, chat_id: int) -> list:
        """
        Gets all party members who are in the same chat.
        Returns list of (telegram_id, player_name) tuples.
        """
        active_party = self.campaign_manager.get_active_party()
        party_members = []
        
        for telegram_id in active_party:
            # Check if player is in this chat
            player_chat_id = self.campaign_manager.get_party_chat_id(telegram_id)
            if player_chat_id == chat_id or player_chat_id is None:
                player = self.campaign_manager.get_player_by_telegram_id(telegram_id)
                if player:
                    party_members.append((telegram_id, player.get("name", "Unknown")))
        
        return party_members

    async def _broadcast_to_party(
        self, 
        context: ContextTypes.DEFAULT_TYPE, 
        chat_id: int, 
        message: str,
        acting_player_name: str = None
    ):
        """
        Broadcasts a message to all party members in the chat.
        In group chats, sends to the chat (all members see it automatically).
        In private chats, sends to individual players.
        """
        try:
            chat = await context.bot.get_chat(chat_id)
            
            # Check if it's a group chat
            if chat.type in ["group", "supergroup"]:
                # In group chat, just send to the group (all members see it)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="Markdown"
                )
                logger.debug(f"[ConversationHandler] Broadcasted to group chat {chat_id}")
            else:
                # Private chat - broadcast to all party members individually
                # Get all unique chat IDs where party members are
                party_chat_ids = self.campaign_manager.get_all_party_chat_ids()
                
                if not party_chat_ids:
                    # Fallback: send to current chat
                    party_chat_ids = [chat_id]
                
                for target_chat_id in party_chat_ids:
                    try:
                        await context.bot.send_message(
                            chat_id=target_chat_id,
                            text=message,
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        logger.warning(f"Could not send message to chat {target_chat_id}: {e}")
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            # Fallback: send to current chat
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="Markdown"
                )
            except Exception as fallback_error:
                logger.error(f"Fallback broadcast also failed: {fallback_error}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Processes a free-form message from a player.
        Routes it to GameAPI for natural language interpretation.
        Broadcasts response to all party members in the chat.
        """
        user = update.effective_user
        user_id = user.id
        chat_id = update.effective_chat.id
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

        # Show typing indicator to all in chat
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

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
        
        # Build response message with player name
        # Format: "PlayerName: [action description]" followed by narrative
        response_text = f"*{player_name}*: {message_text}\n\n"
        response_text += narrative
        
        if event:
            event_title = event.get("event_title", "Evento")
            event_narration = event.get("event_narration", "")
            response_text += f"\n\n🔮 *{event_title}*\n{event_narration}"

        # Broadcast response to all party members in the chat
        await self._broadcast_to_party(
            context=context,
            chat_id=chat_id,
            message=response_text,
            acting_player_name=player_name
        )

        logger.info(
            f"[ConversationHandler] Processed action for {player_name} in chat {chat_id}: {message_text[:50]}..."
        )

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
