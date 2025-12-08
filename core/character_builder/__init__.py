# CharacterBuilder is now in builder_interactive.py and enhanced_builder.py
# This module exports the interactive builder for backwards compatibility
from .builder_interactive import CharacterBuilderInteractive

# For StoryDirector compatibility, create a simple wrapper
class CharacterBuilder:
    """
    Compatibility wrapper for StoryDirector.
    Note: This is a minimal implementation. 
    For full character creation, use CharacterBuilderInteractive via /createcharacter command.
    """
    def create_character(self, name: str) -> dict:
        """Creates a basic character with default stats."""
        return {
            "name": name,
            "race": "Human",
            "class": "Fighter",
            "background": "Soldier",
            "level": 1,
            "attributes": {"STR": 15, "DEX": 14, "CON": 13, "INT": 12, "WIS": 10, "CHA": 8},
            "modifiers": {"STR": 2, "DEX": 2, "CON": 1, "INT": 1, "WIS": 0, "CHA": -1},
            "skills": ["Perception", "Stealth"],
            "spells": [],
        }

__all__ = ["CharacterBuilder", "CharacterBuilderInteractive"]
