import os
import json
from typing import Any, Dict, Optional
from core.utils.logger import safe_logger

logger = safe_logger(__name__)


class FileManager:
    """
    Utilidad general para lectura y escritura segura de archivos JSON
    dentro del sistema S.A.M.
    - Centraliza las operaciones de E/S.
    - Controla errores y permisos.
    - Previene corrupción de datos.
    """

    def __init__(self, base_path: str = "core/data/"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        logger.info(f"FileManager inicializado en: {self.base_path}")

    # ============================================================
    # Métodos de utilidad
    # ============================================================

    def build_path(self, relative_path: str) -> str:
        """Devuelve la ruta absoluta de un archivo dentro de core/data/."""
        path = os.path.join(self.base_path, relative_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def load_json(self, relative_path: str) -> Dict[str, Any]:
        """Carga un archivo JSON desde una ruta relativa al base_path."""
        path = self.build_path(relative_path)
        if not os.path.exists(path):
            logger.warning(f"Archivo no encontrado: {path}")
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Archivo cargado: {path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON ({path}): {e}")
            return {}
        except Exception as e:
            logger.exception(f"Error al leer archivo {path}: {e}")
            return {}

    def save_json(self, relative_path: str, data: Dict[str, Any], indent: int = 2):
        """Guarda datos en formato JSON con manejo seguro de errores."""
        path = self.build_path(relative_path)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            logger.info(f"Archivo guardado correctamente: {path}")
        except Exception as e:
            logger.exception(f"Error al guardar JSON ({path}): {e}")

    def exists(self, relative_path: str) -> bool:
        """Verifica si un archivo existe dentro del base_path."""
        path = self.build_path(relative_path)
        return os.path.exists(path)

    def delete(self, relative_path: str) -> bool:
        """Elimina un archivo si existe."""
        path = self.build_path(relative_path)
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Archivo eliminado: {path}")
                return True
            logger.warning(f"No se encontró archivo para eliminar: {path}")
            return False
        except Exception as e:
            logger.exception(f"Error al eliminar {path}: {e}")
            return False

    def list_files(self, subdir: str = "") -> Optional[list]:
        """Lista archivos dentro de una subcarpeta."""
        folder = self.build_path(subdir)
        try:
            if os.path.exists(folder):
                return os.listdir(folder)
            logger.warning(f"Directorio no encontrado: {folder}")
            return None
        except Exception as e:
            logger.exception(f"Error al listar archivos en {folder}: {e}")
            return None
