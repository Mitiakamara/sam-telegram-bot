# sam-telegram-bot/core/character_builder/validator.py

def validate_abilities(abilities: dict) -> bool:
    """Verifica que existan los seis atributos y sean enteros entre 1 y 20."""
    required = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    for a in required:
        if a not in abilities:
            return False
        try:
            val = int(abilities[a])
            if not 1 <= val <= 20:
                return False
        except Exception:
            return False
    return True
