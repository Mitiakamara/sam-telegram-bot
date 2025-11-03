# sam-telegram-bot/core/character_builder/loader.py
import os
import json
import logging

logger = logging.getLogger(__name__)

def load_party(directory="data/party"):
    """
    Carga todos los personajes creados desde /data/party/.
    Retorna una lista de diccionarios con la información de cada personaje.
    """
    party = []

    if not os.path.exists(directory):
        logger.warning(f"[Party Loader] No existe el directorio {directory}")
        return party

    for file in os.listdir(directory):
        if not file.endswith(".json"):
            continue

        path = os.path.join(directory, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Validación mínima
                if "name" in data and "class" in data:
                    party.append(data)
                else:
                    logger.warning(f"[Party Loader] Archivo {file} incompleto o inválido.")
        except Exception as e:
            logger.error(f"[Party Loader] Error al leer {file}: {e}")

    logger.info(f"[Party Loader] {len(party)} personajes cargados desde {directory}")
    return party
