# sam-telegram-bot/core/dice_roller/roller.py
import random
import math

def roll_dice(sides=20):
    """Devuelve un número aleatorio entre 1 y 'sides'."""
    return random.randint(1, sides)

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

def get_outcome(d20_roll: int) -> str:
    """Devuelve un texto según el resultado del dado (no total)."""
    if d20_roll == 20:
        return "✨ Crítico (éxito sobresaliente)"
    if d20_roll == 1:
        return "💀 Fallo crítico"
    if d20_roll >= 15:
        return "✅ Éxito claro"
    if d20_roll >= 10:
        return "⚖️ Éxito moderado"
    return "❌ Fallo"
