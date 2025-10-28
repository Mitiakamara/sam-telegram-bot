# sam-telegram-bot/core/dice_roller/parser.py
from core.dice_roller.roller import ability_check
from core.dice_roller.intent_mapper import detect_attribute_from_text
import json, os

def find_character(name: str, directory="data/party"):
    path = os.path.join(directory, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_ability(word: str) -> str:
    mapping = {
        "str": "STR", "strength": "STR", "fuerza": "STR",
        "dex": "DEX", "dexterity": "DEX", "destreza": "DEX",
        "con": "CON", "constitution": "CON", "constitución": "CON",
        "int": "INT", "intelligence": "INT", "inteligencia": "INT",
        "wis": "WIS", "wisdom": "WIS", "sabiduría": "WIS",
        "cha": "CHA", "charisma": "CHA", "carisma": "CHA",
    }
    return mapping.get(word.lower().strip())

def perform_roll(player_name: str, ability_word_or_text: str):
    """Ejecuta una tirada con base en el texto o el nombre del atributo."""
    char_data = find_character(player_name)
    if not char_data:
        return f"⚠️ No encontré la ficha de {player_name}. Usa /createcharacter primero."

    # Detectar si el input es una palabra o texto narrativo
    ab_code = normalize_ability(ability_word_or_text)
    if not ab_code:
        ab_code = detect_attribute_from_text(ability_word_or_text)
    if not ab_code:
        return "❓ No se entiende qué atributo usar. Ejemplo: 'forzar la puerta' → Fuerza."

    mods = char_data.get("modifiers", {})
    mod_value = mods.get(ab_code, 0)
    result = ability_check(ab_code, mod_value)

    msg = (
        f"🎲 *{char_data['name']} realiza una prueba de {ab_code}:*\n"
        f"`d20 ({result['d20']}) + {ab_code}({mod_value:+}) = {result['total']}`\n"
        f"➡️ {result['outcome']}"
    )
    return msg
