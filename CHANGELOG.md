# 🧾 CHANGELOG – SAM (Storytelling AI Master)
## Sistema SRD 5.1.2 para Telegram
---

### [v7.6.1] – 2025-11-04
**Estado:** ✅ Stable Release  
**Tipo:** Integración final del sistema SRD + Telegram Bot funcional.

#### ✨ Nuevo
- Integración total del `CampaignManager` con guardado automático de progreso.
- Implementación del `TransitionEngine` (motor de cambio de escena).
- Versión final de `StoryDirector` con interfaz pública estable:
  - `create_character()`
  - `join_player()`
  - `render_current_scene()`
  - `trigger_event()`
  - `get_player_status()`
  - `get_campaign_progress()`
  - `restart_campaign()`
  - `load_campaign()`
- Consolidación de `main.py` con 8 comandos oficiales:
  - `/start`, `/createcharacter`, `/join`, `/scene`,
    `/event`, `/status`, `/progress`, `/restart`, `/loadcampaign`.
- Simplificación del `renderer.py`.
- Documentación técnica (`README.md`, `package.json`, `CHANGELOG.md`).

---

### [v7.5.0] – 2025-11-03
- Integración del `CampaignManager` (persistencia de campaña y quests).
- Guardado automático de `campaign_state.json`.
- Sistema de estado de campaña consultable vía `/progress`.
- Módulo `data/campaign_state.json` con soporte multi-campaña.

---

### [v7.4.0] – 2025-11-02
- Implementación del `TransitionEngine` para transiciones narrativas automáticas.
- Nuevas plantillas de escenas (`progress_scene`, `triumph_scene`, etc.).
- Integración de emoción y evento → próxima escena.

---

### [v7.3.0] – 2025-11-01
- Conexión entre `AttributeAnalyzer` y `ToneAdapter`.
- Adaptación del tono narrativo basado en atributos del grupo.
- Primeras pruebas de coherencia narrativa entre escenas.

---

### [v7.2.0] – 2025-10-31
- Integración de atributos con el motor narrativo.
- Estructura de clases para `ToneAdapter`, `SceneManager` y `EmotionalTracker`.

---

### [v7.0.0] – 2025-10-30
- Inicio de la Fase 7: compatibilidad SRD 5.1.2.
- Adaptación del sistema a campañas precreadas SRD.
- Primeros comandos de Telegram `/start`, `/join`, `/status`.

---

### [v6.x] – Octubre 2025
- Arquitectura base: `SceneManager`, `Renderer`, `ToneAdapter`, `EmotionalTracker`.
- Implementación del pipeline emocional y sistema de escenas adaptativas.

---

### [v5.x] – Septiembre 2025
- Introducción del sistema de tono y emociones.
- Primeras pruebas de interacción narrativa entre jugador y SAM.

---

### [v1–4.x] – Julio–Agosto 2025
- Base del proyecto: conexión a Telegram, manejo de sesiones, almacenamiento local.

---

© 2025 Francisco Correa Alfaro  
**SAM – Storytelling AI Master SRD 5.1.2**
