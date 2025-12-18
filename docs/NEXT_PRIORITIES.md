# 🎯 Next Priorities - SAM Development

## ✅ What's Done

1. ✅ Conversational gameplay - Players can use natural language
2. ✅ GameAPI integration - Actions processed through AI
3. ✅ Basic character creation - With SRD integration
4. ✅ Party management - Players can join campaigns

## 🔴 Critical Next Steps (Priority 1)

### 1. Multi-Player Broadcasting (6-8 players requirement)
**Status**: Partially done - Only acting player sees responses

**What's needed**:
- Broadcast narrative responses to all party members
- Handle group chat scenarios
- Show who performed which action
- Coordinate simultaneous actions

**Impact**: Makes it truly multi-player (requirement: 6-8 players)

**Estimated effort**: 2-3 days

---

### 2. Adventure Loading System ✅ COMPLETADO
**Status**: ✅ Implemented - Adventures can be loaded from JSON

**What's done**:
- ✅ Load adventure JSON files (like `demo_mine_v1.json`)
- ✅ Initialize game state from adventure
- ✅ Load scenes and render them
- ✅ `/loadcampaign` command fully functional
- ✅ Adventure validation and error handling

**What's still needed**:
- ⏳ Scene navigation based on options (success_scene, fail_scene)
- ⏳ Process adventure options (skill_check, spell, attack)
- ⏳ NPC loading from adventures
- ⏳ Reward application (XP, loot)

**Impact**: Pre-existing campaigns can now be loaded (requirement partially met)

**Estimated effort remaining**: 1-2 days

---

### 3. NPC System
**Status**: Basic support via GameAPI dialogue mode

**What's needed**:
- NPC state management
- NPC dialogue system (enhanced)
- NPC decision-making
- NPC behavior patterns
- Track NPC relationships

**Impact**: Full NPC management (requirement)

**Estimated effort**: 3-4 days

---

## 🟡 Important Next Steps (Priority 2)

### 4. Character Progression Tracking
**Status**: Basic - Characters created, but no XP/leveling

**What's needed**:
- XP tracking per player
- Level-up system
- Ability score improvements
- Class feature progression
- Equipment management

**Impact**: Character progression (requirement)

**Estimated effort**: 2-3 days

---

### 5. Real-Time Modifier Tracking
**Status**: Basic - Modifiers calculated, but not updated dynamically

**What's needed**:
- Update modifiers when attributes change
- Track temporary modifiers (spells, conditions)
- NPC modifier tracking
- Display current modifiers in status

**Impact**: Accurate modifier tracking (requirement)

**Estimated effort**: 1-2 days

---

### 6. Turn Management System
**Status**: Not implemented - All players act simultaneously

**What's needed**:
- Initiative system
- Turn order display
- Action queuing
- Turn-based combat flow

**Impact**: Better multi-player coordination

**Estimated effort**: 2-3 days

---

## 🟢 Nice to Have (Priority 3)

### 7. Combat System Integration
- Initiative tracking
- Turn-based combat
- Damage calculation
- Condition tracking

### 8. Spell System Enhancement
- Spell slot tracking
- Spell casting via natural language
- Spell effects processing

### 9. Equipment & Inventory
- Equipment management
- Inventory system
- Item interactions

---

## 🎯 Recommended Order

### Phase 1: Make It Playable (Week 1)
1. **Multi-player broadcasting** - Critical for 6-8 players
2. **Adventure loading** - Need actual campaigns
3. **Testing & bug fixes** - Ensure stability

### Phase 2: Core Features (Week 2)
4. **NPC system** - Full NPC management
5. **Character progression** - XP and leveling
6. **Modifier tracking** - Real-time updates

### Phase 3: Polish (Week 3+)
7. **Turn management** - Better coordination
8. **Combat system** - Full combat support
9. **Spell system** - Enhanced spellcasting

---

## Immediate Next Step

**I recommend starting with Multi-Player Broadcasting** because:
1. It's a core requirement (6-8 players)
2. Relatively straightforward to implement
3. High impact on user experience
4. Unblocks testing with multiple players

**What it involves**:
- Track all party members in a chat
- When one player acts, broadcast response to all
- Show player name in broadcasts
- Handle private vs group chats

---

## Questions to Answer

Before proceeding, consider:

1. **Chat Structure**: 
   - Will all 6-8 players be in one Telegram group chat?
   - Or separate private chats per player?

2. **Broadcasting Style**:
   - Show all actions to everyone?
   - Or only relevant actions?
   - Private messages for some actions?

3. **Adventure Format**:
   - Use existing `demo_mine_v1.json` format?
   - Or need different structure?

4. **NPC Dialogue**:
   - LLM-based (dynamic)?
   - Tree-based (structured)?
   - Hybrid?

---

**What would you like to tackle first?**
