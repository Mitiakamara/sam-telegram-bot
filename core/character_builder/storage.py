# sam-telegram-bot/core/character_builder/storage.py
import os, json

def save_character(data, directory="data/party"):
    """Guarda el personaje como JSON."""
    os.makedirs(directory, exist_ok=True)
    name = data.get("name", "unnamed").replace("/", "_")
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path
