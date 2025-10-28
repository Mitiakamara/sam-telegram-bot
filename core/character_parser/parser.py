import os
import re
import json
from typing import Dict, Any, Optional
from PyPDF2 import PdfReader


# ============================================================
# 🧠 DETECCIÓN DE FUENTE
# ============================================================

def detect_source(file_path: str) -> Dict[str, str]:
    """
    Detecta tipo de archivo y si parece provenir de SRD 5.1.2 o D&D 5e.
    """
    ext = os.path.splitext(file_path)[1].lower()
    ftype = "txt" if ext == ".txt" else "pdf" if ext == ".pdf" else "unknown"
    source = "unknown"

    # Heurística básica
    try:
        if ftype == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
        elif ftype == "pdf":
            reader = PdfReader(file_path)
            content = "\n".join([page.extract_text().lower() for page in reader.pages])
        else:
            return {"type": "unknown", "format": ftype}

        # Palabras clave para distinguir
        if "system reference document" in content or "srd" in content:
            source = "SRD"
        elif "dungeons & dragons" in content or "d&d" in content:
            source = "5e"
        else:
            source = "unknown"

    except Exception as e:
        print(f"[Parser] Error detectando fuente: {e}")

    return {"type": source, "format": ftype}


# ============================================================
# 🧩 EXTRACCIÓN DE DATOS
# ============================================================

def extract_character_data(file_path: str) -> Dict[str, Any]:
    """
    Extrae texto plano del archivo (PDF o TXT) y busca campos comunes de hoja de personaje.
    """
    data = {
        "name": "",
        "class": "",
        "level": "",
        "race": "",
        "background": "",
        "alignment": "",
        "abilities": {},
        "skills": {},
        "equipment": [],
        "spells": [],
        "features": [],
    }

    try:
        ext = os.path.splitext(file_path)[1].lower()
        text = ""

        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif ext == ".pdf":
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() for page in reader.pages])

        # Limpieza básica
        clean = re.sub(r"[^\x00-\x7F]+", " ", text)
        lines = clean.splitlines()

        # Extracción básica con regex
        for line in lines:
            lower = line.lower()

            if "name" in lower and not data["name"]:
                m = re.search(r"name[:\s]+([A-Za-z0-9' -]+)", line)
                if m:
                    data["name"] = m.group(1).strip()

            elif "class" in lower and not data["class"]:
                m = re.search(r"class[:\s]+([A-Za-z]+)", line)
                if m:
                    data["class"] = m.group(1).capitalize()

            elif "level" in lower and not data["level"]:
                m = re.search(r"level[:\s]+(\d+)", line)
                if m:
                    data["level"] = int(m.group(1))

            elif "race" in lower and not data["race"]:
                m = re.search(r"race[:\s]+([A-Za-z' -]+)", line)
                if m:
                    data["race"] = m.group(1).capitalize()

            elif "background" in lower and not data["background"]:
                m = re.search(r"background[:\s]+([A-Za-z' -]+)", line)
                if m:
                    data["background"] = m.group(1).capitalize()

            elif "alignment" in lower and not data["alignment"]:
                m = re.search(r"alignment[:\s]+([A-Za-z -]+)", line)
                if m:
                    data["alignment"] = m.group(1).title()

            # Habilidades básicas (STR, DEX, etc.)
            for abbr in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
                if abbr.lower() in lower and abbr not in data["abilities"]:
                    m = re.search(fr"{abbr}[:\s]+(\d+)", line, re.IGNORECASE)
                    if m:
                        data["abilities"][abbr] = int(m.group(1))

    except Exception as e:
        print(f"[Parser] Error extrayendo datos: {e}")

    return data


# ============================================================
# 🧩 NORMALIZACIÓN A SRD
# ============================================================

def normalize_to_srd(character_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte la información a un formato compatible con SRD 5.1.2.
    Descarta campos que no son SRD.
    """
    allowed_classes = [
        "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
        "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
    ]
    if character_dict.get("class") not in allowed_classes:
        character_dict["class"] = "Custom"  # marcador neutral

    return character_dict


# ============================================================
# 🧩 VALIDACIÓN Y GUARDADO
# ============================================================

def validate_character(character_dict: Dict[str, Any]) -> bool:
    """
    Revisa campos mínimos para considerar válido el personaje.
    """
    required = ["name", "class", "level", "abilities"]
    for r in required:
        if not character_dict.get(r):
            return False
    return True


def save_character(character_dict: Dict[str, Any], output_dir: str = "data/party") -> Optional[str]:
    """
    Guarda el personaje como JSON en /data/party.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{character_dict.get('name', 'unnamed')}.json"
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(character_dict, f, indent=2)
        return path
    except Exception as e:
        print(f"[Parser] Error guardando personaje: {e}")
        return None


# ============================================================
# 🧪 PROCESO COMPLETO
# ============================================================

def parse_character(file_path: str) -> Dict[str, Any]:
    """
    Orquesta todo el proceso: detecta, extrae, normaliza y valida.
    """
    result = {"success": False, "character": None, "message": ""}
    info = detect_source(file_path)
    data = extract_character_data(file_path)
    data = normalize_to_srd(data)

    if validate_character(data):
        result["success"] = True
        result["character"] = data
        result["message"] = f"Personaje '{data.get('name', 'Sin nombre')}' cargado correctamente ({info['type']} {info['format']})."
    else:
        result["message"] = f"No se pudo validar la hoja ({info['type']} {info['format']})."

    return result
