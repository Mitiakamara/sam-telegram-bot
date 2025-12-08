# 🧙‍♂️ Character Creation System

## Overview

SAM uses an **interactive conversation-based** character creation system via Telegram. Users type `/createcharacter` and go through a guided 6-step process.

---

## 🔄 Flow Diagram

```
User: /createcharacter
  ↓
[ConversationHandler starts]
  ↓
Step 1: NAME (text input)
  → User types character name
  → Validates: min 2 characters
  ↓
Step 2: RACE (inline buttons)
  → Shows: Human, Elf, Dwarf, Halfling, Dragonborn, Tiefling, Gnome
  → User clicks button
  ↓
Step 3: CLASS (inline buttons)
  → Shows: Fighter, Wizard, Cleric, Rogue, Paladin, Bard, Ranger
  → User clicks button
  ↓
Step 4: BACKGROUND (inline buttons)
  → Shows: Acolyte, Soldier, Noble, Criminal, Sage, Folk Hero
  → User clicks button
  ↓
Step 5: ATTRIBUTES (text input)
  → User types: "15 14 13 12 10 8" (STR DEX CON INT WIS CHA)
  → OR leaves empty for standard array
  → Validates: 6 numbers, each 3-18
  ↓
Step 6: CONFIRM (text input)
  → User types: "sí" or "yes"
  → Character finalized
  ↓
[Character saved to CampaignManager]
  → Stored in data/campaign_state.json
  → Associated with user's Telegram ID
```

---

## 📁 File Structure

```
core/character_builder/
├── builder_interactive.py    # Main interactive builder (used by handler)
├── builder.py               # Alternative builder (not currently used)
├── prompts.py               # SRD 5.2.1 options (races, classes, skills, spells)
├── validator.py             # Attribute validation (1-20 range)
├── loader.py                # Load characters from JSON files
└── storage.py               # Save characters to JSON files
```

---

## 🎯 Implementation Details

### 1. Handler: `createcharacter_handler.py`

**Type**: Telegram `ConversationHandler` with 6 states

**States**:
```python
NAME = 0      # Text input
RACE = 1      # Inline keyboard buttons
CLASS = 2     # Inline keyboard buttons
BACKGROUND = 3 # Inline keyboard buttons
ATTRIBUTES = 4 # Text input (optional)
SKILLS = 5    # Text input (comma-separated, optional)
CONFIRM = 6   # Text input (yes/no)
```

**Key Features**:
- Uses `context.user_data["character_data"]` to store progress
- Each step validates input before proceeding
- Can be cancelled with `/cancel` at any time
- Final step saves to `CampaignManager` with Telegram ID

### 2. Builder: `CharacterBuilderInteractive`

**Purpose**: Manages the step-by-step logic, validation, and prompts

**Available Options**:

**Races** (7 options):
- Human, Elf, Dwarf, Halfling, Dragonborn, Tiefling, Gnome

**Classes** (7 options):
- Fighter, Wizard, Cleric, Rogue, Paladin, Bard, Ranger

**Backgrounds** (6 options):
- Acolyte, Soldier, Noble, Criminal, Sage, Folk Hero

**Attributes**:
- Default (if empty): `STR:15, DEX:14, CON:13, INT:12, WIS:10, CHA:8`
- Custom: User provides 6 numbers (3-18 each)
- Modifiers calculated automatically: `(value - 10) // 2`

### 3. Validation Rules

| Step | Validation |
|------|------------|
| **Name** | Minimum 2 characters, non-empty |
| **Race** | Must be in predefined list |
| **Class** | Must be in predefined list |
| **Background** | Must be in predefined list |
| **Attributes** | 6 integers, each 3-18, OR empty for default |
| **Confirm** | Must be "sí", "si", "yes", or "y" |

### 4. Final Character Structure

```json
{
  "name": "Aragorn",
  "race": "Human",
  "class": "Ranger",
  "background": "Folk Hero",
  "level": 1,
  "attributes": {
    "STR": 16,  // 15 + 1 (Human bonus)
    "DEX": 15,  // 14 + 1 (Human bonus)
    "CON": 14,  // 13 + 1 (Human bonus)
    "INT": 13,  // 12 + 1 (Human bonus)
    "WIS": 11,  // 10 + 1 (Human bonus)
    "CHA": 9    // 8 + 1 (Human bonus)
  },
  "modifiers": {
    "STR": 3,
    "DEX": 2,
    "CON": 2,
    "INT": 1,
    "WIS": 0,
    "CHA": -1
  },
  "skills": ["Animal Handling", "Survival"],
  "skill_modifiers": {
    "Animal Handling": 2,  // WIS modifier + proficiency
    "Survival": 2
  },
  "spells": ["Cure Wounds", "Hunter's Mark"],
  "spell_slots": {"1st": 0},  // Rangers get spells at level 2
  "background_feature": {
    "name": "Rustic Hospitality",
    "description": "Since you come from the ranks of the common folk, you fit in among them with ease."
  },
  "proficiency_bonus": 2,
  "telegram_id": 123456789
}
```

---

## 🔌 Integration Points

### CampaignManager Integration

After creation, character is saved via:
```python
campaign_manager.add_player(
    telegram_id=user_id,
    player_name=character["name"],
    player_data=character,
)
```

**Storage**: `data/campaign_state.json`
```json
{
  "players": {
    "123456789": {
      "name": "Aragorn",
      "class": "Ranger",
      ...
    }
  }
}
```

### SRD Service Integration

**Current Status**: ⚠️ **Not integrated during creation**

The `prompts.py` file mentions SRD 5.2.1, but the builder doesn't currently:
- Query `sam-srdservice` for race/class features
- Load spell lists from SRD
- Validate against SRD rules
- Load racial bonuses automatically

**Future Enhancement**: Could integrate `srd_client.lookup()` to:
- Fetch race traits (e.g., Elf darkvision, Dwarf resistance)
- Fetch class features (e.g., Fighter Second Wind)
- Fetch background features
- Load spell lists for spellcasting classes

---

## 🎨 User Experience

### Example Conversation

```
User: /createcharacter
Bot: 🧙‍♂️ ¿Cómo se llamará tu personaje?

User: Aragorn
Bot: 🏹 Elige una raza:
     [Human] [Elf] [Dwarf] [Halfling] [Dragonborn] [Tiefling] [Gnome]

User: [clicks Human]
Bot: ⚔️ Elige una clase:
     [Fighter] [Wizard] [Cleric] [Rogue] [Paladin] [Bard] [Ranger]

User: [clicks Ranger]
Bot: 📜 Elige un trasfondo:
     [Acolyte] [Soldier] [Noble] [Criminal] [Sage] [Folk Hero]

User: [clicks Folk Hero]
Bot: 💪 Asigna tus atributos (STR, DEX, CON, INT, WIS, CHA).
     Formato: `15 14 13 12 10 8`
     O deja vacío para usar el estándar.

User: [leaves empty]
Bot: 📚 Selecciona 2 habilidades de tu clase:
     Opciones: Animal Handling, Athletics, Insight, Investigation, Nature, Perception, Stealth, Survival
     Escribe los nombres separados por comas (ej: Perception, Stealth)
     O deja vacío para usar las predeterminadas.
     
     ✨ Tu trasfondo (Folk Hero) ya te da: Animal Handling, Survival

User: Perception, Stealth
Bot: ✅ Habilidades seleccionadas: Perception, Stealth, Animal Handling, Survival
     
     ✅ ¿Confirmas la creación del personaje? (sí/no)

User: sí
Bot: 🔄 Creando personaje con mejoras SRD... (esto puede tomar unos segundos)
Bot: ✅ *Personaje Aragorn creado y guardado*
     
     🏹 Raza: Human
     ⚔️ Clase: Ranger
     📊 Atributos (con bonos raciales):
       • STR: 16 (+3)
       • DEX: 15 (+2)
       • CON: 14 (+2)
       • INT: 13 (+1)
       • WIS: 11 (+0)
       • CHA: 9 (-1)
     
     📚 Habilidades: Perception, Stealth, Animal Handling, Survival
     
     ✨ Hechizos: Cure Wounds, Hunter's Mark
     
     🎭 Característica de trasfondo: *Rustic Hospitality*
     Since you come from the ranks of the common folk, you fit in among them with ease.
```

---

## ⚙️ Configuration

### Available Options

To add more races/classes/backgrounds, edit `builder_interactive.py`:

```python
self.races = ["Human", "Elf", ...]  # Add more here
self.classes = ["Fighter", ...]      # Add more here
self.backgrounds = ["Acolyte", ...] # Add more here
```

Or use the more comprehensive list in `prompts.py`:
- 9 races (includes Goliath, Orc)
- 12 classes (includes Barbarian, Druid, Monk, Sorcerer, Warlock)

### Default Attributes

Current default: `15, 14, 13, 12, 10, 8` (standard array)

To change, edit `builder_interactive.py` line 82:
```python
data["attributes"] = {"STR": 15, "DEX": 14, ...}  # Modify here
```

---

## 🔮 Future Enhancements

### 1. SRD Integration
- [ ] Query `sam-srdservice` for race/class features
- [ ] Auto-apply racial bonuses to attributes
- [ ] Load spell lists for spellcasting classes
- [ ] Validate against SRD 5.2.1 rules

### 2. Point Buy / Rolling
- [ ] Add point buy system (27 points)
- [ ] Add 4d6 drop lowest rolling
- [ ] Add standard array option (current default)

### 3. Skill Selection
- [ ] Let users choose skills based on class/background
- [ ] Calculate skill modifiers automatically
- [ ] Show proficiency bonuses

### 4. Equipment
- [ ] Starting equipment based on class/background
- [ ] Gold calculation
- [ ] Equipment validation

### 5. Leveling
- [ ] Multi-level creation (levels 1-3)
- [ ] ASI/Feat selection
- [ ] Class feature progression

---

## ✅ Recent Enhancements (v7.7.0)

1. **SRD Integration**: ✅ Queries `sam-srdservice` for race/class features and spells
2. **Racial Bonuses**: ✅ Automatically applies racial ability score improvements
3. **Spell Loading**: ✅ Loads appropriate spells for spellcasting classes
4. **Skill Selection**: ✅ Users can choose skills based on class and background
5. **Background Features**: ✅ Grants background features and traits
6. **Enhanced Modifiers**: ✅ Calculates skill modifiers with proficiency bonuses
7. **Skill Proficiencies**: ✅ Combines class and background skill proficiencies

## 🐛 Remaining Limitations

1. **Limited SRD Queries**: Some SRD lookups may fail gracefully (uses fallback data)
2. **Fixed Spell Lists**: If SRD lookup fails, uses hardcoded common spells
3. **No Point Buy**: Only supports standard array or custom input
4. **No Feat Selection**: No feats available at level 1
5. **Limited Backgrounds**: Only 6 backgrounds available (can be expanded)

---

## 📝 Code Examples

### Adding a New Race

```python
# In builder_interactive.py
self.races = ["Human", "Elf", ..., "NewRace"]
```

### Custom Attribute Validation

```python
# In builder_interactive.py, process_step method
if step == "attributes":
    # Your custom validation logic
    ...
```

### Integrating SRD Lookup

```python
from core.srd_client import lookup

# In process_step or finalize_character
race_data = await lookup("race", data["race"], action_id)
# Apply racial bonuses, traits, etc.
```

---

**Last Updated**: 2025-01-XX  
**Version**: 7.6.1
