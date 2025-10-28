# ==========================================================
# 🌍 SAM – Fase 7.2: Propagación de Consecuencias Globales
# ==========================================================
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WorldInfluence:
    """
    Evalúa el historial del mundo y ajusta los sistemas narrativos,
    emocionales y de eventos futuros según las consecuencias acumuladas.
    """

    def __init__(self):
        self.max_memory_days = 30  # tiempo máximo para considerar eventos relevantes

    def analyze_history(self, world_state: dict, emotional_state: dict):
        """
        Analiza el historial de eventos recientes para generar sesgos globales.
        """
        if not world_state or "world_history" not in world_state:
            return emotional_state

        recent_events = self._get_recent_events(world_state["world_history"])
        if not recent_events:
            return emotional_state

        # Contadores de tipos de eventos
        positive, negative, tension = 0, 0, 0

        for e in recent_events:
            title = (e.get("event") or "").lower()
            desc = (e.get("description") or "").lower()

            # Clasificación básica
            if any(x in title for x in ["festival", "renovación", "esperanza"]):
                positive += 1
            elif any(x in title for x in ["ataque", "bestia", "maldición", "guerra"]):
                negative += 1
            elif any(x in title for x in ["rumor", "tormenta", "tensión"]):
                tension += 1
            else:
                # clasificar por tono emocional global de la sesión
                if emotional_state.get("tone") in ["tensión", "melancolía"]:
                    tension += 1

        total = positive + negative + tension
        if total == 0:
            return emotional_state

        # Ajuste de emociones globales
        balance = {
            "hope": round(positive / total, 2),
            "fear": round(negative / total, 2),
            "tension": round(tension / total, 2)
        }

        for key, val in balance.items():
            emotional_state[key] = round(
                (emotional_state.get(key, 0.0) * 0.7) + (val * 0.3), 2
            )

        # Ajuste de tono global
        if balance["hope"] > balance["fear"] and balance["hope"] > balance["tension"]:
            emotional_state["tone"] = "esperanza"
        elif balance["fear"] > 0.5:
            emotional_state["tone"] = "tensión"
        elif balance["tension"] > 0.4:
            emotional_state["tone"] = "melancolía"
        else:
            emotional_state["tone"] = "neutral"

        logger.info(f"[WorldInfluence] Tono global ajustado: {emotional_state['tone']}")
        return emotional_state

    def _get_recent_events(self, history):
        """
        Filtra eventos ocurridos dentro de la ventana de memoria.
        """
        cutoff = datetime.utcnow() - timedelta(days=self.max_memory_days)
        recent = []
        for e in history:
            try:
                ts = datetime.fromisoformat(e.get("timestamp", ""))
                if ts >= cutoff:
                    recent.append(e)
            except Exception:
                continue
        return recent
