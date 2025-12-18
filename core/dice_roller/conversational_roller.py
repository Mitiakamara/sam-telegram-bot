# sam-telegram-bot/core/dice_roller/conversational_roller.py
import re
import logging
from typing import Optional, Dict, Any
from .roller import roll_from_notation, skill_check, ability_check, format_roll_result
from .intent_mapper import detect_attribute_from_text

logger = logging.getLogger(__name__)

SKILL_MAP = {
    'acrobatics': 'Acrobatics', 'acrobacias': 'Acrobatics',
    'percepcion': 'Perception', 'perception': 'Perception',
    'animal handling': 'Animal Handling', 'trato con animales': 'Animal Handling',
    'arcana': 'Arcana', 'arcano': 'Arcana',
    'athletics': 'Athletics', 'atletismo': 'Athletics',
    'deception': 'Deception', 'engano': 'Deception',
    'history': 'History', 'historia': 'History',
    'insight': 'Insight', 'perspicacia': 'Insight',
    'intimidation': 'Intimidation', 'intimidacion': 'Intimidation',
    'investigation': 'Investigation', 'investigacion': 'Investigation',
    'medicine': 'Medicine', 'medicina': 'Medicine',
    'nature': 'Nature', 'naturaleza': 'Nature',
    'perception': 'Perception', 'percepcion': 'Perception',
    'performance': 'Performance', 'interpretacion': 'Performance',
    'persuasion': 'Persuasion',
    'religion': 'Religion',
    'sleight of hand': 'Sleight of Hand', 'juego de manos': 'Sleight of Hand',
    'stealth': 'Stealth', 'sigilo': 'Stealth',
    'survival': 'Survival', 'supervivencia': 'Survival',
}

ATTRIBUTE_MAP = {
    'fuerza': 'STR', 'str': 'STR', 'strength': 'STR',
    'destreza': 'DEX', 'dex': 'DEX', 'dexterity': 'DEX',
    'constitucion': 'CON', 'con': 'CON', 'constitution': 'CON',
    'inteligencia': 'INT', 'int': 'INT', 'intelligence': 'INT',
    'sabiduria': 'WIS', 'wis': 'WIS', 'wisdom': 'WIS',
    'carisma': 'CHA', 'cha': 'CHA', 'charisma': 'CHA',
}

ROLL_CONTEXTS = {
    'iniciativa': ('initiative', 'DEX'),
    'initiative': ('initiative', 'DEX'),
    'ataque': ('attack', None),
    'attack': ('attack', None),
}


class ConversationalRoller:
    DICE_NOTATION_PATTERN = r'\b(\d*d\d+(?:[+-]\d+)?)\b'
    
    ROLL_TRIGGER_PATTERNS = [
        r'(?:lanzo|tiro|hago|realizo)\s+(?:un(?:a)?\s+)?(?:tirada\s+(?:de\s+)?)?(.+)',
        r'(?:tirada|roleo|roll)\s+(?:de\s+)?(.+)',
        r'(?:prueba|chequeo|check)\s+(?:de\s+)?(.+)',
    ]
    
    def __init__(self, campaign_manager):
        self.campaign_manager = campaign_manager
    
    def detect_roll_intent(self, text):
        text_lower = text.lower().strip()
        dice_match = re.search(self.DICE_NOTATION_PATTERN, text_lower)
        if dice_match:
            notation = dice_match.group(1)
            context = self._extract_roll_context(text_lower)
            skill = self._extract_skill_from_text(text_lower)
            attr = self._extract_attribute_from_text(text_lower)
            return {'type': 'explicit', 'notation': notation, 'context': context, 'skill': skill, 'attribute': attr}
        for pattern in self.ROLL_TRIGGER_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                roll_target = match.group(1).strip()
                return self._parse_roll_target(roll_target)
        return None
    
    def _extract_roll_context(self, text):
        for keyword, (context, _) in ROLL_CONTEXTS.items():
            if keyword in text:
                return context
        return None
    
    def _extract_skill_from_text(self, text):
        # Normalizar tildes
        import unicodedata
        text_norm = unicodedata.normalize('NFD', text)
        text_norm = ''.join(c for c in text_norm if unicodedata.category(c) != 'Mn')
        
        for skill_key, skill_name in SKILL_MAP.items():
            if skill_key in text or skill_key in text_norm:
                return skill_name
        return None
    
    def _extract_attribute_from_text(self, text):
        for attr_key, attr_code in ATTRIBUTE_MAP.items():
            if attr_key in text:
                return attr_code
        return None
    
    def _parse_roll_target(self, target):
        target_lower = target.lower().strip()
        dice_match = re.search(self.DICE_NOTATION_PATTERN, target_lower)
        if dice_match:
            return {'type': 'explicit', 'notation': dice_match.group(1), 'context': self._extract_roll_context(target_lower), 'skill': self._extract_skill_from_text(target_lower), 'attribute': self._extract_attribute_from_text(target_lower)}
        for keyword, (context, default_attr) in ROLL_CONTEXTS.items():
            if keyword in target_lower:
                return {'type': 'context', 'context': context, 'attribute': default_attr}
        for skill_key, skill_name in SKILL_MAP.items():
            if skill_key in target_lower:
                return {'type': 'skill', 'skill': skill_name}
        for attr_key, attr_code in ATTRIBUTE_MAP.items():
            if attr_key in target_lower:
                return {'type': 'attribute', 'attribute': attr_code}
        detected_attr = detect_attribute_from_text(target)
        if detected_attr:
            return {'type': 'attribute', 'attribute': detected_attr, 'inferred': True}
        return None
    
    def process_roll(self, player_id, roll_intent, original_text=''):
        player = self.campaign_manager.get_player_by_telegram_id(player_id)
        player_name = player.get('name', 'Aventurero') if player else 'Aventurero'
        roll_type = roll_intent.get('type')
        
        if roll_type == 'explicit':
            notation = roll_intent.get('notation', '1d20')
            result = roll_from_notation(notation)
            if result:
                context = roll_intent.get('context', '')
                skill = roll_intent.get('skill')
                attr = roll_intent.get('attribute')
                modifier = 0
                if skill:
                    modifier = self._get_skill_modifier(player, skill)
                elif attr:
                    modifier = self._get_attribute_modifier(player, attr)
                context_text = f' para {context}' if context else ''
                if skill and not context:
                    context_text = f' de {skill}'
                total_with_mod = result.get('total', 0) + modifier
                message = f'Tirada de {player_name}: {result["notation"]}{context_text}\n\n'
                message += format_roll_result(result)
                if modifier != 0:
                    sign = '+' if modifier >= 0 else ''
                    message += f'\nModificador: {sign}{modifier}'
                    message += f'\n*Total final: {total_with_mod}*'
                return {'success': True, 'message': message, 'result': result, 'modifier': modifier, 'total_with_modifier': total_with_mod}
            else:
                return {'success': False, 'message': 'No pude entender la notacion de dados.'}
        
        elif roll_type == 'skill':
            skill_name = roll_intent.get('skill')
            modifier = self._get_skill_modifier(player, skill_name)
            result = skill_check(skill_name, modifier)
            message = f'Tirada de {player_name}: prueba de {skill_name}\n\n'
            message += format_roll_result(result)
            return {'success': True, 'message': message, 'result': result}
        
        elif roll_type == 'attribute':
            attr = roll_intent.get('attribute', 'STR')
            modifier = self._get_attribute_modifier(player, attr)
            result = ability_check(attr, modifier)
            attr_names = {'STR': 'Fuerza', 'DEX': 'Destreza', 'CON': 'Constitucion', 'INT': 'Inteligencia', 'WIS': 'Sabiduria', 'CHA': 'Carisma'}
            attr_name = attr_names.get(attr, attr)
            message = f'Tirada de {player_name}: prueba de {attr_name}\n\n'
            message += format_roll_result(result)
            if roll_intent.get('inferred'):
                message += '\n_(Atributo inferido del contexto)_'
            return {'success': True, 'message': message, 'result': result}
        
        elif roll_type == 'context':
            context = roll_intent.get('context')
            if context == 'initiative':
                modifier = self._get_attribute_modifier(player, 'DEX')
                result = ability_check('Iniciativa', modifier)
                message = f'Iniciativa de {player_name}!\n\n'
                message += format_roll_result(result)
                return {'success': True, 'message': message, 'result': result}
            elif context == 'attack':
                modifier = self._get_attribute_modifier(player, 'STR')
                result = ability_check('Ataque', modifier)
                message = f'Ataque de {player_name}!\n\n'
                message += format_roll_result(result)
                return {'success': True, 'message': message, 'result': result}
        
        return {'success': False, 'message': 'No pude determinar que tirada realizar.'}
    
    def _get_skill_modifier(self, player, skill_name):
        if not player:
            return 0
        skills = player.get('skills', [])
        has_proficiency = skill_name in skills
        skill_attrs = {'Acrobatics': 'DEX', 'Animal Handling': 'WIS', 'Arcana': 'INT', 'Athletics': 'STR', 'Deception': 'CHA', 'History': 'INT', 'Insight': 'WIS', 'Intimidation': 'CHA', 'Investigation': 'INT', 'Medicine': 'WIS', 'Nature': 'INT', 'Perception': 'WIS', 'Performance': 'CHA', 'Persuasion': 'CHA', 'Religion': 'INT', 'Sleight of Hand': 'DEX', 'Stealth': 'DEX', 'Survival': 'WIS'}
        attr = skill_attrs.get(skill_name, 'STR')
        base_mod = self._get_attribute_modifier(player, attr)
        if has_proficiency:
            level = player.get('level', 1)
            prof_bonus = 2 + (level - 1) // 4
            return base_mod + prof_bonus
        return base_mod
    
    def _get_attribute_modifier(self, player, attr):
        if not player:
            return 0
        attributes = player.get('attributes', {})
        score = attributes.get(attr, 10)
        return (score - 10) // 2
