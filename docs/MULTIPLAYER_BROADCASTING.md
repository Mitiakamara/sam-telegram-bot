# 👥 Multi-Player Broadcasting System

## Overview

SAM now supports **multi-player gameplay in group chats** with 2-8 players. All actions are broadcast to all party members in the group chat.

## How It Works

### Group Chat Structure
- All players join the same Telegram group chat
- Party size: 2-8 players (enforced)
- All actions visible to everyone
- Responses broadcast to the entire group

### Flow

```
Player A: "I hit the goblin with my axe"
  ↓
ConversationHandler processes
  ↓
GameAPI interprets action
  ↓
Response: "PlayerA: I hit the goblin with my axe
           [Narrative response from AI...]"
  ↓
Broadcasted to group chat
  ↓
All party members see the action and response
```

## Implementation Details

### 1. Party Management (`CampaignManager`)

**New Features**:
- Tracks chat IDs for each party member
- Stores `party_chats` mapping: `telegram_id → chat_id`
- Methods:
  - `add_to_active_party(telegram_id, chat_id)` - Join with chat tracking
  - `get_party_chat_id(telegram_id)` - Get chat for a player
  - `get_all_party_chat_ids()` - Get all unique chat IDs

**Party Size Limit**:
- Maximum 8 players enforced
- Players can't join if party is full

### 2. Conversation Handler (`ConversationHandler`)

**Broadcasting Logic**:
- Detects if chat is group or private
- **Group chats**: Sends message to group (all see it automatically)
- **Private chats**: Broadcasts to all party members individually
- Shows player name in format: `*PlayerName*: [action]`

**Message Format**:
```
*PlayerName*: I hit the goblin with my axe

[Narrative response from AI...]

🔮 *Dynamic Event* (if triggered)
[Event narration...]
```

### 3. Join Command (`/join`)

**Enhanced Features**:
- Tracks chat ID when player joins
- Shows party size: "Party: 3/8 jugadores"
- Enforces 8-player limit
- Broadcasts join message to group

## Usage Example

### Setup (Group Chat)

1. **Create Telegram Group Chat**
   - Add bot to group
   - All players join the group

2. **Each Player Creates Character**
   ```
   Player 1: /createcharacter
   Player 2: /createcharacter
   Player 3: /createcharacter
   ...
   ```

3. **Players Join Campaign**
   ```
   Player 1: /join
   → "🎲 Player1 se ha unido a la campaña. Party: 1/8 jugadores"
   
   Player 2: /join
   → "🎲 Player2 se ha unido a la campaña. Party: 2/8 jugadores"
   
   ...
   ```

4. **Players Act (All See Everything)**
   ```
   Player 1: "I explore the room"
   → Bot broadcasts to group:
     "*Player1*: I explore the room
     
     You carefully examine the room, noticing..."
     [All players see this]
   
   Player 2: "I search for hidden doors"
   → Bot broadcasts to group:
     "*Player2*: I search for hidden doors
     
     Running your hands along the walls..."
     [All players see this]
   ```

## Features

### ✅ Implemented

1. **Group Chat Support**
   - Detects group vs private chat
   - Broadcasts appropriately

2. **Party Size Management**
   - 2-8 player limit
   - Shows current party size
   - Prevents joining if full

3. **Action Broadcasting**
   - All actions shown to all players
   - Player name displayed
   - Narrative responses visible to everyone

4. **Chat Tracking**
   - Tracks which chat each player is in
   - Supports multiple groups (future)

### 🔮 Future Enhancements

1. **Turn Management**
   - Initiative system
   - Turn order display
   - Action queuing

2. **Private Actions**
   - Some actions only visible to acting player
   - Secret checks, private thoughts

3. **Action Filtering**
   - Show only relevant actions
   - Filter by proximity, awareness

4. **Multi-Group Support**
   - Multiple campaigns in different groups
   - Isolated party states

## Technical Details

### Data Structure

**Campaign State**:
```json
{
  "active_party": [123456789, 987654321, ...],
  "party_chats": {
    "123456789": -1001234567890,
    "987654321": -1001234567890
  }
}
```

### Chat Types

- **Group/Supergroup**: All members see messages automatically
- **Private**: Messages sent individually to each party member

### Error Handling

- Graceful fallback if broadcast fails
- Logs errors for debugging
- Continues processing even if one player can't receive message

## Testing Checklist

- [ ] Create group chat
- [ ] Add bot to group
- [ ] Multiple players create characters
- [ ] Multiple players join (verify 8-player limit)
- [ ] Player 1 sends action (all see it)
- [ ] Player 2 sends action (all see it)
- [ ] Verify party size display
- [ ] Test with 2 players
- [ ] Test with 8 players (max)
- [ ] Test joining when party is full (should fail)

## Known Limitations

1. **No Turn Management**: All players can act simultaneously
2. **No Action Queuing**: Actions processed immediately
3. **No Private Actions**: Everything is visible to all
4. **Single Group**: One campaign per group (for now)

---

**Version**: 7.11  
**Status**: ✅ Implemented  
**Last Updated**: 2025-01-XX
