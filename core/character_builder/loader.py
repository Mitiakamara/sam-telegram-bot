# sam-telegram-bot/core/character_builder/loader.py
import os, json

def load_party(directory="data/party"):
    """Carga todos los personajes creados desde /data/party"""
    party = []
    if not os.path.exists(directory):
        return party
    for file in os.listdir(directory):
        if file.endswith(".json"):
            path = os.path.join(directory, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    party.append(data)
            except Exception as e:
                print(f"[Party Loader] Error al leer {file}: {e}")
    return party
