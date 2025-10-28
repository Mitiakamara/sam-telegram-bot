# sam-telegram-bot/core/character_builder/prompts.py

# 🧙‍♂️ Opciones del SRD 5.2.1 (CC-BY-4.0)
SPECIES = [
    "Dragonborn", "Dwarf", "Elf", "Gnome", "Goliath",
    "Halfling", "Human", "Orc", "Tiefling"
]

CLASSES = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
    "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
    "Warlock", "Wizard"
]

# Para simplificar, solo las más comunes (puedes ampliarlas)
SKILLS = [
    "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
    "History", "Insight", "Intimidation", "Investigation", "Medicine",
    "Nature", "Perception", "Performance", "Persuasion", "Religion",
    "Sleight of Hand", "Stealth", "Survival"
]

# Solo para clases con magia básica (se puede expandir)
SPELLS_BY_CLASS = {
    "Wizard": ["Mage Hand", "Shield", "Detect Magic", "Magic Missile", "Identify"],
    "Cleric": ["Guidance", "Cure Wounds", "Bless", "Light", "Shield of Faith"],
    "Druid": ["Produce Flame", "Entangle", "Goodberry", "Thunderwave"],
    "Sorcerer": ["Fire Bolt", "Charm Person", "Mage Armor", "Sleep"],
    "Warlock": ["Eldritch Blast", "Hex", "Armor of Agathys"],
    "Bard": ["Vicious Mockery", "Healing Word", "Disguise Self", "Faerie Fire"],
}

ABILITIES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
DEFAULT_LEVEL = 1
