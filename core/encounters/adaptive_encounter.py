import random
from datetime import datetime
from core.emotion.worldstate_projection import EmotionalWorldstateProjection

# ================================================================
# ⚔️ ADAPTIVE ENCOUNTER DESIGN (Fase 6.26)
# ================================================================
# Genera encuentros narrativos y de combate basados en el tono
# emocional actual, la proyección del mundo y el ánimo del grupo.
# ================================================================


class AdaptiveEncounterDesigner:
    def __init__(self, mood_manager):
        self.mood_manager = mood_manager
        self.projection = EmotionalWorldstateProjection()
        self.encounter_history = []

    # ------------------------------------------------------------
    # 🧠 Generar encuentro adaptativo
    # ------------------------------------------------------------
    def generate_encounter(self, group_result=None):
        """
        Genera un encuentro coherente con el tono emocional actual.
        Retorna un dict con tipo, dificultad, descripción narrativa y matiz.
        """
        tone = self.mood_manager.current_tone
        projection = self.projection.project_future_state()
        tone_shift = projection.get("tone_shift", "neutral")
        event_bias = projection.get("event_bias", "balance")

        difficulty = self._calculate_difficulty(group_result, tone_shift)
        encounter_type = self._select_type(tone, event_bias)
        description = self._describe_encounter(encounter_type, tone, difficulty)

        encounter = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": encounter_type,
            "tone": tone,
            "difficulty": difficulty,
            "projection": tone_shift,
            "event_bias": event_bias,
            "description": description
        }

        self.encounter_history.append(encounter)
        print(f"⚔️ [AdaptiveEncounter] {encounter_type} ({tone}/{difficulty}) → {event_bias}")
        return encounter

    # ------------------------------------------------------------
    # 🎭 Calcular dificultad emocional
    # ------------------------------------------------------------
    def _calculate_difficulty(self, group_result, tone_shift):
        """Determina la dificultad según cohesión e intensidad emocional."""
        base = 3  # 1–5 escala
        if group_result:
            cohesion = group_result.get("cohesion", 0.7)
            if cohesion < 0.4:
                base += 1
            elif cohesion > 0.8:
                base -= 1

        if tone_shift in ["dark", "melancholic"]:
            base += 1
        elif tone_shift in ["bright", "hopeful"]:
            base -= 1

        return max(1, min(5, base))

    # ------------------------------------------------------------
    # 🗺️ Elegir tipo de encuentro
    # ------------------------------------------------------------
    def _select_type(self, tone, bias):
        """Selecciona tipo de evento según el tono y sesgo narrativo."""
        options = {
            "combat": ["dark", "tense"],
            "exploration": ["neutral", "melancholic"],
            "social": ["bright", "hopeful"],
            "mystical": ["melancholic", "dark"],
        }

        # Sesgo narrativo modifica probabilidad
        if bias == "rewards":
            options["social"].append("neutral")
        elif bias == "conflict":
            options["combat"].append("neutral")
        elif bias == "instability":
            options["mystical"].append("tense")

        weights = {
            k: 1 + options[k].count(tone) for k in options
        }
        encounter_type = random.choices(list(options.keys()), weights=list(weights.values()), k=1)[0]
        return encounter_type

    # ------------------------------------------------------------
    # 📜 Generar descripción narrativa del encuentro
    # ------------------------------------------------------------
    def _describe_encounter(self, encounter_type, tone, difficulty):
        templates = {
            "combat": [
                "El aire se vuelve denso; presientes peligro inminente.",
                "Un enemigo surge de entre las sombras, probando vuestro temple.",
                "Los ecos de batalla resuenan antes de que podáis reaccionar."
            ],
            "social": [
                "Un viajero solitario se acerca, buscando conversación y calor.",
                "El grupo encuentra un respiro junto a aliados inesperados.",
                "Risas y voces llenan el aire; por un momento, hay paz."
            ],
            "exploration": [
                "El paisaje se abre ante ustedes, prometiendo secretos olvidados.",
                "Una senda oculta entre la maleza invita a ser explorada.",
                "El mundo parece guardar su aliento, esperando ser descubierto."
            ],
            "mystical": [
                "Un susurro antiguo recorre el aire; la magia parece despertar.",
                "Luces extrañas parpadean a lo lejos, danzando con intención propia.",
                "El velo entre mundos se debilita; algo antiguo desea ser escuchado."
            ],
        }

        base = random.choice(templates[encounter_type])
        tone_adaptations = {
            "dark": "Todo parece teñido de amenaza.",
            "melancholic": "La belleza y la tristeza se entrelazan en el aire.",
            "neutral": "Nada destaca, y sin embargo todo parece significativo.",
            "hopeful": "Un brillo cálido alienta vuestros corazones.",
            "bright": "El ambiente se ilumina con energía y optimismo.",
            "tense": "Cada sonido parece anunciar peligro.",
        }

        diff_text = {1: "trivial", 2: "fácil", 3: "moderado", 4: "difícil", 5: "letal"}
        return f"{base} {tone_adaptations[tone]} (Encuentro {diff_text[difficulty]})."
