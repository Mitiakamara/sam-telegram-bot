# 🚀 Next Steps - SAM Development Roadmap

## Priority 1: Core Functionality & Integration (Critical)

### 1.1 Complete GameAPI Integration ⚡ **HIGHEST PRIORITY**
**Why**: Currently, player actions aren't processed through the game engine.

**Tasks**:
- [ ] Integrate `GameService` into player action handlers
- [ ] Route player text input through `sam-gameapi` for action resolution
- [ ] Handle combat, skill checks, and dice rolls via GameAPI
- [ ] Use `DirectorLink` to process GameAPI results into narrative
- [ ] Add error handling for GameAPI connection failures

**Impact**: Makes the bot actually playable with proper D&D mechanics.

**Estimated Effort**: 2-3 days

---

### 1.2 Load Adventure Content 📖 **HIGH PRIORITY**
**Why**: "The Genie's Wishes" adventure exists but isn't loaded into the system.

**Tasks**:
- [ ] Parse `adventures/demo_mine_v1.json` structure
- [ ] Create adventure loader that reads JSON adventures
- [ ] Integrate adventure scenes into StoryDirector
- [ ] Add `/loadcampaign` command to actually load adventures
- [ ] Support multiple adventures (not just one hardcoded)

**Impact**: Enables actual campaign play instead of generic scenes.

**Estimated Effort**: 1-2 days

---

### 1.3 Player Action Processing 🎮 **HIGH PRIORITY**
**Why**: Players can't actually interact with the game world yet.

**Tasks**:
- [ ] Add message handler for free-form player text (not just commands)
- [ ] Route player messages to GameAPI for processing
- [ ] Display results in narrative format
- [ ] Update scene state based on actions
- [ ] Handle skill checks, attacks, spells, etc.

**Impact**: Makes the bot interactive, not just command-based.

**Estimated Effort**: 2-3 days

---

## Priority 2: Quality & Reliability (Important)

### 2.1 Add Error Handling & Logging 🛡️
**Why**: Better debugging and user experience when things go wrong.

**Tasks**:
- [ ] Add try/except blocks around all external API calls
- [ ] Implement retry logic for SRD/GameAPI failures
- [ ] Add structured logging with context
- [ ] Create error messages for users (not just logs)
- [ ] Add health check endpoint/monitoring

**Impact**: More stable, debuggable system.

**Estimated Effort**: 1-2 days

---

### 2.2 Add Basic Testing 🧪
**Why**: No tests exist - risky to make changes.

**Tasks**:
- [ ] Set up pytest
- [ ] Add unit tests for CampaignManager
- [ ] Add unit tests for StoryDirector core methods
- [ ] Add integration tests for character creation
- [ ] Add mock tests for SRD/GameAPI calls

**Impact**: Confidence to refactor and add features safely.

**Estimated Effort**: 2-3 days

---

### 2.3 Improve Character Creation UX 🎨
**Why**: Current flow could be smoother.

**Tasks**:
- [ ] Show character preview before confirmation
- [ ] Allow editing previous steps
- [ ] Add spell selection for spellcasters (not just auto-assign)
- [ ] Show racial bonuses preview before applying
- [ ] Add equipment selection

**Impact**: Better user experience.

**Estimated Effort**: 1-2 days

---

## Priority 3: Features & Enhancement (Nice to Have)

### 3.1 Connect Emotion System 🎭
**Why**: Many emotion modules exist but may not be fully connected.

**Tasks**:
- [ ] Verify all emotion modules are actually used
- [ ] Connect emotional feedback to scene generation
- [ ] Make tone adaptation actually affect narrative
- [ ] Add emotion visualization in `/status` command
- [ ] Test emotional continuity across scenes

**Impact**: More dynamic, adaptive storytelling.

**Estimated Effort**: 2-3 days

---

### 3.2 Add Dice Rolling Commands 🎲
**Why**: Players need to roll dice in D&D.

**Tasks**:
- [ ] Add `/roll` command (e.g., `/roll 1d20+5`)
- [ ] Add `/check <skill>` command (auto-rolls skill checks)
- [ ] Add `/attack` command (rolls attack and damage)
- [ ] Integrate with GameAPI for rule validation
- [ ] Display results in narrative format

**Impact**: Core D&D functionality.

**Estimated Effort**: 1-2 days

---

### 3.3 Add Combat System ⚔️
**Why**: D&D needs combat encounters.

**Tasks**:
- [ ] Integrate with GameAPI for encounter generation
- [ ] Add initiative tracking
- [ ] Add turn-based combat flow
- [ ] Handle damage, healing, conditions
- [ ] Display combat state to players

**Impact**: Full D&D combat experience.

**Estimated Effort**: 3-5 days

---

### 3.4 Add Spell System ✨
**Why**: Spellcasters need to cast spells.

**Tasks**:
- [ ] Query SRD service for spell details
- [ ] Add `/spell <name>` command to cast spells
- [ ] Track spell slots usage
- [ ] Handle spell effects via GameAPI
- [ ] Display spell descriptions from SRD

**Impact**: Spellcasting classes become playable.

**Estimated Effort**: 2-3 days

---

## Priority 4: Infrastructure & Scale (Future)

### 4.1 Database Migration 💾
**Why**: JSON files don't scale well.

**Tasks**:
- [ ] Design PostgreSQL schema
- [ ] Create migration scripts
- [ ] Migrate CampaignManager to use DB
- [ ] Migrate StoryDirector state to DB
- [ ] Add connection pooling

**Impact**: Better performance, multi-instance support.

**Estimated Effort**: 3-5 days

---

### 4.2 Multi-Campaign Support 🗺️
**Why**: Currently supports one campaign at a time.

**Tasks**:
- [ ] Add campaign ID to all state
- [ ] Support multiple active campaigns
- [ ] Add campaign switching
- [ ] Add campaign management commands
- [ ] Isolate player data per campaign

**Impact**: Can run multiple games simultaneously.

**Estimated Effort**: 2-3 days

---

### 4.3 Admin Commands 👑
**Why**: Need tools to manage the bot.

**Tasks**:
- [ ] Add `/admin` command group
- [ ] Add campaign management (create, delete, list)
- [ ] Add player management (kick, ban, promote)
- [ ] Add system status commands
- [ ] Add logging/analytics commands

**Impact**: Easier bot management.

**Estimated Effort**: 1-2 days

---

## Priority 5: Polish & Documentation (Ongoing)

### 5.1 Improve Documentation 📚
**Tasks**:
- [ ] Add API documentation for handlers
- [ ] Document all environment variables
- [ ] Add deployment guide
- [ ] Add troubleshooting guide
- [ ] Add examples and tutorials

**Estimated Effort**: Ongoing

---

### 5.2 Code Quality Improvements 🧹
**Tasks**:
- [ ] Add type hints everywhere
- [ ] Run linters (black, flake8, mypy)
- [ ] Add docstrings to all functions
- [ ] Refactor duplicate code
- [ ] Optimize slow operations

**Estimated Effort**: Ongoing

---

## Recommended Starting Point

**Start with Priority 1.1 (GameAPI Integration)** because:
1. It's the foundation for everything else
2. Makes the bot actually functional
3. Unblocks other features
4. Relatively straightforward to implement

**Then move to Priority 1.2 (Adventure Loading)** to have actual content to play.

**Then Priority 1.3 (Player Actions)** to make it interactive.

---

## Quick Wins (Can Do Anytime)

These are small improvements that provide immediate value:

- [ ] Add `/help` command with all available commands
- [ ] Add `/dice` or `/roll` command for manual dice rolling
- [ ] Improve error messages (user-friendly, not technical)
- [ ] Add character sheet display in `/status`
- [ ] Add campaign summary in `/progress`
- [ ] Add emoji reactions to bot messages
- [ ] Add typing indicators during processing
- [ ] Add command aliases (e.g., `/c` for `/createcharacter`)

---

## Questions to Answer First

Before diving deep, consider:

1. **What's the primary use case?**
   - Solo play? Group play? Both?
   - This affects multi-player features priority

2. **How important is SRD compliance?**
   - Strict rules enforcement vs. narrative flexibility
   - Affects GameAPI integration depth

3. **What's the deployment target?**
   - Render.com only? Or also self-hosted?
   - Affects infrastructure decisions

4. **Who's the target audience?**
   - Experienced D&D players? Newcomers?
   - Affects UX and documentation

---

**Last Updated**: 2025-01-XX  
**Version**: 7.7.0
