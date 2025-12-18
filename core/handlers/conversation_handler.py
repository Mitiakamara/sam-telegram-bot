"""
Conversational Message Handler
Handles free-form player messages (non-commands) and routes them to GameAPI
for natural language interpretation and narrative response.
Supports multi-player broadcasting in group chats (2-8 players).

Ahora incluye deteccion conversacional de:
- Tiradas de dados ("lanzo 1d20", "tiro percepcion")
- Inventario ("mi inventario", "uso pocion", "agarro espada")
"""
import logging
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters
from core.services.game_service import GameService
from core.campaign.campaign_manager import CampaignManager
from core.use_cases.process_player_action import ProcessPlayerActionUseCase
from core.exceptions import PlayerNotFoundError, GameAPIError
from core.dice_roller.conversational_roller import ConversationalRoller
from core.inventory.inventory_manager import InventoryManager

logger = logging.getLogger("ConversationHandler")


class ConversationHandler:
    """
    Handles conversational gameplay - processes free-form player messages
    and routes them to GameAPI for AI interpretation.
    Supports multi-player broadcasting in group chats.
    
    Detecta patrones conversacionales de dados e inventario antes
    de enviar al GameAPI.
    """

    def __init__(
        self,
        process_action_use_case: ProcessPlayerActionUseCase,
        campaign_manager: CampaignManager,
    ):
        self.process_action_use_case = process_action_use_case
        self.campaign_manager = campaign_manager
        
        # Inicializar sistemas conversacionales
        self.dice_roller = ConversationalRoller(campaign_manager)
        self.inventory_manager = InventoryManager(campaign_manager)

    async def _get_party_members_in_chat(self, chat_id: int) -> list:
        """Gets all party members who are in the same chat."""
        active_party = self.campaign_manager.get_active_party()
        party_members = []
        
        for telegram_id in active_party:
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
        """Broadcasts a message to all party members in the chat."""
        try:
            chat = await context.bot.get_chat(chat_id)
            
            if chat.type in ["group", "supergroup"]:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="Markdown"
                )
            else:
                party_chat_ids = self.campaign_manager.get_all_party_chat_ids()
                
                if not party_chat_ids:
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
        Detecta patrones de dados e inventario antes de enviar al GameAPI.
        """
        user = update.effective_user
        user_id = user.id
        chat_id = update.effective_chat.id
        message_text = update.message.text.strip()

        if len(message_text) < 2:
            return

        # Verificar si esta en creacion de personaje
        if "character_data" in context.user_data:
            logger.info(f"[ConversationHandler] Usuario {user_id} en creacion de personaje, ignorando")
            return
        
        if "createcharacter_conversation" in context.user_data:
            return

        # Verificar que tiene personaje
        player = self.campaign_manager.get_player_by_telegram_id(user_id)
        if not player:
            await update.message.reply_text(
                "No tienes un personaje creado. Usa /createcharacter primero."
            )
            return

        player_name = player.get("name", user.first_name)

        # === 1. DETECTAR TIRADA DE DADOS ===
        roll_intent = self.dice_roller.detect_roll_intent(message_text)
        if roll_intent:
            logger.info(f"[ConversationHandler] Detectada tirada de dados: {roll_intent}")
            result = self.dice_roller.process_roll(user_id, roll_intent, message_text)
            
            if result.get("success"):
                await self._broadcast_to_party(
                    context=context,
                    chat_id=chat_id,
                    message=result.get("message", "Tirada realizada"),
                    acting_player_name=player_name
                )
                return

        # === 2. DETECTAR ACCION DE INVENTARIO ===
        inventory_intent = self.inventory_manager.detect_inventory_intent(message_text)
        if inventory_intent:
            action_type, item = inventory_intent
            logger.info(f"[ConversationHandler] Detectada accion de inventario: {action_type}, item={item}")
            
            result = self.inventory_manager.process_inventory_action(user_id, action_type, item)
            
            if result.get("success"):
                if result.get("is_display"):
                    # Solo mostrar inventario, sin enviar al GameAPI
                    await update.message.reply_text(
                        result.get("message", ""),
                        parse_mode="Markdown"
                    )
                    return
                elif result.get("send_to_gameapi"):
                    # Continuar al GameAPI con la narrativa como contexto
                    pass
                else:
                    # Mostrar narrativa local
                    narrative = result.get("narrative", result.get("message", ""))
                    response = f"*{player_name}*: {message_text}\n\n{narrative}"
                    await self._broadcast_to_party(
                        context=context,
                        chat_id=chat_id,
                        message=response,
                        acting_player_name=player_name
                    )
                    return
            else:
                # Error de inventario
                await update.message.reply_text(result.get("message", "Error con inventario"))
                return

        # === 3. ENVIAR AL GAMEAPI PARA NARRATIVA COMPLETA ===
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        try:
            result = await self.process_action_use_case.execute(
                player_id=user_id, action_text=message_text
            )

            narrative = result.get("narrative", "")
            event = result.get("event")

            response_text = f"*{player_name}*: {message_text}\n\n"
            response_text += narrative

            if event:
                event_title = event.get("event_title", "Evento")
                event_narration = event.get("event_narration", "")
                if event_narration:
                    response_text += f"\n\n *{event_title}*\n{event_narration}"

        except PlayerNotFoundError:
            await update.message.reply_text(
                "No tienes un personaje creado. Usa /createcharacter primero."
            )
            return
        except GameAPIError as e:
            logger.error(f"[ConversationHandler] Error del GameAPI: {e}")
            await update.message.reply_text(f"Error procesando accion: {str(e)}")
            return
        except Exception as e:
            logger.exception(f"[ConversationHandler] Error inesperado: {e}")
            await update.message.reply_text("Error inesperado. Intenta mas tarde.")
            return

        await self._broadcast_to_party(
            context=context,
            chat_id=chat_id,
            message=response_text,
            acting_player_name=player_name
        )

        logger.info(f"[ConversationHandler] Processed action for {player_name} in chat {chat_id}: {message_text[:50]}...")

    def register_handler(self, application):
        """Registers the conversation handler with the Telegram application."""
        handler = MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        )
        application.add_handler(handler, group=-1)
        logger.info("[ConversationHandler] Handler registered with dice and inventory support.")


def register_conversation_handler(
    application,
    process_action_use_case: ProcessPlayerActionUseCase = None,
    campaign_manager: CampaignManager = None,
    game_service: GameService = None,
    story_director=None,
):
    """Convenience function to register the conversation handler."""
    if process_action_use_case is None:
        if campaign_manager is None:
            campaign_manager = application.bot_data.get("campaign_manager")
        if game_service is None:
            game_service = application.bot_data.get("game_service")
        if story_director is None:
            story_director = application.bot_data.get("story_director")

        if not all([game_service, story_director]):
            logger.warning("[ConversationHandler] Missing required services.")
            return

        from core.story_director.director_link import DirectorLink
        director_link = DirectorLink(story_director)

        from core.use_cases.process_player_action import ProcessPlayerActionUseCase
        process_action_use_case = ProcessPlayerActionUseCase(
            game_service=game_service,
            story_director=story_director,
            director_link=director_link,
        )

    if campaign_manager is None:
        campaign_manager = application.bot_data.get("campaign_manager")

    handler = ConversationHandler(process_action_use_case, campaign_manager)
    handler.register_handler(application)
