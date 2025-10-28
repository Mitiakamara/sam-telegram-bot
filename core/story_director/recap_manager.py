# sam-telegram-bot/core/story_director/recap_manager.py
"""
RecapManager
-------------
Genera un resumen narrativo dinámico de la campaña actual.
Analiza escenas recientes, su tono emocional y los eventos importantes
para ofrecer al jugador una recapitulación coherente.
"""

import os
import json
from datetime import datetime
from core.renderer import render


class RecapManager:
    """
    Genera recapitulaciones a partir de los registros narrativos recientes.
    Se apoya en el MoodManager y los datos persistidos en game_state.json.
    """

    def __init__(self, base_path: str = "data/"):
        self.base_path = base_path
        self.state_path = os.path.join(base_path, "game_state.json")
        self.scenes_path = os.path.join(base_path, "scenes_history.json")

        # Cargar información persistente
        self._ensure_files_exist()

    # ==========================================================
    # 🧱 UTILIDADES INTERNAS
    # ==========================================================
    def _ensure_files_exist(self):
        """Crea archivos mínimos si no existen."""
        os.makedirs(self.base_path, exist_ok=True)

        if not os.path.exists(self.state_path):
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "mood_state": "neutral",
                        "mood_intensity": 0.5,
                        "genre_profile": "heroic",
                        "last_update": datetime.utcnow().isoformat(),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

        if not os.path.exists(self.scenes_path):
            with open(self.scenes_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def _load_scenes(self) -> list:
        """Carga la lista de escenas guardadas."""
        try:
            with open(self.scenes_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _load_mood(self) -> dict:
        """Carga el estado tonal global."""
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "mood_state": "neutral",
                "mood_intensity": 0.5,
                "genre_profile": "heroic",
                "last_update": "unknown",
            }

    # ==========================================================
    # 🧠 GENERADOR DE RECAPITULACIÓN
    # ==========================================================
    def generate_recap(self) -> str:
        """
        Crea un resumen narrativo de las últimas escenas.
        Integra el mood global para mantener coherencia emocional.
        """
        scenes = self._load_scenes()
        mood = self._load_mood()

        if not scenes:
            return render(
                "Aún no hay suficientes recuerdos grabados en la historia de esta campaña."
            )

        # Tomar las últimas 5 escenas (o menos)
        recent = scenes[-5:]
        lines = []

        for sc in recent:
            title = sc.get("title", "Escena sin título")
            desc = sc.get("description_adapted", sc.get("description", ""))
            emo = sc.get("emotion", "neutral")
            intensity = sc.get("emotion_intensity", 0.5)

            lines.append(
                f"🎭 *{title}*\n"
                f"📖 {desc}\n"
                f"💫 Emoción: `{emo}` (intensidad {intensity})\n"
            )

        # Agregar información tonal general
        mood_text = (
            f"\n🌡️ Estado tonal global: *{mood.get('mood_state', 'neutral')}* "
            f"(intensidad {mood.get('mood_intensity', 0.5)}) · "
            f"género: *{mood.get('genre_profile', 'heroic')}*"
        )

        recap_text = "📜 *Resumen del viaje reciente*\n\n" + "\n".join(lines) + mood_text
        return render(recap_text)
