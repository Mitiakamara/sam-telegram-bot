"""
Enhanced Character Builder with SRD Integration
Integrates with sam-srdservice for race/class features, spells, and skills
"""
import logging
from typing import Dict, Any, List, Optional
from core.srd_client import lookup
from uuid import uuid4

logger = logging.getLogger(__name__)

# Racial ability score improvements (SRD 5.1.2)
RACIAL_BONUSES = {
    "Human": {"STR": 1, "DEX": 1, "CON": 1, "INT": 1, "WIS": 1, "CHA": 1},
    "Elf": {"DEX": 2},
    "Dwarf": {"CON": 2},
    "Halfling": {"DEX": 2},
    "Dragonborn": {"STR": 2, "CHA": 1},
    "Tiefling": {"INT": 1, "CHA": 2},
    "Gnome": {"INT": 2},
    "Goliath": {"STR": 2, "CON": 1},
    "Orc": {"STR": 2, "CON": 1},
}

# Spellcasting classes
SPELLCASTING_CLASSES = ["Wizard", "Cleric", "Druid", "Sorcerer", "Warlock", "Bard", "Paladin", "Ranger"]

# Class skill proficiencies (SRD 5.1.2)
CLASS_SKILLS = {
    "Barbarian": ["Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"],
    "Bard": ["Athletics", "Acrobatics", "Sleight of Hand", "Stealth", "Arcana", "History", "Investigation", "Nature", "Religion", "Animal Handling", "Insight", "Medicine", "Perception", "Survival", "Deception", "Intimidation", "Performance", "Persuasion"],
    "Cleric": ["History", "Insight", "Medicine", "Persuasion", "Religion"],
    "Druid": ["Arcana", "Animal Handling", "Insight", "Medicine", "Nature", "Perception", "Religion", "Survival"],
    "Fighter": ["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"],
    "Monk": ["Acrobatics", "Athletics", "History", "Insight", "Religion", "Stealth"],
    "Paladin": ["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"],
    "Ranger": ["Animal Handling", "Athletics", "Insight", "Investigation", "Nature", "Perception", "Stealth", "Survival"],
    "Rogue": ["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation", "Perception", "Performance", "Persuasion", "Sleight of Hand", "Stealth"],
    "Sorcerer": ["Arcana", "Deception", "Insight", "Intimidation", "Persuasion", "Religion"],
    "Warlock": ["Arcana", "Deception", "History", "Intimidation", "Investigation", "Nature", "Religion"],
    "Wizard": ["Arcana", "History", "Insight", "Investigation", "Medicine", "Religion"],
}

# Background skill proficiencies
BACKGROUND_SKILLS = {
    "Acolyte": ["Insight", "Religion"],
    "Soldier": ["Athletics", "Intimidation"],
    "Noble": ["History", "Persuasion"],
    "Criminal": ["Deception", "Stealth"],
    "Sage": ["Arcana", "History"],
    "Folk Hero": ["Animal Handling", "Survival"],
    "Hermit": ["Medicine", "Religion"],
    "Entertainer": ["Acrobatics", "Performance"],
    "Guild Artisan": ["Insight", "Persuasion"],
    "Outlander": ["Athletics", "Survival"],
    "Sailor": ["Athletics", "Perception"],
    "Charlatan": ["Deception", "Sleight of Hand"],
}

# Background features
BACKGROUND_FEATURES = {
    "Acolyte": {
        "name": "Shelter of the Faithful",
        "description": "You can find a place to hide, rest, or recuperate among other followers of your faith."
    },
    "Soldier": {
        "name": "Military Rank",
        "description": "You have a military rank from your career as a soldier."
    },
    "Noble": {
        "name": "Position of Privilege",
        "description": "Thanks to your noble birth, people are inclined to think the best of you."
    },
    "Criminal": {
        "name": "Criminal Contact",
        "description": "You have a reliable and trustworthy contact who acts as your liaison to a network of other criminals."
    },
    "Sage": {
        "name": "Researcher",
        "description": "When you attempt to learn or recall a piece of lore, you know where to find the information."
    },
    "Folk Hero": {
        "name": "Rustic Hospitality",
        "description": "Since you come from the ranks of the common folk, you fit in among them with ease."
    },
}


class EnhancedCharacterBuilder:
    """
    Enhanced character builder with SRD integration.
    Applies racial bonuses, loads spells, and manages skills.
    """

    def __init__(self):
        self.action_id = uuid4()

    def apply_racial_bonuses(self, race: str, attributes: Dict[str, int]) -> Dict[str, int]:
        """
        Applies racial ability score improvements to attributes.
        """
        bonuses = RACIAL_BONUSES.get(race, {})
        enhanced = attributes.copy()
        
        for ability, bonus in bonuses.items():
            enhanced[ability] = enhanced.get(ability, 10) + bonus
            # Cap at 20
            if enhanced[ability] > 20:
                enhanced[ability] = 20
        
        logger.info(f"[EnhancedBuilder] Applied racial bonuses for {race}: {bonuses}")
        return enhanced

    async def get_race_features(self, race: str) -> List[Dict[str, Any]]:
        """
        Queries SRD service for race features and traits.
        """
        try:
            response = await lookup("race", race, self.action_id)
            if response.hits:
                features = []
                for hit in response.hits:
                    features.append({
                        "name": hit.name,
                        "summary": hit.summary or "",
                        "details": hit.details or {}
                    })
                return features
        except Exception as e:
            logger.warning(f"[EnhancedBuilder] Could not fetch race features for {race}: {e}")
        return []

    async def get_class_features(self, class_name: str) -> List[Dict[str, Any]]:
        """
        Queries SRD service for class features.
        """
        try:
            response = await lookup("class", class_name, self.action_id)
            if response.hits:
                features = []
                for hit in response.hits:
                    features.append({
                        "name": hit.name,
                        "summary": hit.summary or "",
                        "details": hit.details or {}
                    })
                return features
        except Exception as e:
            logger.warning(f"[EnhancedBuilder] Could not fetch class features for {class_name}: {e}")
        return []

    async def get_spells_for_class(self, class_name: str, level: int = 1) -> List[str]:
        """
        Queries SRD service for spells available to a class at a given level.
        """
        if class_name not in SPELLCASTING_CLASSES:
            return []
        
        try:
            # Try to get class spell list
            response = await lookup("spell", class_name.lower(), self.action_id)
            spells = []
            
            # Also try common level 1 spells for the class
            common_spells = {
                "Wizard": ["Mage Hand", "Shield", "Detect Magic", "Magic Missile", "Identify"],
                "Cleric": ["Guidance", "Cure Wounds", "Bless", "Light", "Shield of Faith"],
                "Druid": ["Produce Flame", "Entangle", "Goodberry", "Thunderwave"],
                "Sorcerer": ["Fire Bolt", "Charm Person", "Mage Armor", "Sleep"],
                "Warlock": ["Eldritch Blast", "Hex", "Armor of Agathys"],
                "Bard": ["Vicious Mockery", "Healing Word", "Disguise Self", "Faerie Fire"],
                "Paladin": ["Cure Wounds", "Detect Evil and Good", "Protection from Evil and Good"],
                "Ranger": ["Cure Wounds", "Hunter's Mark", "Goodberry"],
            }
            
            if class_name in common_spells:
                spells = common_spells[class_name]
            
            # Try to enhance with SRD lookup
            if response.hits:
                for hit in response.hits:
                    if hit.name not in spells:
                        spells.append(hit.name)
            
            logger.info(f"[EnhancedBuilder] Loaded {len(spells)} spells for {class_name}")
            return spells[:6]  # Limit to 6 spells for level 1
        except Exception as e:
            logger.warning(f"[EnhancedBuilder] Could not fetch spells for {class_name}: {e}")
            # Fallback to common spells
            common_spells = {
                "Wizard": ["Mage Hand", "Shield", "Detect Magic", "Magic Missile"],
                "Cleric": ["Guidance", "Cure Wounds", "Bless", "Light"],
                "Druid": ["Produce Flame", "Entangle", "Goodberry"],
                "Sorcerer": ["Fire Bolt", "Charm Person", "Mage Armor"],
                "Warlock": ["Eldritch Blast", "Hex"],
                "Bard": ["Vicious Mockery", "Healing Word"],
                "Paladin": ["Cure Wounds", "Detect Evil and Good"],
                "Ranger": ["Cure Wounds", "Hunter's Mark"],
            }
            return common_spells.get(class_name, [])

    def get_class_skills(self, class_name: str) -> List[str]:
        """
        Returns available skills for a class.
        """
        return CLASS_SKILLS.get(class_name, ["Perception", "Stealth"])

    def get_background_skills(self, background: str) -> List[str]:
        """
        Returns skill proficiencies granted by background.
        """
        return BACKGROUND_SKILLS.get(background, [])

    def get_background_feature(self, background: str) -> Optional[Dict[str, str]]:
        """
        Returns the background feature.
        """
        return BACKGROUND_FEATURES.get(background)

    def calculate_skill_modifier(self, skill: str, attributes: Dict[str, int], 
                                 proficiency: bool = False, proficiency_bonus: int = 2) -> int:
        """
        Calculates skill modifier based on attribute and proficiency.
        """
        # Skill to ability mapping
        skill_ability_map = {
            "Athletics": "STR",
            "Acrobatics": "DEX", "Sleight of Hand": "DEX", "Stealth": "DEX",
            "Arcana": "INT", "History": "INT", "Investigation": "INT", "Nature": "INT", "Religion": "INT",
            "Animal Handling": "WIS", "Insight": "WIS", "Medicine": "WIS", "Perception": "WIS", "Survival": "WIS",
            "Deception": "CHA", "Intimidation": "CHA", "Performance": "CHA", "Persuasion": "CHA",
        }
        
        ability = skill_ability_map.get(skill, "STR")
        ability_score = attributes.get(ability, 10)
        ability_modifier = (ability_score - 10) // 2
        
        if proficiency:
            return ability_modifier + proficiency_bonus
        return ability_modifier

    async def finalize_character_enhanced(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalizes character with all enhancements:
        - Applies racial bonuses
        - Loads spells for spellcasting classes
        - Calculates skill modifiers
        - Adds background features
        """
        race = data.get("race")
        class_name = data.get("class")
        background = data.get("background")
        attributes = data.get("attributes", {})
        
        # Apply racial bonuses
        enhanced_attributes = self.apply_racial_bonuses(race, attributes)
        
        # Recalculate modifiers with enhanced attributes
        modifiers = {k: (v - 10) // 2 for k, v in enhanced_attributes.items()}
        
        # Get skills (combine class and background)
        class_skill_list = self.get_class_skills(class_name)
        background_skill_list = self.get_background_skills(background)
        
        # Default skills if none specified (first 2 from class)
        selected_skills = data.get("selected_skills", class_skill_list[:2] if class_skill_list else ["Perception", "Stealth"])
        
        # Calculate skill modifiers
        skill_modifiers = {}
        for skill in selected_skills:
            skill_modifiers[skill] = self.calculate_skill_modifier(
                skill, enhanced_attributes, proficiency=True, proficiency_bonus=2
            )
        
        # Get spells for spellcasting classes
        spells = []
        if class_name in SPELLCASTING_CLASSES:
            spells = await self.get_spells_for_class(class_name, level=1)
        
        # Get background feature
        background_feature = self.get_background_feature(background)
        
        # Build final character
        character = {
            "name": data.get("name"),
            "race": race,
            "class": class_name,
            "background": background,
            "level": 1,
            "attributes": enhanced_attributes,
            "modifiers": modifiers,
            "skills": selected_skills,
            "skill_modifiers": skill_modifiers,
            "spells": spells,
            "spell_slots": self._get_spell_slots(class_name, 1),
            "background_feature": background_feature,
            "proficiency_bonus": 2,  # Level 1 proficiency bonus
        }
        
        logger.info(f"[EnhancedBuilder] Finalized character {character['name']} with enhancements")
        return character

    def _get_spell_slots(self, class_name: str, level: int) -> Dict[str, int]:
        """
        Returns spell slots for a class at a given level.
        """
        # Level 1 spell slots by class
        slots = {
            "Wizard": {"1st": 2},
            "Cleric": {"1st": 2},
            "Druid": {"1st": 2},
            "Sorcerer": {"1st": 2},
            "Warlock": {"1st": 1},  # Warlock uses Pact Magic
            "Bard": {"1st": 2},
            "Paladin": {"1st": 0},  # Paladins get spells at level 2
            "Ranger": {"1st": 0},   # Rangers get spells at level 2
        }
        return slots.get(class_name, {})
