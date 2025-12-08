from typing import Dict, Any, List
from core.character_builder.enhanced_builder import EnhancedCharacterBuilder

class CharacterBuilderInteractive:
    """
    Builder guiado con pasos predefinidos y validaciones SRD básicas.
    Now enhanced with SRD integration, racial bonuses, and skill selection.
    """

    def __init__(self):
        self.steps = ["name", "race", "class", "background", "attributes", "skills", "confirm"]
        self.enhanced_builder = EnhancedCharacterBuilder()

        self.races = ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Tiefling", "Gnome"]
        self.classes = ["Fighter", "Wizard", "Cleric", "Rogue", "Paladin", "Bard", "Ranger"]
        self.backgrounds = ["Acolyte", "Soldier", "Noble", "Criminal", "Sage", "Folk Hero"]

    # -----------------------------------------------------
    #  PROMPTS
    # -----------------------------------------------------
    def get_prompt(self, step: str, data: Dict[str, Any] = None) -> str:
        prompts = {
            "name": "🧙‍♂️ ¿Cómo se llamará tu personaje?",
            "race": "🏹 Elige una raza:",
            "class": "⚔️ Elige una clase:",
            "background": "📜 Elige un trasfondo:",
            "attributes": (
                "💪 Asigna tus atributos (STR, DEX, CON, INT, WIS, CHA).\n"
                "Formato: `15 14 13 12 10 8`\n"
                "O deja vacío para usar el estándar.\n"
                "⚠️ Nota: Los bonos raciales se aplicarán automáticamente."
            ),
            "skills": self._get_skills_prompt(data or {}),
            "confirm": "✅ ¿Confirmas la creación del personaje? (sí/no)",
        }
        return prompts.get(step, "")
    
    def _get_skills_prompt(self, data: Dict[str, Any]) -> str:
        """Genera el prompt de habilidades basado en clase y trasfondo."""
        class_name = data.get("class")
        background = data.get("background")
        
        if not class_name:
            return "📚 Selecciona tus habilidades (se mostrarán después de elegir clase):"
        
        class_skills = self.enhanced_builder.get_class_skills(class_name)
        background_skills = self.enhanced_builder.get_background_skills(background) if background else []
        
        # Combine and remove duplicates
        all_skills = list(set(class_skills + background_skills))
        
        # Determine how many skills to choose (typically 2 from class)
        num_skills = 2
        
        prompt = (
            f"📚 Selecciona {num_skills} habilidades de tu clase:\n"
            f"Opciones: {', '.join(class_skills[:10])}{'...' if len(class_skills) > 10 else ''}\n"
            f"Escribe los nombres separados por comas (ej: Perception, Stealth)\n"
            f"O deja vacío para usar las predeterminadas."
        )
        
        if background_skills:
            prompt += f"\n\n✨ Tu trasfondo ({background}) ya te da: {', '.join(background_skills)}"
        
        return prompt

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
                # Note: modifiers will be recalculated after racial bonuses
                return True

            try:
                vals = list(map(int, value.split()))
                if len(vals) != 6 or any(v < 3 or v > 18 for v in vals):
                    return False
                stats = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
                data["attributes"] = dict(zip(stats, vals))
                # Note: modifiers will be recalculated after racial bonuses
                return True
            except Exception:
                return False

        if step == "skills":
            class_name = data.get("class")
            if not class_name:
                return False
            
            if not value:
                # Use default: first 2 class skills
                class_skills = self.enhanced_builder.get_class_skills(class_name)
                data["selected_skills"] = class_skills[:2] if len(class_skills) >= 2 else class_skills
                return True
            
            # Parse comma-separated skills
            selected = [s.strip() for s in value.split(",")]
            class_skills = self.enhanced_builder.get_class_skills(class_name)
            
            # Validate all selected skills are in class list
            valid_skills = [s for s in selected if s in class_skills]
            if len(valid_skills) < 1:
                return False
            
            data["selected_skills"] = valid_skills[:4]  # Limit to 4 skills
            return True

        if step == "confirm":
            return value.lower() in ["si", "sí", "yes", "y"]

        return False

    # -----------------------------------------------------
    #  FINALIZACIÓN
    # -----------------------------------------------------
    async def finalize_character(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Devuelve el dict final del personaje con todas las mejoras:
        - Bonos raciales aplicados
        - Habilidades calculadas
        - Hechizos cargados (si aplica)
        - Características de trasfondo
        """
        # Use enhanced builder for finalization
        return await self.enhanced_builder.finalize_character_enhanced(data)
