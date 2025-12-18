# sam-telegram-bot/core/dice_roller/roller.py
import random
import re
from typing import Optional, Tuple, List

def roll_dice(sides: int = 20) -> int:
    """Devuelve un numero aleatorio entre 1 y 'sides'."""
    return random.randint(1, sides)


def roll_multiple(num_dice: int, sides: int) -> List[int]:
    """Tira multiples dados y devuelve lista de resultados."""
    return [roll_dice(sides) for _ in range(num_dice)]


def parse_dice_notation(notation: str) -> Optional[Tuple[int, int, int]]:
    """
    Parsea notacion de dados como "1d20", "2d6+3", "1d8-1".
    Retorna (num_dados, caras, modificador) o None si no es valido.
    """
    pattern = r'(\d+)?d(\d+)([+-]\d+)?'
    match = re.search(pattern, notation.lower())
    
    if not match:
        return None
    
    num_dice = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    return (num_dice, sides, modifier)


def roll_from_notation(notation: str) -> Optional[dict]:
    """
    Ejecuta una tirada desde notacion como "2d6+3".
    Retorna dict con resultados detallados.
    """
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
    """Realiza una tirada d20 + modificador."""
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
    """Realiza una tirada de habilidad d20 + modificador."""
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
    """Devuelve un texto segun el resultado del dado (no total)."""
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
    """Formatea el resultado de una tirada para mostrar al usuario."""
    if "notation" in result:
        rolls_str = ", ".join(str(r) for r in result["rolls"])
        mod_str = f" {result['modifier']:+}" if result["modifier"] else ""
        
        emoji = "ðŸŽ²"
        if result.get("is_crit"):
            emoji = "âœ¨"
        elif result.get("is_fumble"):
            emoji = "ðŸ’€"
        
        msg = f"{emoji} *Tirada: {result['notation']}*\n"
        msg += f"Dados: [{rolls_str}]{mod_str}\n"
        msg += f"*Total: {result['total']}*"
        
        if result.get("is_crit"):
            msg += "\n_CRITICO!_"
        elif result.get("is_fumble"):
            msg += "\n_Pifia!_"
        
        return msg
    
    elif "skill" in result:
        emoji = "âœ¨" if result["outcome"] == "critico_exito" else "ðŸ’€" if result["outcome"] == "critico_fallo" else "ðŸŽ²"
        
        msg = f"{emoji} *Tirada de {result['skill']}*\n"
        msg += f"d20 ({result['d20']}) + modificador ({result['modifier']:+}) = *{result['total']}*"
        
        if result.get("dc"):
            success_emoji = "âœ…" if result["success"] else "âŒ"
            msg += f"\nCD {result['dc']}: {success_emoji}"
        
        return msg
    
    elif "ability" in result:
        emoji = "âœ¨" if result["outcome"] == "critico_exito" else "ðŸ’€" if result["outcome"] == "critico_fallo" else "ðŸŽ²"
        
        msg = f"{emoji} *Tirada de {result['ability']}*\n"
        msg += f"d20 ({result['d20']}) + {result['ability']} ({result['modifier']:+}) = *{result['total']}*"
        
        return msg
    
    return "ðŸŽ² Tirada realizada"
