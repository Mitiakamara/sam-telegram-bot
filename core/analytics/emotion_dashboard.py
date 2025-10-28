import os
import json
from datetime import datetime

# ================================================================
# 📊 EMOTIONAL ANALYTICS DASHBOARD (Fase 6.28)
# ================================================================
# Reúne métricas dispersas (escenas, tono, blends, grupo, proyección,
# refuerzos) y genera un panel en Markdown (y opcional HTML).
# ================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "../../data/emotion")

FILES = {
    "scene_history": os.path.join(BASE_DIR, "scene_history.json"),
    "emotional_state": os.path.join(BASE_DIR, "emotional_state.json"),
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

def _fmt_pct(x):
    try:
        return f"{100*float(x):.0f}%"
    except Exception:
        return "-"

def _list_to_sparkline(series, min_len=5, max_len=24):
    # ASCII sparkline simple (▁▂▃▄▅▆▇█)
    if not series:
        return "—"
    bars = "▁▂▃▄▅▆▇█"
    vals = series[-max_len:]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1e-9
    scaled = [int((v - lo) / span * (len(bars)-1)) for v in vals]
    s = "".join(bars[i] for i in scaled)
    return s if len(s) >= min_len else s.ljust(min_len, "·")

def _last(items, default=None):
    return items[-1] if items else default

class EmotionDashboard:
    def __init__(self):
        self.now = datetime.utcnow().isoformat()

        # Cargas suaves (no rompen si falta algún archivo)
        self.scene_history = _load_json(FILES["scene_history"], {"scenes": []})
        self.emotional_state = _load_json(FILES["emotional_state"], {"summary": {}, "vector": {}})
        self.tone_memory = _load_json(FILES["tone_memory"], {"imprint": {}, "history": []})
        self.collective = _load_json(FILES["collective_memory"], {"patterns": {}, "history": []})
        self.projection = _load_json(FILES["world_projection"], {"history": []})
        self.reinforcement = _load_json(FILES["reinforcement"], {"reinforcement_profile": {}, "history": []})

    # ------------------------------------------------------------
    # 🔎 Extractores de métricas
    # ------------------------------------------------------------
    def _scene_metrics(self):
        scenes = self.scene_history.get("scenes", [])
        total = len(scenes)
        emotions = [s.get("dominant_emotion", "neutral") for s in scenes]
        intens = [float(s.get("emotion_intensity", 0.0)) for s in scenes if s.get("emotion_intensity") is not None]
        last_emotion = emotions[-1] if emotions else "—"
        spark = _list_to_sparkline(intens)
        return total, last_emotion, spark

    def _tone_metrics(self):
        v = self.emotional_state.get("vector", {})
        tone = v.get("tone_label", self.emotional_state.get("summary", {}).get("tone_label", "neutral"))
        trend = v.get("state", "stable")
        blend = self.tone_memory.get("imprint", {}).get("dominant_signature", "—")
        dist = self.tone_memory.get("imprint", {}).get("blend_distribution", {})
        # top-3 blends
        top = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)[:3]
        top_str = ", ".join(f"{k}:{_fmt_pct(p)}" for k, p in top) if top else "—"
        return tone, trend, blend, top_str

    def _group_metrics(self):
        pat = self.collective.get("patterns", {})
        dom = pat.get("dominant_emotion", "neutral")
        coh = pat.get("avg_cohesion", 0.0)
        trend = pat.get("trend", "neutral")
        # spark de cohesión
        coh_series = [float(h.get("cohesion", 0.0)) for h in self.collective.get("history", [])]
        spark = _list_to_sparkline(coh_series)
        return dom, coh, trend, spark

    def _projection_metrics(self):
        last = _last(self.projection.get("history", []), {})
        return {
            "predicted_trend": last.get("predicted_trend", "—"),
            "tone_shift": last.get("tone_shift", "—"),
            "event_bias": last.get("event_bias", "—"),
            "desc": last.get("description", "—")
        }

    def _reinforcement_metrics(self):
        prof = self.reinforcement.get("reinforcement_profile", {}).get("encounter_types", {})
        if not prof:
            return "—"
        items = sorted(prof.items(), key=lambda kv: kv[1]["avg_delta"], reverse=True)
        return ", ".join(f"{k}:{v['avg_delta']:+.2f}" for k, v in items)

    # ------------------------------------------------------------
    # 🧾 Render (Markdown / HTML)
    # ------------------------------------------------------------
    def generate_markdown(self) -> str:
        total, last_emotion, spark = self._scene_metrics()
        tone, trend, blend, top_blends = self._tone_metrics()
        g_dom, g_coh, g_trend, g_spark = self._group_metrics()
        proj = self._projection_metrics()
        reinforce = self._reinforcement_metrics()

        md = []
        md.append(f"# 📊 Emotional Dashboard — {self.now} UTC\n")
        md.append("## 🎬 Escenas & Intensidad")
        md.append(f"- Total de escenas: **{total}**")
        md.append(f"- Última emoción dominante: **{last_emotion}**")
        md.append(f"- Intensidad (sparkline): `{spark}`\n")

        md.append("## 🎭 Tono Global & Firma Tonal")
        md.append(f"- Tono actual: **{tone}**  | Tendencia: **{trend}**")
        md.append(f"- Firma tonal dominante (blends): **{blend}**")
        md.append(f"- Top blends: {top_blends}\n")

        md.append("## 🤝 Estado Emocional del Grupo")
        md.append(f"- Emoción dominante histórica: **{g_dom}**  | Cohesión media: **{g_coh:.2f}**  | Tendencia: **{g_trend}**")
        md.append(f"- Cohesión (sparkline): `{g_spark}`\n")

        md.append("## 🔮 Proyección del Mundo (Worldstate)")
        md.append(f"- Tendencia prevista: **{proj['predicted_trend']}**")
        md.append(f"- Matiz tonal anticipado: **{proj['tone_shift']}**")
        md.append(f"- Sesgo narrativo esperado: **{proj['event_bias']}**")
        md.append(f"- Nota: {proj['desc']}\n")

        md.append("## ♻️ Refuerzo Emocional por Tipo de Encuentro")
        md.append(f"- Impacto medio por tipo (Δ cohesión): {reinforce}\n")

        md.append("> _Este panel resume el estado emocional persistente y proyectado de la campaña. "
                  "Úsalo para ajustar ritmo, dificultad y el tipo de escenas/encuentros._")
        return "\n".join(md)

    def save_html(self, out_path: str = None) -> str:
        md = self.generate_markdown()
        html = (
            "<!doctype html><meta charset='utf-8'>"
            "<style>body{font-family:system-ui,Segoe UI,Arial;max-width:900px;margin:40px auto;line-height:1.5}"
            "code{background:#f6f8fa;padding:.2em .4em;border-radius:4px}</style>"
            f"<article>{md.replace('\n','<br/>')}</article>"
        )
        out_path = out_path or os.path.join(BASE_DIR, "dashboard.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        return out_path
