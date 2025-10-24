import os
import json
import random
from typing import Optional

# ============================================================
# 🎭 TONE ADAPTER 5.2b+
# ------------------------------------------------------------
# Aplica el tono narrativo adaptativo a textos narrativos
# usando los parámetros definidos en /data/emotion/emotional_scale.json
# ============================================================

# Ruta por defecto del archivo de configuración emocional
EMOTIONAL_SCALE_PATH = os.getenv(
    "EMOTIONAL_SCALE_PATH",
    "data/emotion/emotional_scale.json"
)

# ============================================================
# 📘 Cargar la escala emocional
# ============================================================
def load_emotional_scale(path: str = EMOTIONAL_SCALE_PATH) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"[ToneAdapter] ⚠️ No se encontró {path}. Usando configuración por defecto.")
        return {"scene_adaptation": {"default": "neutral"}, "emotions": {"neutral": {"tone": "Neutro"}}}
    except Exception as e:
        print(f"[ToneAdapter] ⚠️ Error al cargar emotional_scale.json: {e}")
        return {}

EMOTIONAL_SCALE = load_emotional_scale()


# ============================================================
# 🔍 Funciones auxiliares
# ============================================================
def get_emotion_for_scene(scene_type: str) -> str:
    """Devuelve la emoción asociada al tipo de escena."""
    mapping = EMOTIONAL_SCALE.get("scene_adaptation", {})
    return mapping.get(scene_type, "neutral")


def get_tone_data(emotion: str) -> dict:
    """Devuelve el bloque de datos de tono correspondiente a una emoción."""
    return EMOTIONAL_SCALE.get("emotions", {}).get(emotion, {})


def get_random_bias_words(emotion: str, n: int = 2) -> list[str]:
    """Selecciona palabras asociadas a la emoción para añadir matices al texto."""
    tone_data = get_tone_data(emotion)
    vocab = tone_data.get("vocabulary_bias", [])
    return random.sample(vocab, min(n, len(vocab))) if vocab else []


# ============================================================
# ✨ Función principal de adaptación narrativa
# ============================================================
def apply_tone(scene_type: str, text: str, intensity: int = 3) -> str:
    """
    Aplica el tono narrativo adaptativo según la emoción del tipo de escena.

    Parámetros:
        - scene_type: tipo de escena (exploration, combat, rest, etc.)
        - text: texto base a adaptar
        - intensity: nivel 1–5 de fuerza emocional

    Retorna:
        - Texto con tono narrativo ajustado.
    """
    if not text:
        return ""

    # 1️⃣ Obtener emoción y configuración de tono
    emotion = get_emotion_for_scene(scene_type)
    tone_data = get_tone_data(emotion)

    tone_label = tone_data.get("tone", "Neutral")
    style_hint = tone_data.get("style", "")
    bias_words = get_random_bias_words(emotion, n=random.randint(1, 3))

    adapted_text = text.strip()

    # 2️⃣ Adaptar ritmo y puntuación según intensidad
    if intensity >= 4:
        adapted_text = adapted_text.replace(".", "...")
    if intensity >= 5:
        adapted_text = adapted_text.upper()

    # 3️⃣ Introducir sesgos léxicos (palabras clave de emoción)
    if bias_words:
        # Inserta una o dos palabras sesgadas al final para matizar el tono
        adapted_text += f" ({', '.join(bias_words)})"

    # 4️⃣ Prefijo de tono (solo visible si intensidad >= 3)
    prefix = ""
    if intensity >= 3:
        prefix = f"[{tone_label}] "

    # 5️⃣ Ensamblar resultado final
    final_text = f"{prefix}{adapted_text}"

    # 6️⃣ (Opcional) Registrar el estilo o color narrativo
    if intensity >= 4 and style_hint:
        final_text += f" — {style_hint}"

    return final_text


# ============================================================
# 🧪 Modo de prueba manual
# ============================================================
if __name__ == "__main__":
    demo_text = "El grupo avanza por el sendero nevado, el viento corta sus rostros."
    scenes = ["exploration", "combat", "rest", "revelation", "victory", "defeat"]

    print("=== DEMO TONE ADAPTER ===")
    for s in scenes:
        print(f"\nScene type: {s}")
        for lvl in range(2, 6):
            result = apply_tone(s, demo_text, intensity=lvl)
            print(f"  Intensity {lvl}: {result}")
