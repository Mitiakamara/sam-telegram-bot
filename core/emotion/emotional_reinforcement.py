import os
import json
from datetime import datetime
from statistics import mean

# ================================================================
# ♻️ EMOTIONAL REINFORCEMENT LOOP (Fase 6.27)
# ================================================================
# Analiza cómo cada encuentro afectó la cohesión y el tono
# emocional del grupo, y ajusta los pesos narrativos futuros.
# ================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")
REINFORCEMENT_FILE = os.path.join(BASE_DIR, "emotional_reinforcement.json")


class EmotionalReinforcementLoop:
    def __init__(self):
        os.makedirs(BASE_DIR, exist_ok=True)
        self.memory = self._load_memory()
        self.last_update = None

    # ------------------------------------------------------------
    # 🔧 Utilidades internas
    # ------------------------------------------------------------
    def _load_memory(self):
        if not os.path.exists(REINFORCEMENT_FILE):
            return {"history": [], "reinforcement_profile": {}}
        try:
            with open(REINFORCEMENT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"history": [], "reinforcement_profile": {}}

    def _save_memory(self):
        with open(REINFORCEMENT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4, ensure_ascii=False)

    # ------------------------------------------------------------
    # 🧩 Registrar impacto emocional del encuentro
    # ------------------------------------------------------------
    def record_encounter_result(self, encounter, before_group, after_group):
        """
        Guarda el impacto de un encuentro sobre la cohesión grupal.
        Calcula si el evento reforzó o debilitó el estado emocional.
        """
        before = before_group.get("cohesion", 0.7) if before_group else 0.7
        after = after_group.get("cohesion", 0.7) if after_group else 0.7
        delta = round(after - before, 2)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": encounter.get("type", "unknown"),
            "tone": encounter.get("tone", "neutral"),
            "difficulty": encounter.get("difficulty", 3),
            "delta_cohesion": delta,
            "reinforced": delta >= 0,
        }

        self.memory["history"].append(result)
        self._update_reinforcement_profile()
        self._save_memory()

        outcome = "positivo" if delta >= 0 else "negativo"
        print(f"♻️ [EmotionalReinforcement] {encounter['type']} → impacto {outcome} ({delta:+.2f})")

    # ------------------------------------------------------------
    # 🔬 Analizar patrones de refuerzo
    # ------------------------------------------------------------
    def _update_reinforcement_profile(self):
        """Identifica qué tipos de encuentros suelen reforzar o debilitar la cohesión."""
        history = self.memory["history"]
        if not history:
            return

        grouped = {}
        for h in history:
            t = h["type"]
            grouped.setdefault(t, []).append(h["delta_cohesion"])

        profile = {}
        for t, deltas in grouped.items():
            avg_delta = round(mean(deltas), 2)
            profile[t] = {
                "avg_delta": avg_delta,
                "trend": "positive" if avg_delta > 0 else "negative" if avg_delta < 0 else "neutral"
            }

        self.memory["reinforcement_profile"] = {
            "encounter_types": profile,
            "total_records": len(history),
            "last_update": datetime.utcnow().isoformat()
        }
        self.last_update = self.memory["reinforcement_profile"]["last_update"]

    # ------------------------------------------------------------
    # 🎯 Obtener perfil de refuerzo actual
    # ------------------------------------------------------------
    def get_profile(self):
        """Devuelve el perfil actual de refuerzo emocional."""
        if not self.memory["reinforcement_profile"]:
            self._update_reinforcement_profile()
        return self.memory["reinforcement_profile"]

    # ------------------------------------------------------------
    # 🧠 Aplicar refuerzo al sistema narrativo
    # ------------------------------------------------------------
    def apply_reinforcement_to_director(self, story_director):
        """
        Ajusta pesos narrativos del Story Director según qué tipos
        de encuentros generan mejor cohesión emocional.
        """
        profile = self.get_profile().get("encounter_types", {})
        if not profile:
            return

        adjustments = {}
        for enc_type, data in profile.items():
            if data["trend"] == "positive":
                adjustments[enc_type] = 1.2
            elif data["trend"] == "negative":
                adjustments[enc_type] = 0.8
            else:
                adjustments[enc_type] = 1.0

        story_director.update_encounter_weights(adjustments)
        print(f"🎛️ [EmotionalReinforcement] Ajustes aplicados al Story Director: {adjustments}")
        return adjustments
