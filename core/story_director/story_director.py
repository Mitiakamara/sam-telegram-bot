import random
from datetime import datetime

# ================================================================
# 🎬 STORY DIRECTOR
# ================================================================
# Motor de decisiones narrativas adaptativas.
# Integra Emotional Analytics (Fase 6.11)
# para ajustar tipo de próxima escena, ritmo y tono.
# ================================================================

from core.emotion.emotional_analytics import (
    emotional_trend_score,
    compute_tone_score,
    emotion_frequency,
)

class StoryDirector:
    def __init__(self):
        self.last_outcome = "mixed"
        self.last_decision = {}
        self.scene_counter = 0

    # ------------------------------------------------------------
    # 🔮 Selección del tipo de escena según emociones recientes
    # ------------------------------------------------------------
    def decide_next_scene_type(self) -> str:
        """
        Analiza las métricas emocionales recientes y elige
        el tipo de próxima escena (progress, tension, triumph, setback, complication).
        """
        trend = emotional_trend_score(window=5)
        tone = compute_tone_score()
        freq = emotion_frequency()

        trend_dir = trend.get("direction", "stable")
        tone_label = tone.get("label", "neutral")
        dominant_emotion = max(freq, key=freq.get) if freq else "neutral"

        next_type = "progress"

        # --- Reglas básicas de adaptación ---
        if tone_label in ["dark", "melancholic"] and trend_dir == "falling":
            next_type = "triumph"  # aligerar el tono con una escena positiva
        elif tone_label in ["bright", "hopeful"] and trend_dir == "rising":
            next_type = random.choice(["tension", "complication"])  # introducir desafío
        elif dominant_emotion == "fear":
            next_type = random.choice(["setback", "tension"])
        elif dominant_emotion == "joy":
            next_type = random.choice(["progress", "triumph"])
        elif dominant_emotion == "anger":
            next_type = random.choice(["complication", "tension"])
        elif dominant_emotion == "sadness":
            next_type = random.choice(["progress", "hopeful_recovery"])
        else:
            next_type = random.choice(["progress", "tension", "complication"])

        self.last_decision = {
            "timestamp": datetime.utcnow().isoformat(),
            "trend": trend,
            "tone": tone,
            "dominant_emotion": dominant_emotion,
            "next_scene_type": next_type,
        }

        print(f"\n🎭 [StoryDirector] Próxima escena sugerida → {next_type.upper()}")
        print(f"    Tendencia: {trend_dir}, Tono: {tone_label}, Emoción dominante: {dominant_emotion}")

        return next_type

    # ------------------------------------------------------------
    # ⚖️ Determina resultado narrativo de la escena actual
    # ------------------------------------------------------------
    def evaluate_scene_outcome(self, player_success: float):
        """
        Determina el resultado narrativo general de la escena (éxito, fracaso o mixto).
        player_success: valor entre 0 y 1
        """
        if player_success >= 0.7:
            self.last_outcome = "success"
        elif player_success <= 0.3:
            self.last_outcome = "failure"
        else:
            self.last_outcome = "mixed"

        print(f"📖 [StoryDirector] Resultado de escena: {self.last_outcome}")
        return self.last_outcome

    # ------------------------------------------------------------
    # 🧩 Genera resumen narrativo adaptativo
    # ------------------------------------------------------------
    def generate_summary_prompt(self, current_scene):
        """
        Genera una descripción que combine emoción, tono y progreso.
        """
        decision = self.last_decision or {}
        tone_label = decision.get("tone", {}).get("label", "neutral")
        emotion = decision.get("dominant_emotion", "neutral")
        next_type = decision.get("next_scene_type", "progress")

        prompt = (
            f"La historia progresa hacia una nueva etapa de tipo '{next_type}', "
            f"con un tono {tone_label} y una emoción dominante de {emotion}. "
            f"La última escena ('{current_scene.title}') concluyó con resultado {self.last_outcome}."
        )
        return prompt

    # ------------------------------------------------------------
    # 🧠 Interfaz principal para Orchestrator
    # ------------------------------------------------------------
    def process_input(self, user_input: str, current_scene: dict, emotional_state: dict):
        """
        Procesa la entrada del jugador y genera la siguiente escena adaptada.
        Este método sirve como punto de entrada unificado para el Orchestrator.
        """
        # 1️⃣ Analiza el estado emocional y decide tipo de próxima escena
        next_type = self.decide_next_scene_type()

        # 2️⃣ Simula resultado de escena con un valor aleatorio (luego se podrá vincular con tiradas)
        player_success = random.uniform(0.2, 0.9)
        outcome = self.evaluate_scene_outcome(player_success)

        # 3️⃣ Genera resumen adaptativo
        class TempScene:
            title = current_scene.get("title", "Escena sin título")

        narrative_prompt = self.generate_summary_prompt(TempScene())

        # 4️⃣ Crea salida narrativa para el Orchestrator
        return {
            "description": narrative_prompt,
            "next_scene_type": next_type,
            "outcome": outcome,
            "tone": emotional_state.get("tone", "neutral"),
            "dominant_emotion": emotional_state.get("dominant_emotion", "neutral"),
        }


# ------------------------------------------------------------
# 🧪 DEMO LOCAL
# ------------------------------------------------------------
if __name__ == "__main__":
    sd = StoryDirector()
    print("🎬 Ejecutando demo de Story Director con Emotional Analytics...\n")

    next_scene = sd.decide_next_scene_type()
    sd.evaluate_scene_outcome(0.8)

    class DummyScene:
        title = "El puente roto sobre el abismo"

    prompt = sd.generate_summary_prompt(DummyScene())
    print("\n🧾 Prompt narrativo generado:")
    print(prompt)
