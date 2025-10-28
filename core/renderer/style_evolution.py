import random
from core.emotion.tone_memory import ToneMemory
from datetime import datetime

# ================================================================
# 🧬 NARRATIVE STYLE EVOLUTION (Fase 6.21)
# ================================================================
# Ajusta el estilo narrativo de S.A.M. en función de la firma tonal
# dominante de la campaña (Tone Memory Imprint) y el tono actual.
# ================================================================


class NarrativeStyleEvolution:
    def __init__(self, mood_manager):
        self.mood_manager = mood_manager
        self.tone_memory = ToneMemory()
        self.signature = self.tone_memory.get_imprint()
        self.last_update = datetime.utcnow().isoformat()
        self.active_style = self._define_style()

    # ------------------------------------------------------------
    # 🧠 Definir estilo activo basado en la firma tonal
    # ------------------------------------------------------------
    def _define_style(self):
        dominant = self.signature.get("dominant_signature", "neutral")
        tone = self.mood_manager.current_tone
        blend = self.mood_manager.last_blend["label"] if self.mood_manager.last_blend else "neutral"

        style_map = {
            "wistful_hope": {
                "tempo": "slow",
                "tone": "warm",
                "lexicon": ["recuerdo", "anhelo", "renacer", "luz", "melancolía"],
                "voice": "poética y suave, con un dejo de nostalgia luminosa"
            },
            "quiet_tension": {
                "tempo": "medium",
                "tone": "cool",
                "lexicon": ["silencio", "susurro", "espera", "eco", "sombra"],
                "voice": "tensa y contenida, con frases cortas"
            },
            "ironic_light": {
                "tempo": "fast",
                "tone": "warm",
                "lexicon": ["risa", "contraste", "brillo", "ironía", "destino"],
                "voice": "sarcástica, teatral y expresiva"
            },
            "grief": {
                "tempo": "slow",
                "tone": "cold",
                "lexicon": ["noche", "vacío", "recuerdo", "dolor", "memoria"],
                "voice": "profunda, poética y sombría"
            },
            "radiant": {
                "tempo": "fast",
                "tone": "hot",
                "lexicon": ["sol", "vida", "destino", "futuro", "renacer"],
                "voice": "épica, entusiasta y heroica"
            },
            "bittersweet": {
                "tempo": "medium",
                "tone": "neutral",
                "lexicon": ["risa", "llanto", "mirada", "memoria", "adiós"],
                "voice": "emocional y cálida, mezcla de alegría y tristeza"
            },
            "default": {
                "tempo": "medium",
                "tone": "neutral",
                "lexicon": ["día", "camino", "voz", "destino", "tiempo"],
                "voice": "narración equilibrada y descriptiva"
            }
        }

        style = style_map.get(dominant, style_map["default"])
        style["blend"] = blend
        style["tone"] = tone
        return style

    # ------------------------------------------------------------
    # ✍️ Aplicar estilo narrativo al texto generado
    # ------------------------------------------------------------
    def stylize_text(self, text: str) -> str:
        """
        Modifica el texto base según el estilo activo.
        Cambia ritmo, léxico y tono de voz.
        """
        style = self.active_style
        modified = text

        # Inyectar matices léxicos
        if random.random() > 0.6:
            word = random.choice(style["lexicon"])
            modified += f" {random.choice(['...', '—', ','])} {word}."

        # Ajustar ritmo narrativo
        if style["tempo"] == "slow":
            modified = self._apply_slow_rhythm(modified)
        elif style["tempo"] == "fast":
            modified = self._apply_fast_rhythm(modified)

        # Añadir “voz narrativa”
        signature = style.get("voice", "")
        return f"{modified}\n\n_{signature}_"

    # ------------------------------------------------------------
    # ⚙️ Ritmo narrativo lento o rápido
    # ------------------------------------------------------------
    def _apply_slow_rhythm(self, text: str) -> str:
        """Divide el texto con pausas para crear efecto introspectivo."""
        segments = text.split(". ")
        return "… ".join(segments)

    def _apply_fast_rhythm(self, text: str) -> str:
        """Une oraciones para un ritmo acelerado."""
        text = text.replace(". ", ", ").replace("…", ",")
        return text + "!"

    # ------------------------------------------------------------
    # 📜 Generar resumen del estilo activo
    # ------------------------------------------------------------
    def describe_style(self) -> str:
        style = self.active_style
        return (
            f"🎨 *Estilo narrativo activo:*\n"
            f"- Firma tonal dominante: {self.signature.get('dominant_signature', 'neutral')}\n"
            f"- Ritmo: {style['tempo']}\n"
            f"- Tono base: {style['tone']}\n"
            f"- Matiz actual: {style['blend']}\n"
            f"- Voz: {style['voice']}"
        )
