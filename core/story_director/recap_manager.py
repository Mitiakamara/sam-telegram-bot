"""
RecapManager
-------------
Genera un resumen narrativo dinámico basado en la memoria dramática de S.A.M.

Analiza los eventos guardados en memory_state.json y crea una recapitulación
en tono adaptativo, mencionando temas recurrentes, emociones dominantes y
eventos recientes.
"""

import statistics
from core.story_director.memory_manager import MemoryManager
from core.tone_adapter.tone_adapter import ToneAdapter


class RecapManager:
    def __init__(self):
        self.memory = MemoryManager()
        self.tone_adapter = ToneAdapter()

    # ==========================================================
    # 🔹 GENERAR RESUMEN
    # ==========================================================
    def generate_recap(self) -> str:
        """Crea un resumen narrativo adaptativo del viaje."""
        data = self.memory.memory
        timeline = data.get("timeline", [])
        if not timeline:
            return "S.A.M. se queda pensativo... aún no hay historia que recordar."

        # Determinar emociones promedio y temas predominantes
        avg_emotion = self.memory.get_average_emotion()
        main_theme = self.memory.get_recurrent_theme() or "misterio"
        last_event = self.memory.get_last_event()

        # Construir resumen base
        total_events = len(timeline)
        opening = f"📜 *Resumen del viaje hasta ahora* ({total_events} eventos registrados)\n\n"
        narrative = []

        # Sintetizar primeros y últimos eventos
        if total_events > 3:
            first = timeline[0]
            middle = timeline[len(timeline) // 2]
            last = timeline[-1]
            narrative.append(
                f"Todo comenzó con *{first['theme']}*, cuando {first['description'].lower()}"
            )
            narrative.append(
                f"Más tarde, el tono de la historia se tornó hacia *{middle['theme']}*, "
                f"marcado por la emoción de nivel {middle['emotion']}."
            )
            narrative.append(
                f"Y finalmente, {last['description'].lower()} — un reflejo del tema de *{last['theme']}*."
            )
        else:
            for ev in timeline:
                narrative.append(f"- {ev['description']}")

        # Añadir análisis emocional y temático
        narrative.append("")
        narrative.append(f"💫 *Tema predominante:* {main_theme.capitalize()}")
        narrative.append(f"🎭 *Emoción media del viaje:* {round(avg_emotion, 2)} / 5")

        # Adaptar tono del resumen
        recap_text = " ".join(narrative)
        recap_text = self.tone_adapter.adapt_description(recap_text, int(round(avg_emotion)))

        return opening + recap_text
