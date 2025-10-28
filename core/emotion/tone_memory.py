import os
import json
from datetime import datetime
from statistics import mean

# ================================================================
# 🧬 TONE MEMORY IMPRINTING (Fase 6.20)
# ================================================================
# Permite que S.A.M. aprenda su firma emocional a partir de los
# blends y tonos usados. Cada campaña desarrolla su propio "ADN tonal".
# ================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")
MEMORY_FILE = os.path.join(BASE_DIR, "tone_memory.json")


class ToneMemory:
    def __init__(self):
        os.makedirs(BASE_DIR, exist_ok=True)
        self.memory = self._load_memory()
        self.last_update = None

    # ------------------------------------------------------------
    # 📖 Cargar y guardar memoria
    # ------------------------------------------------------------
    def _load_memory(self):
        if not os.path.exists(MEMORY_FILE):
            return {"history": [], "imprint": {}}
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"history": [], "imprint": {}}

    def _save_memory(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4, ensure_ascii=False)

    # ------------------------------------------------------------
    # 🧠 Registrar un blend de tono
    # ------------------------------------------------------------
    def record_blend(self, blend: dict):
        """Guarda un blend de tono usado recientemente."""
        if not blend or "label" not in blend:
            return

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "label": blend["label"],
            "description": blend.get("description", ""),
        }
        self.memory["history"].append(entry)
        self._update_imprint()
        self._save_memory()

        print(f"🧩 [ToneMemory] Registrado blend: {blend['label']}")

    # ------------------------------------------------------------
    # 🔬 Calcular “firma tonal” (imprint)
    # ------------------------------------------------------------
    def _update_imprint(self):
        """Calcula la frecuencia de los blends y actualiza el imprint."""
        history = self.memory["history"]
        if not history:
            return

        freq = {}
        for h in history:
            lbl = h["label"]
            freq[lbl] = freq.get(lbl, 0) + 1

        total = sum(freq.values())
        imprint = {k: round(v / total, 3) for k, v in freq.items()}

        self.memory["imprint"] = {
            "total_blends": total,
            "dominant_signature": max(imprint, key=imprint.get),
            "blend_distribution": imprint,
            "last_update": datetime.utcnow().isoformat(),
        }
        self.last_update = self.memory["imprint"]["last_update"]

    # ------------------------------------------------------------
    # 🌈 Obtener firma tonal actual
    # ------------------------------------------------------------
    def get_imprint(self):
        """Devuelve el estado actual del ADN tonal."""
        if not self.memory["imprint"]:
            self._update_imprint()
        return self.memory["imprint"]

    # ------------------------------------------------------------
    # 🧬 Aplicar la firma tonal al MoodManager
    # ------------------------------------------------------------
    def apply_to_mood_manager(self, mood_manager):
        """Ajusta el tono base del MoodManager según la firma tonal."""
        imprint = self.get_imprint()
        if not imprint or not imprint.get("dominant_signature"):
            return

        signature = imprint["dominant_signature"]
        mood_manager.last_blend = {"label": signature, "description": "Firma emocional dominante de la campaña."}
        print(f"🎨 [ToneMemory] Firma tonal aplicada → {signature}")
