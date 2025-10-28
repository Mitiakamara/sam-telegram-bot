# ==========================================================
# 💾 SAM – Fase 7.1: Persistencia y Memoria de Consecuencias
# ==========================================================
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class StatePersistence:
    """
    Administra la carga y guardado de los estados globales del juego.
    """

    def __init__(self, save_path="data/game_state.json"):
        self.save_path = Path(save_path)
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------------
    # GUARDADO
    # ----------------------------------------------------------
    def save_state(self, world_state: dict, emotional_state: dict, party_state: dict):
        try:
            data = {
                "world_state": world_state,
                "emotional_state": emotional_state,
                "party_state": party_state
            }
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"[StatePersistence] Estado guardado en {self.save_path}")
        except Exception as e:
            logger.error(f"[StatePersistence] Error al guardar estado: {e}")

    # ----------------------------------------------------------
    # CARGA
    # ----------------------------------------------------------
    def load_state(self):
        if not self.save_path.exists():
            logger.warning("[StatePersistence] No se encontró archivo de estado previo.")
            return None, None, None
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("[StatePersistence] Estado cargado correctamente.")
            return (
                data.get("world_state", {}),
                data.get("emotional_state", {}),
                data.get("party_state", {})
            )
        except Exception as e:
            logger.error(f"[StatePersistence] Error al cargar estado: {e}")
            return None, None, None
