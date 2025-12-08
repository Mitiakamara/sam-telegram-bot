# 🏗️ SAM Architecture Documentation

## Overview

SAM (Storytelling AI Master) is a D&D 5e Dungeon Master AI bot for Telegram, built with a **3-repository microservices architecture**:

1. **sam-telegram-bot** (this repository) - Telegram bot interface
2. **sam-gameapi** - Game logic and action processing API
3. **sam-srdservice** - SRD 5.1.2/5.2.1 rules reference service

Each service runs on a separate Render.com server.

---

## 📦 Repository Structure

### sam-telegram-bot (Current Repository)

**Purpose**: Telegram bot interface that handles user interactions and orchestrates the narrative.

**Key Components**:

```
/workspace
├── main.py                          # Entry point, initializes bot and handlers
├── bot_service.py                   # Legacy/Unused: HTTP client for GameAPI (future integration)
├── core/
│   ├── campaign/                    # Campaign state management
│   │   └── campaign_manager.py      # Manages campaign state, players, scenes
│   ├── handlers/                    # Telegram command handlers
│   │   ├── player_handler.py        # /start, /join, /status, /progress, /scene
│   │   ├── createcharacter_handler.py # /createcharacter (interactive conversation)
│   │   ├── narrative_handler.py     # /scene, /event
│   │   └── campaign_handler.py      # /progress, /restart, /loadcampaign
│   ├── story_director/              # Narrative orchestration engine
│   │   ├── story_director.py        # Main orchestrator (scenes, events, players)
│   │   ├── transition_engine.py     # Decides next scene based on emotion/event
│   │   └── scene_template_engine.py # Generates scenes from templates
│   ├── character_builder/           # Character creation system
│   ├── services/                    # Service layer
│   │   ├── game_service.py          # HTTP client for sam-gameapi
│   │   ├── emotion_service.py       # Emotion analysis from text
│   │   └── state_service.py         # Game state persistence
│   ├── srd_client.py                # HTTP client for sam-srdservice
│   └── [many other modules...]      # Emotion tracking, rendering, etc.
```

**Environment Variables**:
- `TELEGRAM_BOT_TOKEN` - Bot token from BotFather
- `GAME_API_URL` - URL of sam-gameapi service (default: `https://sam-gameapi.onrender.com`)
- `SRD_SERVICE_URL` - URL of sam-srdservice (default: `https://sam-srdservice.onrender.com`)
- `ADMIN_TELEGRAM_ID` - Optional admin user ID
- `LOG_LEVEL` - Logging level
- `HTTP_TIMEOUT` - HTTP request timeout

**Current Status**: ✅ Functional - All handlers registered, StoryDirector initialized, basic narrative flow working.

---

### sam-gameapi

**Purpose**: Game logic API that processes player actions, combat, dice rolls, and game mechanics.

**Expected Endpoints** (based on bot_service.py):
- `POST /game/action` - Process player action
  - Request: `{"player": "player_id", "action": "action_text"}`
  - Response: Game result with outcome, description, emotion
- `GET /game/state` - Get current game state
- `POST /game/start` - Start a new game session
  - Request: `{"party_levels": [3, 3, 4]}`

**Integration Status**: ⚠️ Partially integrated - `GameService` class exists but not actively used. `bot_service.py` has HTTP client functions ready for integration.

**Future Integration**: The bot should call GameAPI for:
- Processing player actions (attacks, spells, skill checks)
- Combat resolution
- Dice rolling with SRD rules
- Encounter scaling

---

### sam-srdservice

**Purpose**: SRD 5.1.2/5.2.1 rules reference service for spells, features, conditions, monsters, etc.

**Current Integration**: ✅ Active - Used via `core/srd_client.py`

**Endpoints Used**:
- `GET /search?kind={kind}&q={query}` - Search SRD content
  - `kind`: "spell", "feature", "condition", "monster", etc.
  - `q`: Search query text

**Caching**: Results are cached for 1 hour using `aiocache`.

---

## 🔄 Data Flow

### Character Creation Flow
```
User: /createcharacter
  → createcharacter_handler.py (interactive conversation)
  → CharacterBuilderInteractive
  → CampaignManager.add_player()
  → Saved to data/campaign_state.json
```

### Scene Rendering Flow
```
User: /scene
  → narrative_handler.py
  → StoryDirector.render_current_scene()
  → CampaignManager.get_active_scene()
  → AutoNarrator.narrate_scene()
  → Returns formatted text to user
```

### Event Triggering Flow
```
User: /event combat_victory
  → narrative_handler.py
  → StoryDirector.trigger_event("combat_victory")
  → TransitionEngine.get_next_scene(emotion, event_type)
  → SceneTemplateEngine.generate_scene_from_template()
  → CampaignManager.set_current_scene()
  → Returns new scene description
```

### SRD Lookup Flow
```
Character creation / Action processing
  → srd_client.lookup(kind="spell", q="fireball")
  → HTTP GET to sam-srdservice/search
  → Cached result returned
  → Used in character building or action resolution
```

---

## 📊 State Management

### Campaign State (`data/campaign_state.json`)
Managed by `CampaignManager`:
```json
{
  "campaign_name": "TheGeniesWishes",
  "chapter": 1,
  "current_scene": "Oasis perdido",
  "players": {
    "123456789": {
      "name": "PlayerName",
      "class": "Fighter",
      "race": "Human",
      "level": 3,
      "telegram_id": 123456789,
      "attributes": {...}
    }
  },
  "active_party": [123456789]
}
```

### Story Director State (`data/story_director_state.json`)
Managed by `StoryDirector`:
```json
{
  "players": {...},
  "campaign": {...}
}
```

---

## 🎯 Current Issues & Future Work

### ✅ Fixed Issues
- [x] SRD client now uses environment variable
- [x] Missing methods added to CampaignManager
- [x] Missing methods added to StoryDirector
- [x] StoryDirector initialized in main.py
- [x] All handlers registered

### ⚠️ Known Issues / Future Work
- [ ] `bot_service.py` functions not actively used (legacy code for future GameAPI integration)
- [ ] `GameService` class exists but not integrated into handlers
- [ ] `DirectorLink` class exists but not used
- [ ] Full integration with sam-gameapi for action processing
- [ ] Adventure content ("The Genie's Wishes") not yet loaded/parsed
- [ ] PDF parsing pipeline not implemented
- [ ] Database schemas not created (if using PostgreSQL)

### 🔮 Future Architecture Enhancements
1. **Full GameAPI Integration**: Route player actions through GameAPI for proper rule resolution
2. **Adventure Loading**: Parse and load "The Genie's Wishes" adventure content
3. **Database Migration**: Move from JSON files to PostgreSQL for scalability
4. **Encounter Builder**: Dynamic encounter generation based on party level
5. **Spell/Monster Database**: Structured data from SRD service

---

## 🚀 Deployment

### Render.com Configuration

Each service has its own Render service:

1. **sam-telegram-bot** (Worker service)
   - Type: `worker`
   - Build: `pip install -r requirements.txt`
   - Start: `python main.py`
   - Environment variables configured in Render dashboard

2. **sam-gameapi** (Web service)
   - Type: `web`
   - Expected to run FastAPI/Flask server
   - Endpoints: `/game/action`, `/game/state`, `/game/start`

3. **sam-srdservice** (Web service)
   - Type: `web`
   - Endpoints: `/search`

### Local Development

1. Copy `.env.example` to `.env`
2. Set `TELEGRAM_BOT_TOKEN`
3. Set `GAME_API_URL=http://127.0.0.1:9000` (if running locally)
4. Set `SRD_SERVICE_URL=http://127.0.0.1:8000` (if running locally)
5. Run: `python main.py`

---

## 📝 Code Organization Principles

1. **Separation of Concerns**:
   - Handlers: Telegram interaction only
   - Services: External API communication
   - Managers: State management
   - Directors: Business logic orchestration

2. **State Persistence**:
   - Campaign state: `CampaignManager` → JSON file
   - Story state: `StoryDirector` → JSON file
   - Both auto-save on changes

3. **Error Handling**:
   - All handlers have try/except
   - HTTP clients handle connection errors gracefully
   - Logging at INFO level for debugging

---

## 🔗 Related Repositories

- **sam-gameapi**: Game logic and action processing
- **sam-srdservice**: SRD 5.1.2/5.2.1 rules reference

---

**Last Updated**: 2025-01-XX  
**Version**: 7.6.1  
**Maintainer**: Francisco Correa Alfaro
