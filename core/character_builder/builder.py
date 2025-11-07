from typing import Dict, Any, Optional


class CharacterBuilder:
    """
    Creador de personajes guiado paso a paso.
    Gestiona los prompts y validaciones de la creación de personaje.
    """

    def __init__(self):
        self.steps = ["name", "race", "cls", "background", "attributes", "confirm"]

        self.available_races = [
            "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Tiefling", "Gnome"
        ]
        self.available_classes = [
            "Fighter", "Wizard", "Cleric", "Rogue", "Paladin", "Bard", "Ranger"
        ]
        self.available_backgrounds = [
            "Acolyte", "Soldier", "Noble", "Criminal", "Sage", "Folk Hero"
        ]

    # ===================== PROMPTS =====================
    def get_prompt_for_step(self, step: str) -> str:
        if step == "name":
            return "🧙‍♂️ ¿Cómo se llamará tu personaje?"
        elif step == "race":
            return f"🏹 Elige una raza ({', '.join(self.available_races)}):"
        elif step == "cls":
            return f"⚔️ Elige una clase ({', '.join(self.available_classes)}):"
        elif step == "background":
            return f"📜 Elige un trasfondo ({', '.join(self.available_backgrounds)}):"
        elif step == "attributes":
            return (
                "💪 Asigna tus atributos (STR, DEX, CON, INT, WIS, CHA).\n"
                "Formato: `15 14 13 12 10 8`\n"
                "O deja vacío para usar el estándar."
            )
        elif step == "confirm":
            return "✅ ¿Confirmas la creación del personaje? (sí/no)"
        else:
            return ""

    def get_next_step(self, current_step: str) -> Optional[str]:
        idx = self.steps.index(current_step)
        return self.steps[idx + 1] if idx + 1 < len(self.steps) else None

    # ===================== VALIDACIONES =====================
    def process_step(self, step: str, value: str, data: Dict[str, Any]) -> Dict[str, Any]:
        value = value.strip()

        if step == "name":
            data["name"] = value

        elif step == "race":
            if value.title() not in self.available_races:
                raise ValueError("Raza no válida.")
            data["race"] = value.title()

        elif step == "cls":
            if value.title() not in self.available_classes:
                raise ValueError("Clase no válida.")
            data["class"] = value.title()

        elif step == "background":
            if value.title() not in self.available_backgrounds:
                raise ValueError("Trasfondo no válido.")
            data["background"] = value.title()

        elif step == "attributes":
            if value:
                try:
                    nums = [int(x) for x in value.split()]
                    if len(nums) != 6:
                        raise ValueError
                    data["attributes"] = dict(zip(["STR", "DEX", "CON", "INT", "WIS", "CHA"], nums))
                except Exception:
                    raise ValueError("Formato incorrecto. Escribe 6 números separados por espacios.")
            else:
                data["attributes"] = {"STR": 15, "DEX": 14, "CON": 13, "INT": 12, "WIS": 10, "CHA": 8}

        elif step == "confirm":
            if value.lower() not in ["sí", "si", "yes", "y"]:
                raise ValueError("Creación cancelada.")

        return data

    # ===================== RESULTADO FINAL =====================
    def finalize_character(self, data: Dict[str, Any]) -> Dict[str, Any]:
        attributes = data.get("attributes", {})
        modifiers = {k: (v - 10) // 2 for k, v in attributes.items()}

        return {
            "name": data.get("name"),
            "race": data.get("race"),
            "class": data.get("class"),
            "background": data.get("background"),
            "level": 1,
            "attributes": attributes,
            "modifiers": modifiers,
            "skills": ["Perception", "Stealth"],
            "spells": [],
        }
