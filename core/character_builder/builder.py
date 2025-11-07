from typing import Dict, Any


class CharacterBuilder:
    """
    Creador de personajes mínimo.
    La lógica real puede ir creciendo aquí.
    """

    def create_character(
        self,
        name: str,
        race: str = "Elf",
        cls: str = "Fighter",
    ) -> Dict[str, Any]:
        # atributos base como el ejemplo de tu log
        attributes = {
            "STR": 15,
            "DEX": 14,
            "CON": 13,
            "INT": 12,
            "WIS": 10,
            "CHA": 8,
        }
        modifiers = {
            "STR": 2,
            "DEX": 2,
            "CON": 1,
            "INT": 1,
            "WIS": 0,
            "CHA": -1,
        }

        return {
            "name": name,
            "race": race,
            "class": cls,
            "level": 1,
            "attributes": attributes,
            "modifiers": modifiers,
            "skills": ["Stealth", "Sleight of Hand", "Religion"],
            "spells": [],
        }
