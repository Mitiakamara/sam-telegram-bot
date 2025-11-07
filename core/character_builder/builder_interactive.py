from typing import Dict, Any, List


class CharacterBuilderInteractive:
    """
    Builder guiado con pasos predefinidos y validaciones SRD básicas.
    """

    def __init__(self):
        self.steps = ["name", "race", "class", "background", "attributes", "confirm"]

        self.races = ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Tiefling", "Gnome"]
        self.classes = ["Fighter", "Wizard", "Cleric", "Rogue", "Paladin", "Bard", "Ranger"]
        self.backgrounds = ["Acolyte", "Soldier", "Noble", "Criminal", "Sage", "Folk Hero"]

    # -----------------------------------------------------
    #  PROMPTS
    # -----------------------------------------------------
    def get_prompt(self, step: str) -> str:
        prompts = {
            "name": "🧙‍♂️ ¿Cómo se llamará tu personaje?",
            "race": "🏹 Elige una raza:",
            "class": "⚔️ Elige una clase:",
            "background": "📜 Elige un trasfondo:",
            "attributes": (
                "💪 Asigna tus atributos (STR, DEX, CON, INT, WIS, CHA).\n"
                "Formato: `15 14 13 12 10 8`\n"
                "O deja vacío para usar el estándar."
            ),
            "confirm": "✅ ¿Confirmas la creación del personaje? (sí/no)",
        }
        return prompts.get(step, "")

    # -----------------------------------------------------
    #  BOTONES
    # -----------------------------------------------------
    def get_options(self, step: str) -> List[str]:
        if step == "race":
            return self.races
        elif step == "class":
            return self.classes
        elif step == "background":
            return self.backgrounds
        return []

    # -----------------------------------------------------
    #  VALIDACIÓN
    # -----------------------------------------------------
    def process_step(self, step: str, value: str, data: Dict[str, Any]) -> bool:
        """
        Retorna True si el valor es válido y se guarda en data.
        """
        value = value.strip()

        if step == "name":
            if not value or len(value) < 2:
                return False
            data["name"] = value
            return True

        if step == "race":
            if value not in self.races:
                return False
            data["race"] = value
            return True

        if step == "class":
            if value not in self.classes:
                return False
            data["class"] = value
            return True

        if step == "background":
            if value not in self.backgrounds:
                return False
            data["background"] = value
            return True

        if step == "attributes":
            if not value:
                # estándar
                data["attributes"] = {"STR": 15, "DEX": 14, "CON": 13, "INT": 12, "WIS": 10, "CHA": 8}
                data["modifiers"] = {"STR": 2, "DEX": 2, "CON": 1, "INT": 1, "WIS": 0, "CHA": -1}
                return True

            try:
                vals = list(map(int, value.split()))
                if len(vals) != 6 or any(v < 3 or v > 18 for v in vals):
                    return False
                stats = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
                data["attributes"] = dict(zip(stats, vals))
                data["modifiers"] = {k: (v - 10) // 2 for k, v in data["attributes"].items()}
                return True
            except Exception:
                return False

        if step == "confirm":
            return value.lower() in ["si", "sí", "yes", "y"]

        return False

    # -----------------------------------------------------
    #  FINALIZACIÓN
    # -----------------------------------------------------
    def finalize_character(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Devuelve el dict final del personaje."""
        return {
            "name": data.get("name"),
            "race": data.get("race"),
            "class": data.get("class"),
            "background": data.get("background"),
            "level": 1,
            "attributes": data.get("attributes"),
            "modifiers": data.get("modifiers"),
            "skills": ["Perception", "Stealth"],
            "spells": [],
        }
