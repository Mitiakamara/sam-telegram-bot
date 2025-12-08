# 📋 SAM Requirements Analysis

## Core Requirements

### 1. ✅ Pre-existing Campaigns (SRD 5.2.1)
**Status**: Partially implemented
- Adventure JSON structure exists (`demo_mine_v1.json`)
- Need: Adventure loader and campaign manager integration

### 2. ⚠️ Narrative Flexibility + Player Improvisation
**Status**: Not fully implemented
- Current: Command-based (`/event`, `/scene`)
- **Required**: Conversational, natural language interpretation
- **Gap**: Need NLP to understand player intent from free text

### 3. ⚠️ Character Progression Tracking
**Status**: Basic implementation
- Characters created and stored
- Need: XP tracking, leveling, ability improvements
- Need: Equipment, inventory, spell progression

### 4. ❌ Full NPC Management
**Status**: Not implemented
- Need: NPC creation and management
- Need: NPC dialogue system
- Need: NPC decision-making AI
- Need: NPC behavior patterns

### 5. ❌ Conversational Gameplay (CRITICAL)
**Status**: **NOT IMPLEMENTED** - This is the biggest gap
- **Current**: Command-based (`/createcharacter`, `/join`, `/status`)
- **Required**: Natural language understanding
  - "I hit the goblin with my axe" → Combat action
  - "I search the room" → Investigation check
  - "I cast fireball at the orcs" → Spell casting
  - "Can I talk to the merchant?" → NPC interaction
- **Gap**: Need NLP intent detection + action routing

### 6. ⚠️ Accurate Modifier Tracking
**Status**: Partially implemented
- Character modifiers calculated
- Need: Real-time modifier updates
- Need: NPC modifier tracking
- Need: Temporary modifiers (spells, conditions)

### 7. ⚠️ Multi-Player Support (6-8 players)
**Status**: Basic implementation
- Players can join campaign
- Need: Turn management
- Need: Action queuing
- Need: Group state synchronization
- Need: Player-specific responses

---

## Architecture Gaps

### Critical Missing Components

1. **NLP Intent Parser** 🔴
   - Understands natural language player input
   - Maps to game actions (combat, skill check, spell, dialogue)
   - Extracts entities (targets, items, locations)

2. **Action Router** 🔴
   - Routes parsed intents to appropriate handlers
   - Combat → GameAPI
   - Skill check → GameAPI
   - Spell → SRD service + GameAPI
   - Dialogue → NPC system

3. **NPC System** 🔴
   - NPC state management
   - Dialogue trees/LLM-based dialogue
   - Decision-making logic
   - Behavior patterns

4. **Conversation Handler** 🔴
   - Processes all non-command messages
   - Integrates with NLP parser
   - Manages conversation context
   - Handles multi-player turn-taking

5. **Game State Synchronization** 🟡
   - Real-time state updates for all players
   - Conflict resolution
   - Action ordering

---

## Implementation Plan

### Phase 1: Conversational Core (CRITICAL)
**Goal**: Replace command-based with conversational gameplay

1. **NLP Intent Detection**
   - Use existing `core/nlp_intent.py` or enhance it
   - Detect: combat, skill check, spell, dialogue, movement, interaction
   - Extract: action type, target, modifiers

2. **Message Handler for Free Text**
   - Add handler for all non-command messages
   - Route through NLP parser
   - Route to appropriate action handler

3. **Action Processing Pipeline**
   ```
   Player Message → NLP Parser → Intent + Entities → Action Router → 
   GameAPI/SRD → Result Processing → Narrative Response
   ```

### Phase 2: NPC System
1. NPC data model
2. Dialogue system (LLM-based or tree-based)
3. NPC decision-making
4. NPC state management

### Phase 3: Multi-Player Coordination
1. Turn management
2. Action queuing
3. State synchronization
4. Player-specific responses

### Phase 4: Progression & Polish
1. XP tracking
2. Leveling system
3. Equipment management
4. Advanced modifiers

---

## Current vs Required Architecture

### Current Architecture
```
Telegram Message → Command Handler → Simple Response
```

### Required Architecture
```
Telegram Message → NLP Parser → Intent Detection → 
Action Router → GameAPI/SRD/NPC System → 
Result Processing → Narrative Generator → Response
```

---

## Key Questions

1. **NLP Approach**:
   - Use existing `core/nlp_intent.py`?
   - Integrate with LLM (GPT/Claude) for intent?
   - Rule-based pattern matching?
   - Hybrid approach?

2. **NPC Dialogue**:
   - LLM-based (dynamic)?
   - Tree-based (structured)?
   - Hybrid?

3. **Multi-Player Turn Management**:
   - Strict turn order?
   - Free-form with queuing?
   - Initiative-based?

4. **GameAPI Integration**:
   - Does GameAPI handle all game mechanics?
   - Or does bot need local rule engine?
   - How to handle NPC actions?

---

## Priority Reassessment

Given these requirements, the priorities change:

### 🔴 CRITICAL (Must Have)
1. **Conversational NLP System** - Without this, core requirement fails
2. **Action Router** - Routes intents to correct handlers
3. **GameAPI Integration** - For mechanical resolution
4. **Message Handler for Free Text** - Process all player messages

### 🟡 HIGH (Important)
5. **NPC System** - Required for full functionality
6. **Multi-Player Coordination** - 6-8 players requirement
7. **Adventure Loading** - Pre-existing campaigns

### 🟢 MEDIUM (Nice to Have)
8. **Character Progression** - Can be added incrementally
9. **Advanced Modifiers** - Basic tracking exists
10. **Polish & UX** - Ongoing

---

## Next Steps

1. **Get access to other repositories** (sam-gameapi, sam-srdservice)
2. **Design NLP intent system** architecture
3. **Implement conversational message handler**
4. **Integrate with GameAPI** for action processing
5. **Build NPC system** foundation
