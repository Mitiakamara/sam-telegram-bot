import random
from typing import Dict, Any
from core.utils.logger import safe_logger
from core.tone_adapter import apply_tone

logger = safe_logger(__name__)

# ============================================================
# 🪶 NARRATIVE FEEDBACK 5.6a
# ------------------------------------------------------------
# Modula la narración global según la curva emocional y el
# tono dramático dominante de la sesión.
# ============================================================


class NarrativeFeedback:
    def __init__(self, session_data: Dict[str, Any]):
        self.session = session_data
        self.state = self.session.get("emotional_state", {})
        self.tone = self.state.get("session_tone", "neutral")
        self.intensity = int(self.state.get("emotion_intensity", 3))
        self.curve = self.state.get("curve_report", {})
        self.current_emotion = self.state.get("current_emotion", "neutral")

    # ============================================================
    # ✨ Ajuste del tono narrativo global
    # ============================================================

    GLOBAL_TONE_STYLES = {
        "heroico": {
            "prefix": "La atmósfera vibra con la energía de los héroes. ",
            "style": "frases amplias, épicas, llenas de determinación y luz."
        },
        "esperanzador": {
            "prefix": "Aunque el peligro persiste, una chispa de esperanza guía sus pasos. ",
            "style": "lenguaje positivo, tono cálido, imágenes luminosas."
        },
        "trágico": {
            "prefix": "El silencio pesa sobre los corazones, cada paso es un recuerdo de lo perdido. ",
            "style": "poético, introspectivo, ritmo pausado, melancólico."
        },
        "tenso u oscuro": {
            "prefix": "Sombras densas se arrastran sobre el escenario, cada sonido podría ser el último. ",
            "style": "frases cortas, sensación de peligro constante, tono sombrío."
        },
        "neutral": {
            "prefix": "",
            "style": "narración equilibrada, sin inclinación emocional evidente."
        }
    }

    # ============================================================
    # 🧠 Generación de narración adaptada
    # ============================================================

    def adapt_narration(self, base_text: str, scene_type: str = "neutral") -> str:
        """
        Aplica una capa de retroalimentación narrativa:
        el texto se ajusta al tono global y a la emoción actual.
        """
        style_data = self.GLOBAL_TONE_STYLES.get(self.tone, self.GLOBAL_TONE_STYLES["neutral"])
        prefix = style_data.get("prefix", "")
        style_hint = style_data.get("style", "")

        # Aplicar microtono local (escena actual)
        text_with_tone = apply_tone(scene_type, base_text, intensity=self.intensity)

        # Combinar con tono global
        final_text = f"{prefix}{text_with_tone}"

        # Suavizar o intensificar según promedio de intensidad global
        avg_intensity = self.curve.get("average_intensity", self.intensity)
        if avg_intensity >= 4:
            final_text = final_text.replace(".", "!").replace("..", "!")
        elif avg_intensity <= 2:
            final_text = final_text.replace(".", ",").replace("!", ".")

        logger.info(f"🪶 Narrativa adaptada ({self.tone}, intensidad {avg_intensity:.2f}) aplicada.")
        return final_text.strip()

    # ============================================================
    # 🎬 Resumen narrativo de sesión
    # ============================================================

    def summarize_session(self) -> str:
        """
        Devuelve una sinopsis narrativa breve de la sesión, basada en la curva emocional.
        """
        tone = self.tone
        curve_points = self.curve.get("curve_points", [])
        if not curve_points:
            return "La sesión carece de registros emocionales suficientes para generar un resumen."

        highs = [p for p in curve_points if p["value"] > 2]
        lows = [p for p in curve_points if p["value"] < -1]
        avg_intensity = self.curve.get("average_intensity", 3)

        summary = f"La aventura tomó un tono {tone}. "
        if highs:
            summary += f"Hubo momentos de gran intensidad emocional ({len(highs)}), llenos de energía y dramatismo. "
        if lows:
            summary += f"También se sintieron descensos y dudas ({len(lows)}), marcando la vulnerabilidad del grupo. "
        if avg_intensity >= 4:
            summary += "La historia alcanzó un clímax poderoso, dejando una sensación de triunfo y agotamiento."
        elif avg_intensity <= 2:
            summary += "El tono fue más contenido y reflexivo, con pausas que aliviaron la tensión."

        return summary.strip()
