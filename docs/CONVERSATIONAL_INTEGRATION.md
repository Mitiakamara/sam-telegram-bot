# 💬 Conversational Gameplay Integration

## Overview

SAM now supports **conversational gameplay** - players can use natural language instead of commands!

## How It Works

### Flow Diagram

```
Player Message → Check if command → 
  If command: Handle via command handler
  If not: → Conversation Handler → 
    GameService → GameAPI /game/action → 
      AI Engine (GPT) interprets → 
        Narrative response → 
          Send to player
```

### Key Components

1. **ConversationHandler** (`core/handlers/conversation_handler.py`)
   - Processes all non-command text messages
   - Routes to GameAPI for AI interpretation
   - Handles player identification
   - Manages responses

2. **GameService** (`core/services/game_service.py`)
   - Updated to use correct GameAPI format
   - Handles action processing
   - Manages party operations
   - Error handling

3. **GameAPI Integration**
   - Uses existing AI engine (GPT-4o-mini/GPT-5)
   - Interprets natural language
   - Generates narrative responses
   - Maintains game state and history

## Examples

### Combat Actions
```
Player: "I hit the goblin with my axe"
→ GameAPI AI interprets as combat action
→ Returns narrative: "You swing your axe with determination..."
```

### Exploration
```
Player: "I search the room for hidden doors"
→ GameAPI AI interprets as investigation
→ Returns narrative: "You carefully examine the walls..."
```

### Spell Casting
```
Player: "I cast fireball at the orcs"
→ GameAPI AI interprets as spell
→ Returns narrative: "You weave the arcane energies..."
```

### Dialogue
```
Player: "Can I talk to the merchant?"
→ GameAPI AI interprets as dialogue
→ Returns narrative with NPC response
```

## Multi-Player Support

### Current Implementation
- Each player's actions are processed individually
- Responses sent only to the acting player
- Party state managed via GameAPI

### Future Enhancement
- Broadcast responses to all party members
- Turn management system
- Action queuing for simultaneous actions

## Party Management

### Integration Points
- `/join` command now also joins GameAPI party
- Party state synchronized between bot and GameAPI
- Player names used for GameAPI identification

## Error Handling

### Connection Errors
- Graceful fallback messages
- Logging for debugging
- User-friendly error messages

### GameAPI Errors
- Retry logic (future)
- Fallback responses
- State recovery

## Configuration

### Environment Variables
- `GAME_API_URL` - GameAPI endpoint (default: https://sam-gameapi.onrender.com)
- `TELEGRAM_BOT_TOKEN` - Bot token

### GameAPI Requirements
- Must be running and accessible
- OpenAI API key configured in GameAPI
- Game state initialized

## Testing

### Manual Testing
1. Create character: `/createcharacter`
2. Join campaign: `/join`
3. Send natural language message: "I explore the room"
4. Verify narrative response

### Expected Behavior
- Non-command messages routed to GameAPI
- AI generates appropriate narrative
- Response sent to player
- Game state updated

## Known Limitations

1. **Multi-player Broadcasting**: Not yet implemented
   - Only acting player sees response
   - Future: Broadcast to all party members

2. **Turn Management**: Not implemented
   - All players can act simultaneously
   - Future: Initiative-based turns

3. **Action Queuing**: Not implemented
   - Actions processed immediately
   - Future: Queue for conflict resolution

4. **NPC Dialogue**: Basic support
   - Uses GameAPI dialogue mode
   - Future: Enhanced NPC system

## Future Enhancements

1. **Multi-player Broadcasting**
   - Send responses to all party members
   - Group chat support
   - Private message filtering

2. **Turn Management**
   - Initiative system
   - Turn order display
   - Action queuing

3. **Enhanced NPC System**
   - NPC state management
   - Dialogue trees
   - Behavior patterns

4. **Combat System**
   - Initiative tracking
   - Turn-based combat
   - Damage calculation

## Troubleshooting

### GameAPI Not Responding
- Check `GAME_API_URL` environment variable
- Verify GameAPI service is running
- Check network connectivity

### No Response from AI
- Verify OpenAI API key in GameAPI
- Check GameAPI logs
- Verify game state is initialized

### Player Not Found
- Ensure character is created
- Verify player joined party
- Check campaign state

---

**Version**: 7.10  
**Status**: ✅ Active  
**Last Updated**: 2025-01-XX
