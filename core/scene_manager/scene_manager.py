import random

class SceneAdapter:
    """
    Fase 7.3 – Adaptador narrativo de escenas.
    Ajusta descripciones de escena según el perfil narrativo del grupo
    y el estado emocional actual proveniente del StoryDirector.
    """

    def __init__(self):
        # Palabras o atmósferas posibles por arquetipo dominante
        self.trait_atmospheres = {
            "brute": ["cargado de energía", "implacable", "áspero"],
            "graceful": ["silencioso", "preciso", "fluyente"],
            "clever": ["analítico", "meticuloso", "calculado"],
            "resilient": ["denso", "constante", "pesado"],
            "insightful": ["místico", "profundo", "sereno"],
            "charming": ["inspirador", "luminoso", "cálido"]
        }

        # Ajustes de ambiente por emoción global
        self.emotion_layers = {
            "neutral": ["equilibrado", "calmo"],
            "tension": ["opresivo", "tenso", "inquietante"],
            "progress": ["determinado", "vibrante", "activo"],
            "triumph": ["resplandeciente", "heroico", "liberador"],
            "setback": ["sombrío", "melancólico", "lento"],
            "fear": ["frío", "vacío", "amenazante"]
        }

    # =========================================================
    # FUNCIÓN PRINCIPAL
    # =========================================================
    def adapt_scene_description(self, base_text, party_profile, emotion_state="neutral"):
        """
        Reescribe parcialmente la descripción base de la escena usando el perfil narrativo.
        Ejemplo de marcador en JSON:
            "description": "El grupo avanza [ATMOSFERA] entre las ruinas antiguas."
        """
        if not base_text:
            return ""

        # 1. Arquetipo dominante del grupo
        dominant_trait = max(party_profile, key=party_profile.get) if party_profile else "neutral"
        trait_desc = random.choice(self.trait_atmospheres.get(dominant_trait, ["simple"]))

        # 2. Capa emocional actual
        emotion_desc = random.choice(self.emotion_layers.get(emotion_state, ["neutro"]))

        # 3. Reemplazo o inserción de atmósfera
        if "[ATMOSFERA]" in base_text:
            adapted = base_text.replace("[ATMOSFERA]", f"en un ambiente {emotion_desc} y {trait_desc}")
        else:
            adapted = f"En un ambiente {emotion_desc} y {trait_desc}, {base_text.strip()}"

        return adapted

    # =========================================================
    # MODO DEMO LOCAL
    # =========================================================
    def demo(self):
        sample = "El grupo avanza [ATMOSFERA] entre las ruinas antiguas."
        profile = {
            "brute": 0.2, "graceful": 0.7, "clever": 0.5,
            "resilient": 0.4, "insightful": 0.6, "charming": 0.3
        }
        print(self.adapt_scene_description(sample, profile, emotion_state="progress"))


if __name__ == "__main__":
    SceneAdapter().demo()
