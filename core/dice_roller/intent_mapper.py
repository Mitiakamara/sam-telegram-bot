# sam-telegram-bot/core/dice_roller/intent_mapper.py
"""
Módulo que analiza texto narrativo y determina qué atributo (SRD) se usa.
"""
import re

def detect_attribute_from_text(text: str) -> str | None:
    """
    Recibe texto como 'intento convencer al guardia' y devuelve 'CHA', 'STR', etc.
    Retorna None si no se encuentra correspondencia.
    """
    t = text.lower().strip()

    # === Fuerza (STR) ===
    if any(w in t for w in ["empujar", "romper", "forzar", "levantar", "derribar", "golpear", "cargar"]):
        return "STR"

    # === Destreza (DEX) ===
    if any(w in t for w in ["saltar", "agacharse", "esquivar", "escalar", "moverse sigiloso", "sigilo", "robar", "lanzar"]):
        return "DEX"

    # === Constitución (CON) ===
    if any(w in t for w in ["aguantar", "resistir", "soportar", "envenenamiento", "fatiga", "frío", "cansancio"]):
        return "CON"

    # === Inteligencia (INT) ===
    if any(w in t for w in ["recordar", "analizar", "estudiar", "investigar", "examinar", "planear", "pensar"]):
        return "INT"

    # === Sabiduría (WIS) ===
    if any(w in t for w in ["percibir", "observar", "buscar", "detectar", "escuchar", "rastrear", "curar", "sentir"]):
        return "WIS"

    # === Carisma (CHA) ===
    if any(w in t for w in ["convencer", "persuadir", "engañar", "intimidar", "cantar", "hablar", "presentar", "actuar"]):
        return "CHA"

    return None
