import os
import json
from datetime import datetime
from core.analytics.emotion_dashboard import EmotionDashboard

# ================================================================
# 📜 NARRATIVE REPORT EXPORTER (Fase 6.29)
# ================================================================
# Crea un informe completo de campaña/sesión en formato Markdown,
# combinando narrativa, métricas emocionales y resúmenes.
# ================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")

FILES = {
    "scene_history": os.path.join(BASE_DIR, "scene_history.json"),
    "tone_memory": os.path.join(BASE_DIR, "tone_memory.json"),
    "collective_memory": os.path.join(BASE_DIR, "collective_emotional_memory.json"),
    "world_projection": os.path.join(BASE_DIR, "worldstate_projection.json"),
    "reinforcement": os.path.join(BASE_DIR, "emotional_reinforcement.json"),
}


def _load_json(path, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default


class NarrativeReport:
    def __init__(self):
        self.now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        self.scene_history = _load_json(FILES["scene_history"], {"scenes": []})
        self.tone_memory = _load_json(FILES["tone_memory"], {"imprint": {}, "history": []})
        self.collective = _load_json(FILES["collective_memory"], {"patterns": {}, "history": []})
        self.projection = _load_json(FILES["world_projection"], {"history": []})
        self.reinforcement = _load_json(FILES["reinforcement"], {"history": []})
        self.dashboard = EmotionDashboard().generate_markdown()

    # ------------------------------------------------------------
    # 🧠 Extraer highlights narrativos
    # ------------------------------------------------------------
    def _scene_highlights(self):
        """Selecciona las escenas más relevantes (emociones fuertes o cambios de tono)."""
        scenes = self.scene_history.get("scenes", [])
        if not scenes:
            return ["_No hay escenas registradas._"]

        highlights = []
        for s in scenes[-8:]:  # últimas escenas
            title = s.get("title", "Escena sin título")
            emo = s.get("dominant_emotion", "neutral")
            tone = s.get("tone", "neutral")
            desc = s.get("description", "")
            highlights.append(f"### 🎬 {title}\n**Tono:** {tone} | **Emoción:** {emo}\n> {desc}")
        return highlights

    def _collective_summary(self):
        pat = self.collective.get("patterns", {})
        return (
            f"- Emoción dominante grupal: **{pat.get('dominant_emotion', 'neutral')}**\n"
            f"- Cohesión media: **{pat.get('avg_cohesion', 0.0):.2f}**\n"
            f"- Tendencia: **{pat.get('trend', 'neutral')}**"
        )

    def _tone_signature(self):
        imp = self.tone_memory.get("imprint", {})
        sig = imp.get("dominant_signature", "neutral")
        dist = imp.get("blend_distribution", {})
        dist_text = ", ".join(f"{k}:{v:.2f}" for k, v in dist.items()) if dist else "sin datos"
        return f"- Firma tonal dominante: **{sig}**\n- Distribución de blends: {dist_text}"

    def _projection_summary(self):
        last = self.projection.get("history", [{}])[-1]
        return (
            f"- Tendencia futura: **{last.get('predicted_trend', '—')}**\n"
            f"- Matiz tonal anticipado: **{last.get('tone_shift', '—')}**\n"
            f"- Sesgo narrativo: **{last.get('event_bias', '—')}**\n"
            f"> {last.get('description', '—')}"
        )

    def _reinforcement_summary(self):
        prof = self.reinforcement.get("reinforcement_profile", {}).get("encounter_types", {})
        if not prof:
            return "_No hay datos de refuerzo aún._"
        lines = [f"- {k}: Δ cohesión promedio {v['avg_delta']:+.2f} ({v['trend']})" for k, v in prof.items()]
        return "\n".join(lines)

    # ------------------------------------------------------------
    # 🧾 Generar el informe completo
    # ------------------------------------------------------------
    def generate_markdown_report(self) -> str:
        parts = [
            f"# 📜 Informe Narrativo de Campaña\n**Generado:** {self.now}\n\n",
            "## 🎞️ Resumen Narrativo",
            *self._scene_highlights(),
            "\n## 🎭 Tono y Firma Emocional",
            self._tone_signature(),
            "\n## 🤝 Memoria Emocional Colectiva",
            self._collective_summary(),
            "\n## 🔮 Proyección del Mundo",
            self._projection_summary(),
            "\n## ♻️ Refuerzo Emocional",
            self._reinforcement_summary(),
            "\n## 📊 Dashboard Emocional Resumido",
            self.dashboard,
            "\n> _Informe generado automáticamente por S.A.M. — Emotional Story Engine._"
        ]
        return "\n".join(parts)

    # ------------------------------------------------------------
    # 💾 Guardar en archivo
    # ------------------------------------------------------------
    def save_report(self, output_dir: str = BASE_DIR) -> str:
        md = self.generate_markdown_report()
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"narrative_report_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        return path

