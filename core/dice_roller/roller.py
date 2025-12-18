# sam-telegram-bot/core/dice_roller/roller.py
import random
import re
from typing import Optional, Tuple, List

def roll_dice(sides: int = 20) -> int:
    return random.randint(1, sides)


def roll_multiple(num_dice: int, sides: int) -> List[int]:
    return [roll_dice(sides) for _ in range(num_dice)]


def parse_dice_notation(notation: str) -> Optional[Tuple[int, int, int]]:
    pattern = r'(\d+)?d(\d+)([+-]\d+)?'
    match = re.search(pattern, notation.lower())
    
    if not match:
        return None
    
    num_dice = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    return (num_dice, sides, modifier)


def roll_from_notation(notation: str) -> Optional[dict]:
    parsed = parse_dice_notation(notation)
    if not parsed:
        return None
    
    num_dice, sides, modifier = parsed
    rolls = roll_multiple(num_dice, sides)
    total = sum(rolls) + modifier
    
    return {
        "notation": f"{num_dice}d{sides}" + (f"{modifier:+}" if modifier else ""),
        "rolls": rolls,
        "modifier": modifier,
        "total": total,
        "is_crit": sides == 20 and num_dice == 1 and rolls[0] == 20,
        "is_fumble": sides == 20 and num_dice == 1 and rolls[0] == 1,
    }


def ability_check(ability_name: str, ability_mod: int) -> dict:
    d20 = roll_dice(20)
    total = d20 + ability_mod
    return {
        "ability": ability_name.upper(),
        "d20": d20,
        "modifier": ability_mod,
        "total": total,
        "outcome": get_outcome(d20)
    }


def skill_check(skill_name: str, skill_mod: int, dc: int = None) -> dict:
    d20 = roll_dice(20)
    total = d20 + skill_mod
    
    result = {
        "skill": skill_name,
        "d20": d20,
        "modifier": skill_mod,
        "total": total,
        "outcome": get_outcome(d20),
    }
    
    if dc:
        result["dc"] = dc
        result["success"] = total >= dc
    
    return result


def get_outcome(d20_roll: int) -> str:
    if d20_roll == 20:
        return "critico_exito"
    if d20_roll == 1:
        return "critico_fallo"
    if d20_roll >= 15:
        return "exito"
    if d20_roll >= 10:
        return "exito_parcial"
    return "fallo"


def format_roll_result(result: dict, context: str = "") -> str:
    if "notation" in result:
        rolls_str = ", ".join(str(r) for r in result["rolls"])
        mod_str = f" {result['modifier']:+}" if result["modifier"] else ""
        
        if result.get("is_crit"):
            prefix = "CRITICO! "
        elif result.get("is_fumble"):
            prefix = "PIFIA! "
        else:
            prefix = ""
        
        msg = f"Tirada: {result['notation']}\n"
        msg += f"Dados: {rolls_str}\n"
        msg += f"Total: {result['total']}"
        
        if prefix:
            msg = prefix + msg
        
        return msg
    
    elif "skill" in result:
        msg = f"Tirada de {result['skill']}\n"
        msg += f"d20: {result['d20']} + mod: {result['modifier']:+} = {result['total']}"
        
        if result.get("dc"):
            success = "Exito!" if result["success"] else "Fallo"
            msg += f"\nCD {result['dc']}: {success}"
        
        return msg
    
    elif "ability" in result:
        msg = f"Tirada de {result['ability']}\n"
        msg += f"d20: {result['d20']} + {result['ability']}: {result['modifier']:+} = {result['total']}"
        
        return msg
    
    return "Tirada realizada"
