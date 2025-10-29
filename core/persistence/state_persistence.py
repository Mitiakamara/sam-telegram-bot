# ================================================================
# 💾 STATE PERSISTENCE
# ================================================================
# Maneja el guardado y la carga del estado narrativo del mundo.
# Persiste:
#  - Escena actual
#  - Estado emocional
#  - Estado del grupo (party)
#
# Compatible con Orchestrator (Fase 7.0)
# ================================================================

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class StatePersistence:
    def __init__(self, file_path: str = "data/game_state.json"):
        self.file_path = file_path

        # Asegurar existencia de carpeta
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Intentar cargar estado previo si existe
        if os.path.exists(self.file_path):
            logger.info("[StatePersistence] Cargando estado previo desde disco...")
            self.state = self.load_state()
        else:
            logger.warning("[StatePersistence] No se encontró archivo de estado previo.")
            self.state = {}

    # ------------------------------------------------------------
    # 💾 Guardar estado
    # ------------------------------------------------------------
    def save_state(self, scene_state: dict, emotional_state: dict, party_state: dict):
        """
        Guarda el estado actual del mundo narrativo en JSON.
        """
        try:
            state = {
                "scene": scene_state,
                "emotion": emotional_state,
                "party": party_state,
                "timestamp": datetime.utcnow().isoformat(),
            }

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            logger.info("[StatePersistence] Estado guardado correctamente en data/game_state.json")
            self.state = state

        except Exception as e:
            logger.error(f"[StatePersistence] Error al guardar el estado: {e}")

    # ------------------------------------------------------------
    # 📖 Cargar estado
    # ------------------------------------------------------------
    def load_state(self):
        """
        Carga el estado del mundo desde disco.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("[StatePersistence] Estado cargado correctamente.")
            return data
        except FileNotFoundError:
            logger.warning("[StatePersistence] Archivo de estado no encontrado. Iniciando desde cero.")
            return {}
        except json.JSONDecodeError:
            logger.error("[StatePersistence] Error al decodificar el archivo JSON. Reiniciando estado.")
            return {}
        except Exception as e:
            logger.error(f"[StatePersistence] Error inesperado al cargar estado: {e}")
            return {}

    # ------------------------------------------------------------
    # 🔍 Obtener estado actual
    # ------------------------------------------------------------
    def get_state(self):
        """
        Devuelve el último estado cargado o guardado.
        """
        return self.state

    # ------------------------------------------------------------
    # 🧹 Borrar estado (opcional, para debug o reinicio total)
    # ------------------------------------------------------------
    def clear_state(self):
        """
        Elimina el archivo de estado y reinicia el sistema.
        """
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
                logger.warning("[StatePersistence] Archivo de estado eliminado manualmente.")
            self.state = {}
        except Exception as e:
            logger.error(f"[StatePersistence] Error al eliminar archivo de estado: {e}")


# ------------------------------------------------------------
# 🧪 DEMO LOCAL
# ------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    persistence = StatePersistence()

    dummy_scene = {"scene": {"title": "El amanecer sobre el valle"}}
    dummy_emotion = {"emotion": "hope", "intensity": 0.8}
    dummy_party = {"members": ["Asterix", "Valen"]}

    persistence.save_state(dummy_scene, dummy_emotion, dummy_party)

    loaded = persistence.load_state()
    print("\n🧾 Estado cargado:")
    print(json.dumps(loaded, indent=2, ensure_ascii=False))
