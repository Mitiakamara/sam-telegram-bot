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
from core.use_cases.process_player_action import ProcessPlayerActionUseCase
from core.exceptions import PlayerNotFoundError, GameAPIError

logger = logging.getLogger("ConversationHandler")


class ConversationHandler:
    """
    Handles conversational gameplay - processes free-form player messages
    and routes them to GameAPI for AI interpretation.
    Supports multi-player broadcasting in group chats.
    
    Ahora usa casos de uso para separar lógica de negocio.
    """

    def __init__(
        self,
        process_action_use_case: ProcessPlayerActionUseCase,
        campaign_manager: CampaignManager,
    ):
        """
        Inicializa el handler con el caso de uso.
        
        Args:
            process_action_use_case: Caso de uso para procesar acciones
            campaign_manager: Manager de campaña (para broadcasting)
        """
        self.process_action_use_case = process_action_use_case
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

        # IMPORTANTE: Verificar si el usuario está en una conversación activa
        # Si está en una conversación (como crear personaje), no procesar este mensaje
        # Dejar que el ConversationHandler específico lo maneje
        if context.user_data.get("_conversation_active"):
            logger.debug(f"[ConversationHandler] Usuario {user_id} está en conversación activa, ignorando mensaje")
            return
        
        # Verificar si hay alguna conversación activa en el contexto
        # Los ConversationHandler de python-telegram-bot establecen estados en user_data
        # Si hay un estado de conversación, no procesar aquí
        conversation_states = [
            "name", "race", "class", "background", "attribute_method", 
            "allocate_attributes", "skills", "confirm"
        ]
        for state_key in conversation_states:
            if state_key in context.user_data:
                logger.debug(f"[ConversationHandler] Usuario {user_id} tiene estado '{state_key}' activo, ignorando mensaje")
                return

        # Get player character from campaign
        player = self.campaign_manager.get_player_by_telegram_id(user_id)
        if not player:
            await update.message.reply_text(
                "⚠️ No tienes un personaje creado. Usa /createcharacter primero."
            )
            return

        # Show typing indicator to all in chat
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        try:
            # Usar caso de uso para procesar la acción
            # El caso de uso maneja toda la lógica de negocio
            result = await self.process_action_use_case.execute(
                player_id=user_id, action_text=message_text
            )

            # Construir respuesta con nombre del jugador
            player_name = result.get("player_name", user.first_name)
            narrative = result.get("narrative", "")
            event = result.get("event")

            response_text = f"*{player_name}*: {message_text}\n\n"
            response_text += narrative

            # El evento ya está procesado en el caso de uso, solo mostrarlo si existe
            if event:
                event_title = event.get("event_title", "Evento")
                event_narration = event.get("event_narration", "")
                if event_narration:
                    response_text += f"\n\n🔮 *{event_title}*\n{event_narration}"

        except PlayerNotFoundError:
            await update.message.reply_text(
                "⚠️ No tienes un personaje creado. Usa /createcharacter primero."
            )
            return
        except GameAPIError as e:
            logger.error(f"[ConversationHandler] Error del GameAPI: {e}")
            await update.message.reply_text(
                f"⚠️ Error procesando acción: {str(e)}"
            )
            return
        except Exception as e:
            logger.exception(
                f"[ConversationHandler] Error inesperado procesando acción: {e}"
            )
            await update.message.reply_text(
                "⚠️ Error inesperado procesando acción. Intenta más tarde."
            )
            return

        # Broadcast response to all party members in the chat
        await self._broadcast_to_party(
            context=context,
            chat_id=chat_id,
            message=response_text,
            acting_player_name=player_name
        )

        logger.info(
            f"[ConversationHandler] Processed action for {result.get('player_name', 'Unknown')} in chat {chat_id}: {message_text[:50]}..."
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


def register_conversation_handler(
    application,
    process_action_use_case: ProcessPlayerActionUseCase = None,
    campaign_manager: CampaignManager = None,
    game_service: GameService = None,
    story_director=None,
):
    """
    Convenience function to register the conversation handler.
    
    Args:
        application: Telegram application instance
        process_action_use_case: Caso de uso para procesar acciones (opcional)
        campaign_manager: CampaignManager instance (opcional, obtenido de bot_data si no se proporciona)
        game_service: GameService instance (opcional, para crear caso de uso si no se proporciona)
        story_director: StoryDirector instance (opcional, para crear caso de uso si no se proporciona)
    """
    # Si no se proporciona el caso de uso, crearlo
    if process_action_use_case is None:
        # Obtener servicios de bot_data si no se proporcionan
        if campaign_manager is None:
            campaign_manager = application.bot_data.get("campaign_manager")
        if game_service is None:
            game_service = application.bot_data.get("game_service")
        if story_director is None:
            story_director = application.bot_data.get("story_director")

        if not all([game_service, story_director]):
            logger.warning(
                "[ConversationHandler] No se pueden crear servicios necesarios. "
                "Asegúrate de que estén en bot_data o pásalos como parámetros."
            )
            return

        # Crear DirectorLink
        from core.story_director.director_link import DirectorLink

        director_link = DirectorLink(story_director)

        # Crear caso de uso
        from core.use_cases.process_player_action import ProcessPlayerActionUseCase

        process_action_use_case = ProcessPlayerActionUseCase(
            game_service=game_service,
            story_director=story_director,
            director_link=director_link,
        )

    # Obtener campaign_manager si no se proporciona
    if campaign_manager is None:
        campaign_manager = application.bot_data.get("campaign_manager")

    handler = ConversationHandler(process_action_use_case, campaign_manager)
    handler.register_handler(application)
