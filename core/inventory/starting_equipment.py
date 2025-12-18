# sam-telegram-bot/core/inventory/starting_equipment.py
"""
Equipamiento inicial basado en clase y trasfondo segun SRD 5.2.1
Siempre incluye cuerda y antorcha para facilidad narrativa.
"""
from typing import Dict, List, Any


# Equipamiento base por clase
CLASS_EQUIPMENT: Dict[str, Dict[str, Any]] = {
    "Fighter": {
        "weapons": ["Espada larga", "Escudo"],
        "armor": "Cota de malla",
        "items": ["Kit de explorador"],
    },
    "Wizard": {
        "weapons": ["Baston arcano"],
        "armor": None,
        "items": ["Libro de hechizos", "Bolsa de componentes"],
    },
    "Rogue": {
        "weapons": ["Espada corta", "Daga", "Arco corto"],
        "armor": "Armadura de cuero",
        "items": ["Herramientas de ladron"],
    },
    "Cleric": {
        "weapons": ["Maza", "Escudo"],
        "armor": "Cota de escamas",
        "items": ["Simbolo sagrado"],
    },
    "Ranger": {
        "weapons": ["Arco largo", "2 espadas cortas"],
        "armor": "Armadura de cuero",
        "items": ["Kit de explorador"],
    },
    "Barbarian": {
        "weapons": ["Hacha grande", "2 hachas de mano"],
        "armor": None,
        "items": ["Kit de explorador"],
    },
    "Bard": {
        "weapons": ["Espada ropera", "Daga"],
        "armor": "Armadura de cuero",
        "items": ["Instrumento musical", "Kit de artista"],
    },
    "Paladin": {
        "weapons": ["Espada larga", "Escudo"],
        "armor": "Cota de malla",
        "items": ["Simbolo sagrado"],
    },
    "Monk": {
        "weapons": ["Espada corta"],
        "armor": None,
        "items": ["Kit de explorador"],
    },
    "Druid": {
        "weapons": ["Cimitarra", "Escudo de madera"],
        "armor": "Armadura de cuero",
        "items": ["Foco druidico"],
    },
    "Sorcerer": {
        "weapons": ["Ballesta ligera", "Daga"],
        "armor": None,
        "items": ["Bolsa de componentes"],
    },
    "Warlock": {
        "weapons": ["Ballesta ligera", "Daga"],
        "armor": "Armadura de cuero",
        "items": ["Foco arcano"],
    },
}

# Items adicionales por trasfondo
BACKGROUND_ITEMS: Dict[str, List[str]] = {
    "Acolyte": ["Simbolo sagrado", "Libro de oraciones", "5 varitas de incienso"],
    "Criminal": ["Palanca", "Ropa oscura con capucha"],
    "Folk Hero": ["Herramientas de artesano", "Pala"],
    "Noble": ["Sello de firma", "Pergamino con arbol genealogico", "Ropa fina"],
    "Sage": ["Tinta y pluma", "Cuchillo pequeno", "Carta de un colega"],
    "Soldier": ["Insignia de rango", "Trofeo de enemigo", "Juego de dados"],
    "Entertainer": ["Instrumento musical", "Traje de disfraz"],
    "Hermit": ["Caso de pergamino con notas", "Manta de invierno"],
    "Outlander": ["Baston", "Trampa de caza", "Trofeo de animal"],
    "Urchin": ["Cuchillo pequeno", "Mapa de la ciudad", "Raton mascota"],
    "Guild Artisan": ["Herramientas de artesano", "Carta de presentacion del gremio"],
    "Charlatan": ["Ropa fina", "Kit de disfraz", "Herramientas de falsificacion"],
}

# Items SIEMPRE incluidos
UNIVERSAL_ITEMS = ["Cuerda (50 pies)", "Antorcha (x5)"]


def get_starting_equipment(
    character_class: str,
    background: str = None,
    level: int = 1
) -> Dict[str, Any]:
    """
    Genera el equipamiento inicial para un personaje.
    """
    class_eq = CLASS_EQUIPMENT.get(character_class, CLASS_EQUIPMENT.get("Fighter"))
    
    equipment = {
        "weapons": class_eq.get("weapons", []).copy(),
        "armor": class_eq.get("armor"),
        "shield": "Escudo" if "Escudo" in class_eq.get("weapons", []) else None,
    }
    
    if "Escudo" in equipment["weapons"]:
        equipment["weapons"].remove("Escudo")
    
    inventory = class_eq.get("items", []).copy()
    
    if background and background in BACKGROUND_ITEMS:
        for item in BACKGROUND_ITEMS[background]:
            if item not in inventory:
                inventory.append(item)
    
    for universal_item in UNIVERSAL_ITEMS:
        if universal_item not in inventory:
            inventory.append(universal_item)
    
    inventory.append("Raciones (5 dias)")
    inventory.append("Odre de agua")
    
    gold = calculate_starting_gold(character_class, level)
    
    return {
        "equipment": equipment,
        "inventory": inventory,
        "gold": gold,
    }


def calculate_starting_gold(character_class: str, level: int = 1) -> int:
    """Calcula el oro inicial basado en clase."""
    base_gold = {
        "Fighter": 125, "Wizard": 100, "Rogue": 100, "Cleric": 125,
        "Ranger": 125, "Barbarian": 50, "Bard": 125, "Paladin": 125,
        "Monk": 25, "Druid": 50, "Sorcerer": 75, "Warlock": 100,
    }
    return base_gold.get(character_class, 100)


def format_inventory_display(player_data: Dict) -> str:
    """Formatea el inventario del jugador para mostrar en Telegram."""
    equipment = player_data.get("equipment", {})
    inventory = player_data.get("inventory", [])
    gold = player_data.get("gold", 0)
    
    lines = []
    lines.append("*Inventario*\n")
    
    lines.append("*Equipado:*")
    
    weapons = equipment.get("weapons", [])
    if weapons:
        lines.append(f"  Armas: {', '.join(weapons)}")
    
    armor = equipment.get("armor")
    if armor:
        lines.append(f"  Armadura: {armor}")
    
    shield = equipment.get("shield")
    if shield:
        lines.append(f"  Escudo: {shield}")
    
    if inventory:
        lines.append("\n*Objetos:*")
        for item in inventory:
            lines.append(f"  - {item}")
    
    lines.append(f"\n*Oro:* {gold} mo")
    
    return "\n".join(lines)
