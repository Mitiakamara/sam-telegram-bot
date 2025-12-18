# sam-telegram-bot/core/dice_roller/conversational_roller.py
"""
Sistema de dados conversacional.
Detecta patrones como "lanzo 1d20", "tiro percepcion", "hago una tirada de fuerza".
"""
import re
import logging
from typing import Optional, Dict, Any, Tuple
from .roller import roll_from_notation, skill_check, ability_check, format_roll_result
from .intent_mapper import detect_attribute_from_text

logger = logging.getLogger(__name__)


# Mapeo de habilidades en espanol a ingles
SKILL_MAP = {
    # Espanol -> Ingles (para buscar en character data)
    "acrobatics": "Acrobatics", "acrobacias": "Acrobatics",
    "animal handling": "Animal Handling", "trato con animales": "Animal Handling",
    "arcana": "Arcana", "arcano": "Arcana",
    "athletics": "Athletics", "atletismo": "Athletics",
    "deception": "Deception", "engano": "Deception",
    "history": "History", "historia": "History",
    "insight": "Insight", "perspicacia": "Insight",
    "intimidation": "Intimidation", "intimidacion": "Intimidation",
    "investigation": "Investigation", "investigacion": "Investigation",
    "medicine": "Medicine", "medicina": "Medicine",
    "nature": "Nature", "naturaleza": "Nature",
    "perception": "Perception", "percepcion": "Perception",
    "performance": "Performance", "interpretacion": "Performance", "actuacion": "Performance",
    "persuasion": "Persuasion", "persuasion": "Persuasion",
    "religion": "Religion", "religion": "Religion",
    "sleight of hand": "Sleight of Hand", "juego de manos": "Sleight of Hand",
    "stealth": "Stealth", "sigilo": "Stealth",
    "survival": "Survival", "supervivencia": "Survival",
}

# Mapeo de atributos
ATTRIBUTE_MAP = {
    "fuerza": "STR", "str": "STR", "strength": "STR",
    "destreza": "DEX", "dex": "DEX", "dexterity": "DEX",
    "constitucion": "CON", "con": "CON", "constitution": "CON",
    "inteligencia": "INT", "int": "INT", "intelligence": "INT",
    "sabiduria": "WIS", "wis": "WIS", "wisdom": "WIS",
    "carisma": "CHA", "cha": "CHA", "charisma": "CHA",
}

# Contextos especiales que sugieren tiradas
ROLL_CONTEXTS = {
    "iniciativa": ("initiative", "DEX"),
    "initiative": ("initiative", "DEX"),
    "ataque": ("attack", None),
    "attack": ("attack", None),
    "dano": ("damage", None),
    "damage": ("damage", None),
    "salvacion": ("saving_throw", None),
    "saving throw": ("saving_throw", None),
}


class ConversationalRoller:
    """Detecta y procesa tiradas de dados en lenguaje natural."""
    
    # Patrones para detectar tiradas
    DICE_NOTATION_PATTERN = r'\b(\d*d\d+(?:[+-]\d+)?)\b'
    
    ROLL_TRIGGER_PATTERNS = [
        r"(?:lanzo|tiro|hago|realizo)\s+(?:un(?:a)?\s+)?(?:tirada\s+(?:de\s+)?)?(.+)",
        r"(?:tirada|roleo|roll)\s+(?:de\s+)?(.+)",
        r"(?:prueba|chequeo|check)\s+(?:de\s+)?(.+)",
    ]
    
    def __init__(self, campaign_manager):
        self.campaign_manager = campaign_manager
    
    def detect_roll_intent(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Detecta si el texto contiene una intencion de tirada.
        
        Returns:
            Dict con tipo de tirada y parametros, o None si no es una tirada.
        """
        text_lower = text.lower().strip()
        
        # 1. Buscar notacion de dados explicita (1d20, 2d6+3, etc)
        dice_match = re.search(self.DICE_NOTATION_PATTERN, text_lower)
        if dice_match:
            notation = dice_match.group(1)
            # Buscar contexto adicional
            context = self._extract_roll_context(text_lower)
            return {
                "type": "explicit",
                "notation": notation,
                "context": context,
            }
        
        # 2. Buscar patrones conversacionales
        for pattern in self.ROLL_TRIGGER_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                roll_target = match.group(1).strip()
                return self._parse_roll_target(roll_target)
        
        return None
    
    def _extract_roll_context(self, text: str) -> Optional[str]:
        """Extrae el contexto de la tirada (iniciativa, ataque, etc)."""
        for keyword, (context, _) in ROLL_CONTEXTS.items():
            if keyword in text:
                return context
        return None
    
    def _parse_roll_target(self, target: str) -> Optional[Dict[str, Any]]:
        """Parsea el objetivo de la tirada (habilidad, atributo, etc)."""
        target_lower = target.lower().strip()
        
        # Buscar notacion de dados en el target
        dice_match = re.search(self.DICE_NOTATION_PATTERN, target_lower)
        if dice_match:
            return {
                "type": "explicit",
                "notation": dice_match.group(1),
                "context": self._extract_roll_context(target_lower),
            }
        
        # Buscar contextos especiales
        for keyword, (context, default_attr) in ROLL_CONTEXTS.items():
            if keyword in target_lower:
                return {
                    "type": "context",
                    "context": context,
                    "attribute": default_attr,
                }
        
        # Buscar habilidad
        for skill_key, skill_name in SKILL_MAP.items():
            if skill_key in target_lower:
                return {
                    "type": "skill",
                    "skill": skill_name,
                }
        
        # Buscar atributo
        for attr_key, attr_code in ATTRIBUTE_MAP.items():
            if attr_key in target_lower:
                return {
                    "type": "attribute",
                    "attribute": attr_code,
                }
        
        # Intentar detectar atributo por contexto semantico
        detected_attr = detect_attribute_from_text(target)
        if detected_attr:
            return {
                "type": "attribute",
                "attribute": detected_attr,
                "inferred": True,
            }
        
        return None
    
    def process_roll(
        self, 
        player_id: int, 
        roll_intent: Dict[str, Any],
        original_text: str = ""
    ) -> Dict[str, Any]:
        """
        Procesa una tirada de dados.
        
        Returns:
            Dict con resultado de la tirada y mensaje formateado.
        """
        player = self.campaign_manager.get_player_by_telegram_id(player_id)
        player_name = player.get("name", "Aventurero") if player else "Aventurero"
        
        roll_type = roll_intent.get("type")
        
        if roll_type == "explicit":
            # Tirada con notacion explicita (1d20, 2d6+3)
            notation = roll_intent.get("notation", "1d20")
            result = roll_from_notation(notation)
            
            if result:
                context = roll_intent.get("context", "")
                context_text = f" para {context}" if context else ""
                
                message = f"ðŸŽ² *{player_name}* lanza {result['notation']}{context_text}\n\n"
                message += format_roll_result(result)
                
                return {
                    "success": True,
                    "message": message,
                    "result": result,
                }
            else:
                return {
                    "success": False,
                    "message": "No pude entender la notacion de dados.",
                }
        
        elif roll_type == "skill":
            # Tirada de habilidad
            skill_name = roll_intent.get("skill")
            modifier = self._get_skill_modifier(player, skill_name)
            result = skill_check(skill_name, modifier)
            
            message = f"ðŸŽ² *{player_name}* hace una prueba de {skill_name}\n\n"
            message += format_roll_result(result)
            
            return {
                "success": True,
                "message": message,
                "result": result,
            }
        
        elif roll_type == "attribute":
            # Tirada de atributo
            attr = roll_intent.get("attribute", "STR")
            modifier = self._get_attribute_modifier(player, attr)
            result = ability_check(attr, modifier)
            
            attr_names = {"STR": "Fuerza", "DEX": "Destreza", "CON": "Constitucion", 
                         "INT": "Inteligencia", "WIS": "Sabiduria", "CHA": "Carisma"}
            attr_name = attr_names.get(attr, attr)
            
            message = f"ðŸŽ² *{player_name}* hace una prueba de {attr_name}\n\n"
            message += format_roll_result(result)
            
            if roll_intent.get("inferred"):
                message += f"\n_(Atributo inferido del contexto)_"
            
            return {
                "success": True,
                "message": message,
                "result": result,
            }
        
        elif roll_type == "context":
            # Tirada contextual (iniciativa, ataque)
            context = roll_intent.get("context")
            attr = roll_intent.get("attribute")
            
            if context == "initiative":
                modifier = self._get_attribute_modifier(player, "DEX")
                result = ability_check("Iniciativa", modifier)
                
                message = f"âš”ï¸ *{player_name}* lanza iniciativa!\n\n"
                message += format_roll_result(result)
                
                return {
                    "success": True,
                    "message": message,
                    "result": result,
                }
            elif context == "attack":
                # Tirada de ataque generica
                modifier = self._get_attribute_modifier(player, "STR")
                result = ability_check("Ataque", modifier)
                
                message = f"âš”ï¸ *{player_name}* realiza un ataque!\n\n"
                message += format_roll_result(result)
                
                return {
                    "success": True,
                    "message": message,
                    "result": result,
                }
        
        return {
            "success": False,
            "message": "No pude determinar que tirada realizar.",
        }
    
    def _get_skill_modifier(self, player: Dict, skill_name: str) -> int:
        """Obtiene el modificador de habilidad del jugador."""
        if not player:
            return 0
        
        # Verificar si tiene proficiencia
        skills = player.get("skills", [])
        has_proficiency = skill_name in skills
        
        # Obtener atributo asociado a la habilidad
        skill_attrs = {
            "Acrobatics": "DEX", "Animal Handling": "WIS", "Arcana": "INT",
            "Athletics": "STR", "Deception": "CHA", "History": "INT",
            "Insight": "WIS", "Intimidation": "CHA", "Investigation": "INT",
            "Medicine": "WIS", "Nature": "INT", "Perception": "WIS",
            "Performance": "CHA", "Persuasion": "CHA", "Religion": "INT",
            "Sleight of Hand": "DEX", "Stealth": "DEX", "Survival": "WIS",
        }
        
        attr = skill_attrs.get(skill_name, "STR")
        base_mod = self._get_attribute_modifier(player, attr)
        
        # Agregar proficiencia si la tiene
        if has_proficiency:
            level = player.get("level", 1)
            prof_bonus = 2 + (level - 1) // 4
            return base_mod + prof_bonus
        
        return base_mod
    
    def _get_attribute_modifier(self, player: Dict, attr: str) -> int:
        """Obtiene el modificador de atributo del jugador."""
        if not player:
            return 0
        
        attributes = player.get("attributes", {})
        score = attributes.get(attr, 10)
        return (score - 10) // 2
