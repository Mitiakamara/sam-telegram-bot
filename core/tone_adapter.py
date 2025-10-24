import os
import json
import random
from typing import Optional

# ============================================================
# 🎭 TONE ADAPTER 5.2b — Silent Mode
# ------------------------------------------------------------
# Adapta el tono narrativo sin insertar etiquetas visibles.
# Usa los datos de /data/emotion/emotional_scale.json
# ============================================================

EMOTIONAL_SCALE_PATH = os.getenv(
    "EMOTIONAL_SCALE_PATH",
    "data/emotion/emotional_scale.json"
)

# ============================================================
# 📘 Cargar configuración emocional
# ============================================================
def load_emotional_scale(path: str = EMOTIONAL_SCALE_PATH) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ToneAdapter] ⚠️ No se encontró {path}. Se usará configuración mínima.")
        return {"scene_adaptation": {"default": "neutral"}, "emotions": {"neutral": {"tone": "Equilibrado"}}}
    except Exception as e:
        print(f"[ToneAdapter] ⚠️ Error al cargar emotional_scale.json: {e}")
        return {}

EMOTIONAL_SCALE = load_emotional_scale()

# ============================================================
# 🔍 Funciones auxiliares
# ============================================================
def get_emotion_for_scene(scene_type: str) -> str:
    """Obtiene la emoción principal asociada al tipo de escena."""
    mapping = EMOTIONAL_SCALE.get("scene_adaptation", {})
    return mapping.get(scene_type, "neutral")

def get_tone_data(emotion: str) -> dict:
    """Devuelve la configuración narrativa de una emoción."""
    return EMOTIONAL_SCALE.get("emotions", {}).get(emotion, {})

def pick_bias_words(emotion: str, n: int = 2) -> list[str]:
    """Selecciona palabras representativas de la emoción."""
    tone_data = get_tone_data(emotion)
    vocab = tone_data.get("vocabulary_bias", [])
    return random.sample(vocab, min(n, len(vocab))) if vocab else []


# ============================================================
# ✨ Función principal silenciosa
# ============================================================
def apply_tone(scene_type: str, text: str, intensity: int = 3) -> str:
    """
    Aplica el tono narrativo según la emoción de la escena,
    sin mostrar etiquetas visibles ni paréntesis.

    scene_type: tipo de escena (exploration, combat, rest, etc.)
    text: texto base del narrador
    intensity: nivel 1–5 (afecta ritmo y matices)
    """
    if not text:
        return ""

    emotion = get_emotion_for_scene(scene_type)
    tone_data = get_tone_data(emotion)
    bias_words = pick_bias_words(emotion, n=random.randint(1, 3))

    adapted_text = text.strip()

    # ============================================================
    # 1️⃣ Variación de ritmo y puntuación según intensidad
    # ============================================================
    if intensity == 1:
        # Tono más neutral, oraciones completas
        adapted_text = adapted_text
    elif intensity == 2:
        # Ligero énfasis emocional: pausas suaves
        adapted_text = adapted_text.replace(".", ",").replace(",", ", ")
    elif intensity == 3:
        # Fluido y descriptivo
        adapted_text = adapted_text.replace(".", "...", 1)
    elif intensity == 4:
        # Ritmo acelerado o expectante
        adapted_text = adapted_text.replace(".", "...").replace(",", "...")
        if not adapted_text.endswith("..."):
            adapted_text += "..."
    elif intensity >= 5:
        # Clímax emocional: frases cortas, tensión o exaltación
        adapted_text = adapted_text.upper()
        if not adapted_text.endswith("!"):
            adapted_text += "!"

    # ============================================================
    # 2️⃣ Inserción natural de sesgos emocionales
    # ============================================================
    if bias_words and intensity >= 2:
        insert_word = random.choice(bias_words)
        # Inserta la palabra clave en una zona fluida del texto
        parts = adapted_text.split()
        if len(parts) > 6:
            insert_index = random.randint(3, len(parts) - 2)
            parts.insert(insert_index, insert_word)
            adapted_text = " ".join(parts)

    # ============================================================
    # 3️⃣ Ajuste final: estilo narrativo
    # ============================================================
    style_hint = tone_data.get("style", "")
    if intensity >= 4 and "frases cortas" in style_hint:
        # Simula respiración rápida o tensión: oraciones más breves
        adapted_text = adapted_text.replace(",", ".").replace("..", ".")
    elif intensity <= 2 and "pausada" in style_hint:
        # Ritmo pausado para escenas melancólicas
        adapted_text = adapted_text.replace(".", ",").replace("...", ",")

    return adapted_text.strip()


# ============================================================
# 🧪 Prueba manual (silenciosa)
# ============================================================
if __name__ == "__main__":
    demo_text = "El grupo avanza por el sendero nevado, el viento corta sus rostros."
    for scene in ["exploration", "combat", "rest", "revelation", "victory"]:
        print(f"\nScene: {scene}")
        for lvl in range(1, 6):
            out = apply_tone(scene, demo_text, lvl)
            print(f"  Intensity {lvl}: {out}")
