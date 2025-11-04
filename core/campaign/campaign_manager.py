# ================================================================
# 📘 CAMPAIGN MANAGER – Fase 7.5 (SRD Adaptada)
# ================================================================
# Gestiona el progreso de campañas pre-creadas.
# Permite guardar y restaurar:
# - Escena actual
# - Capítulo de campaña
# - Estado del grupo (party)
# - Objetivos completados o pendientes
# ================================================================

import json
import os
from datetime import datetime


class CampaignManager:
    """
    Administra el estado actual de una campaña pre-creada SRD 5.1.2.
    """

    def __init__(self, campaign_id="default_campaign", save_path="data/campaign_state.json"):
        self.campaign_id = campaign_id
        self.save_path = save_path
        self.state = self._load_state()

    # =========================================================
    # CARGA Y GUARDADO DE ESTADO
    # =========================================================
    def _load_state(self):
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("campaign_id") == self.campaign_id:
                        return data
            except Exception as e:
                print(f"[CampaignManager] Error cargando estado: {e}")
        # Estado inicial por defecto
        return {
            "campaign_id": self.campaign_id,
            "current_chapter": 1,
            "active_scene": None,
            "party": [],
            "completed_quests": [],
            "pending_quests": [],
            "last_updated": str(datetime.now())
        }

    def save_state(self):
        self.state["last_updated"] = str(datetime.now())
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
        print(f"[CampaignManager] Estado guardado en {self.save_path}")

    # =========================================================
    # ACTUALIZACIÓN DE PROGRESO
    # =========================================================
    def update_scene(self, scene_name):
        self.state["active_scene"] = scene_name
        self.save_state()

    def advance_chapter(self):
        self.state["current_chapter"] += 1
        self.save_state()

    def add_completed_quest(self, quest_name):
        if quest_name not in self.state["completed_quests"]:
            self.state["completed_quests"].append(quest_name)
        if quest_name in self.state["pending_quests"]:
            self.state["pending_quests"].remove(quest_name)
        self.save_state()

    def add_pending_quest(self, quest_name):
        if quest_name not in self.state["pending_quests"]:
            self.state["pending_quests"].append(quest_name)
        self.save_state()

    def set_party(self, party_names):
        self.state["party"] = party_names
        self.save_state()

    # =========================================================
    # OBTENCIÓN DE ESTADO
    # =========================================================
    def get_summary(self):
        summary = (
            f"📘 *Campaña:* {self.state['campaign_id']}\n"
            f"📖 *Capítulo:* {self.state['current_chapter']}\n"
            f"🎭 *Escena activa:* {self.state['active_scene'] or 'N/A'}\n"
            f"🧙‍♂️ *Personajes:* {', '.join(self.state['party']) or 'Sin grupo'}\n"
            f"✅ *Completadas:* {', '.join(self.state['completed_quests']) or 'Ninguna'}\n"
            f"🗺️ *Pendientes:* {', '.join(self.state['pending_quests']) or 'Ninguna'}\n"
        )
        return summary


# =========================================================
# DEMO LOCAL
# =========================================================
if __name__ == "__main__":
    manager = CampaignManager("The_Genie_s_Wishes")
    manager.set_party(["Pimp", "Asterix"])
    manager.update_scene("progress_scene.json")
    manager.add_pending_quest("Recuperar la lámpara perdida")
    manager.add_completed_quest("Escapar del oasis")
    print(manager.get_summary())
