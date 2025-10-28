# ==========================================================
# ⚔️ SAM – Fase 7.3: Facciones y Repercusiones Regionales
# ==========================================================
import json
import logging
from pathlib import Path
from random import randint, choice

logger = logging.getLogger(__name__)

class FactionManager:
    """
    Gestiona el estado de las facciones y regiones del mundo.
    Permite actualizar reputaciones, influencias y tensiones políticas.
    """

    def __init__(self, factions_path: str = "core/world_events/factions.json"):
        self.factions_path = Path(factions_path)
        self.factions = self._load_factions()

    # ==========================================================
    # CARGA / GUARDADO
    # ==========================================================
    def _load_factions(self):
        if not self.factions_path.exists():
            logger.warning(f"[FactionManager] No se encontró {self.factions_path}, creando base vacía.")
            return {"factions": []}
        with open(self.factions_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_factions(self):
        with open(self.factions_path, "w", encoding="utf-8") as f:
            json.dump(self.factions, f, indent=4, ensure_ascii=False)
        logger.info(f"[FactionManager] Estado de facciones guardado en {self.factions_path}")

    # ==========================================================
    # FUNCIONES PRINCIPALES
    # ==========================================================
    def apply_event_effect(self, event: dict):
        """
        Aplica el impacto de un evento en las facciones relevantes.
        Si el evento incluye 'faction_targets' en su consecuencia, modifica su influencia/reputación.
        """
        cons = event.get("consequence", {})
        factions_affected = cons.get("factions", [])
        if not factions_affected:
            return

        for f_data in factions_affected:
            f_id = f_data.get("id")
            delta = f_data.get("influence", 0)
            reputation = f_data.get("reputation", 0)
            self._adjust_faction(f_id, delta, reputation)

        # Calcular tensiones y conflictos tras el evento
        self._update_tensions()

        # Guardar el resultado actualizado
        self.save_factions()

    def _adjust_faction(self, faction_id, delta_influence, delta_reputation):
        for f in self.factions.get("factions", []):
            if f["id"] == faction_id:
                f["influence"] = max(-100, min(100, f.get("influence", 0) + delta_influence))
                f["reputation"] = max(-100, min(100, f.get("reputation", 0) + delta_reputation))
                logger.info(
                    f"[FactionManager] {f['name']} → Influencia: {f['influence']} | Reputación: {f['reputation']}"
                )
                return

    def _update_tensions(self):
        """
        Evalúa relaciones entre facciones según sus alineamientos e influencias.
        Si las diferencias son muy grandes, marca tensión o guerra.
        """
        factions = self.factions.get("factions", [])
        for f in factions:
            for other in factions:
                if f["id"] == other["id"]:
                    continue
                # Diferencia de alineamiento o poder → ajusta relación
                power_gap = abs(f["influence"] - other["influence"])
                rel = f["relations"].get(other["id"], 0)
                if power_gap > 50:
                    rel -= 5
                elif power_gap < 20:
                    rel += 2
                rel = max(-100, min(100, rel))
                f["relations"][other["id"]] = rel

                # Cambiar estado a "en guerra" si es muy negativo
                if rel < -75:
                    f["status"] = "en guerra"
                elif rel > 60:
                    f["status"] = "aliada"
                else:
                    f["status"] = "activo"

    def summarize_world(self):
        """
        Devuelve un resumen general del estado político del mundo.
        """
        summary = []
        for f in self.factions.get("factions", []):
            summary.append(
                {
                    "name": f["name"],
                    "influence": f["influence"],
                    "reputation": f["reputation"],
                    "status": f["status"],
                    "region": f["region"]
                }
            )
        return summary

    def random_faction(self):
        """
        Devuelve una facción aleatoria (para generar eventos o misiones).
        """
        if not self.factions.get("factions"):
            return None
        return choice(self.factions["factions"])
