import random

# ================================================================
# 🧪 NARRATIVE TONE BLENDING (Fase 6.19)
# ================================================================
# Combina dos tonos emocionales para crear matices narrativos
# intermedios más naturales y profundos.
# ================================================================


class ToneBlender:
    def __init__(self):
        self.blend_matrix = {
            ("hopeful", "melancholic"): {
                "label": "wistful_hope",
                "description": "Una esperanza teñida de nostalgia.",
                "style": "poético, pausado pero optimista",
                "lexical_bias": ["recuerdo", "luz", "anhelo", "renacer", "pasado"]
            },
            ("dark", "bright"): {
                "label": "ironic_light",
                "description": "Una luz absurda entre sombras densas.",
                "style": "sarcástico, teatral, contrastante",
                "lexical_bias": ["risa amarga", "sombras", "brillo", "ironía", "destino"]
            },
            ("neutral", "fearful"): {
                "label": "quiet_tension",
                "description": "Un silencio expectante que presagia peligro.",
                "style": "contenido, tenso, introspectivo",
                "lexical_bias": ["eco", "susurro", "sombra", "duda", "espera"]
            },
            ("bright", "sad"): {
                "label": "bittersweet",
                "description": "Una alegría que duele al recordarla.",
                "style": "emotivo, nostálgico pero cálido",
                "lexical_bias": ["risa", "llanto", "recuerdo", "sol", "melodía"]
            },
            ("melancholic", "dark"): {
                "label": "grief",
                "description": "Tristeza profunda que roza la desesperación.",
                "style": "lento, denso, poético",
                "lexical_bias": ["noche", "eco", "vacío", "dolor", "memoria"]
            },
            ("hopeful", "bright"): {
                "label": "radiant",
                "description": "Luz y optimismo desbordantes.",
                "style": "rápido, expresivo y positivo",
                "lexical_bias": ["luz", "sol", "futuro", "vida", "renacer"]
            },
        }

    # ------------------------------------------------------------
    # 🔮 Mezclar dos tonos
    # ------------------------------------------------------------
    def blend(self, tone_a: str, tone_b: str) -> dict:
        """Combina dos tonos para obtener un matiz emocional intermedio."""
        key = (tone_a, tone_b)
        if key not in self.blend_matrix:
            key = (tone_b, tone_a)  # probar reverso

        if key in self.blend_matrix:
            blend = self.blend_matrix[key]
        else:
            blend = {
                "label": f"{tone_a}_{tone_b}",
                "description": "Una mezcla ambigua de emociones.",
                "style": "neutro, adaptable",
                "lexical_bias": ["equil]()_
