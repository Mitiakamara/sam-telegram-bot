# sam-telegram-bot/core/dice_roller/parser.py
from core.dice_roller.roller import ability_check
import json, os

def find_character(name: str, directory="data/party"):
    """Busca el archivo del personaje y devuelve sus datos."""
    path = os.path.join(directory, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_ability(word: str) -> str:
    """Traduce términos comunes a códigos SRD."""
    mapping = {
        "str": "STR", "strength": "STR", "fuerza": "STR",
        "dex": "DEX", "dexterity": "DEX", "destreza": "DEX",
        "con": "CON", "constitution": "CON", "constitución": "CON",
        "int": "INT", "intelligence": "INT", "inteligencia": "INT",
        "wis": "WIS", "wisdom": "WIS", "sabiduría": "WIS",
        "cha": "CHA", "charisma": "CHA", "carisma": "CHA",
    }
    word = word.lower().strip()
    return mapping.get(word)

def perform_roll(player_name: str, ability_word: str):
    """Ejecuta una tirada con base en el personaje y atributo."""
    char_data = find_character(player_name)
    if not char_data:
        return f"⚠️ No encontré la ficha de {player_name}. Usa /createcharacter primero."

    ab_code = normalize_ability(ability_word)
    if not ab_code:
        return "❓ No entiendo qué atributo quieres usar. Usa STR, DEX, CON, INT, WIS o CHA."

    mods = char_data.get("modifiers", {})
    mod_value = mods.get(ab_code, 0)
    result = ability_check(ab_code, mod_value)

    msg = (
        f"🎲 *{char_data['name']} lanza una prueba de {ab_code}:*\n"
        f"`d20 ({result['d20']}) + {ab_code}({mod_value:+}) = {result['total']}`\n"
        f"➡️ {result['outcome']}"
    )
    return msg
