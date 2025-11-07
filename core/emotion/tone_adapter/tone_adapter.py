# ================================================================
# 🎭 TONE ADAPTER – Fase 7.7-clean
# ================================================================
# Ajusta el tono narrativo según la emoción global y
# el perfil de grupo (party_profile) proporcionado por StoryDirector.
# Permite que la descripción de la escena se sienta “viva” y coherente.
# ================================================================

import random

class ToneAdapter:
    """
    🎭 Adapta el tono y estilo narrativo del texto según:
      - el estado emocional actual (p.ej. tenso, neutral, heroico)
      - el perfil del grupo (rasgos dominantes)
    """

    def __init__(self):
        # Diccionario base de ajustes de tono por emoción
        self.tone_presets = {
            "neutral": {
                "prefix": "",
                "suffix": "",
                "adjectives": ["tranquilo", "sereno", "neutral"]
            },
            "tension": {
                "prefix": "⚡ Una sensación de tensión recorre el aire. ",
                "suffix": " El peligro parece inminente.",
                "adjectives": ["tenso", "inquietante", "suspenso"]
            },
            "setback": {
                "prefix": "💥 Un revés sacude el ánimo del grupo. ",
                "suffix": " Pero aún hay esperanza.",
                "adjectives": ["oscuro", "difícil", "angustioso"]
            },
            "triumph": {
                "prefix": "🌟 El espíritu del grupo brilla con fuerza. ",
                "suffix": " Una nueva energía los impulsa a seguir.",
                "adjectives": ["glorioso", "vibrante", "heroico"]
            },
            "progress": {
                "prefix": "🚶‍♂️ El viaje continúa con determinación. ",
                "suffix": " El horizonte promete descubrimientos.",
                "adjectives": ["optimista", "resuelto", "esperanzador"]
            },
            "fear": {
                "prefix": "😨 Una sombra de miedo se cierne sobre ellos. ",
                "suffix": " Algo desconocido los observa desde lejos.",
                "adjectives": ["aterrador", "sombrío", "opresivo"]
            }
        }

    # ------------------------------------------------------------
    # 🔧 MÉTODO PRINCIPAL
    # ------------------------------------------------------------
    def apply_tone(self, text: str, emotional_state: str, party_profile: dict = None) -> str:
        """
        Aplica un tono narrativo al texto base en función del estado emocional
        y del perfil colectivo del grupo.
        """
        tone_data = self.tone_presets.get(emotional_state, self.tone_presets["neutral"])
        prefix = tone_data.get("prefix", "")
        suffix = tone_data.get("suffix", "")

        adjectives = tone_data.get("adjectives", [])
        adjective = random.choice(adjectives) if adjectives else ""

        # Ajuste adicional según perfil de grupo
        if party_profile:
            focus_trait = party_profile.get("dominant_trait", "")
            if focus_trait in ["brave", "valor", "fuerte"]:
                suffix += " El grupo mantiene la frente en alto, sin temor."
            elif focus_trait in ["wise", "sabio", "inteligente"]:
                suffix += " Analizan la situación antes de actuar."
            elif focus_trait in ["cunning", "astuto"]:
                suffix += " Una sonrisa astuta cruza sus rostros."
            elif focus_trait in ["charismatic", "carismático"]:
                suffix += " Su presencia inspira a quienes los rodean."

        # Construcción final del texto adaptado
        adapted_text = f"{prefix}{text.strip().capitalize()} {suffix}".strip()
        return adapted_text

    # ------------------------------------------------------------
    # 🎨 FUNCIÓN AUXILIAR (debug o vista previa)
    # ------------------------------------------------------------
    def preview_tone(self, emotional_state: str):
        """
        Devuelve una breve muestra de cómo sería el tono narrativo
        para un estado emocional específico.
        """
        tone_data = self.tone_presets.get(emotional_state, {})
        sample = f"{tone_data.get('prefix', '')}Ejemplo de escena {emotional_state}. {tone_data.get('suffix', '')}"
        return sample.strip()


# ================================================================
# 🧪 TEST LOCAL
# ================================================================
if __name__ == "__main__":
    adapter = ToneAdapter()

    examples = ["neutral", "tension", "setback", "triumph", "progress", "fear"]
    for e in examples:
        preview = adapter.apply_tone("el grupo avanza hacia la cueva silenciosa", e, {"dominant_trait": "brave"})
        print(f"\n[{e.upper()}] {preview}")
