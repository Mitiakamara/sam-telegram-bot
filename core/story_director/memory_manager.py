"""
MemoryManager
-------------
Subsistema de memoria dramática de S.A.M.

Guarda los eventos narrativos relevantes (temas, emociones, transiciones, clímax)
para que el StoryDirector pueda adaptar el futuro de la historia basándose en
lo ocurrido anteriormente.

Estructura interna de memoria:
{
    "timeline": [ ... eventos ... ],
    "themes_count": { "traicion": 2, "esperanza": 1 },
    "emotion_curve": [3, 4, 5, 3],
    "last_event": {...}
}
"""

import json
import os
from datetime import datetime


class MemoryManager:
    def __init__(self, file_path: str = "data/memory_state.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.memory = self._load_memory()

    # ==========================================================
    # 🔹 CARGA Y GUARDADO
    # ==========================================================
    def _load_memory(self) -> dict:
        """Carga el archivo de memoria si existe."""
        if not os.path.exists(self.file_path):
            return {"timeline": [], "themes_count": {}, "emotion_curve": [], "last_event": {}}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"timeline": [], "themes_count": {}, "emotion_curve": [], "last_event": {}}

    def _save_memory(self):
        """Guarda el estado actual de memoria."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    # ==========================================================
    # 🔹 REGISTRO DE EVENTOS
    # ==========================================================
    def record_event(self, description: str, theme: str, emotion_level: int, stage: str):
        """
        Registra un nuevo evento narrativo relevante en la línea temporal.
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "description": description,
            "theme": theme,
            "emotion": emotion_level,
            "stage": stage
        }

        # Añadir al timeline
        self.memory["timeline"].append(event)
        self.memory["last_event"] = event

        # Actualizar curva emocional
        self.memory.setdefault("emotion_curve", []).append(emotion_level)
        if len(self.memory["emotion_curve"]) > 100:
            self.memory["emotion_curve"] = self.memory["emotion_curve"][-100:]

        # Actualizar temas recurrentes
        themes = self.memory.setdefault("themes_count", {})
        themes[theme] = themes.get(theme, 0) + 1

        self._save_memory()

    # ==========================================================
    # 🔹 CONSULTAS
    # ==========================================================
    def get_recurrent_theme(self) -> str | None:
        """Devuelve el tema más frecuente hasta el momento."""
        themes = self.memory.get("themes_count", {})
        if not themes:
            return None
        return max(themes, key=themes.get)

    def get_average_emotion(self) -> float:
        """Devuelve la media emocional de toda la historia."""
        curve = self.memory.get("emotion_curve", [])
        return sum(curve) / len(curve) if curve else 3.0

    def get_last_event(self) -> dict:
        """Devuelve el último evento registrado."""
        return self.memory.get("last_event", {})

    # ==========================================================
    # 🔹 RESET / LIMPIEZA
    # ==========================================================
    def clear_memory(self):
        """Limpia toda la memoria dramática."""
        self.memory = {"timeline": [], "themes_count": {}, "emotion_curve": [], "last_event": {}}
        self._save_memory()
