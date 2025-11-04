# 🧙‍♂️ SAM – Storytelling AI Master (SRD 5.1.2)

Versión: **v7.6.1 Stable**  
Tipo de proyecto: *AI Dungeon Master para Telegram basado en SRD 5.1.2*  
Desarrollado por: **Francisco Correa Alfaro**

---

## 🎯 Objetivo

SAM es un **Dungeon Master AI** diseñado para dirigir partidas de *Dungeons & Dragons* compatibles con el **SRD 5.1.2 (Creative Commons)**.  
Utiliza campañas precreadas, mantiene coherencia narrativa y permite crear personajes directamente desde Telegram.

---

## ⚙️ Características Principales

| Módulo | Funcionalidad |
|--------|----------------|
| 🎬 **StoryDirector** | Orquesta la narrativa, maneja escenas, emociones y tono. |
| 🧠 **ToneAdapter** | Ajusta la voz narrativa según emoción y rasgos del grupo. |
| ❤️ **EmotionalTracker** | Calcula la emoción global y reacciones adaptativas. |
| 🗺️ **SceneManager** | Crea escenas a partir de plantillas SRD. |
| 🔁 **TransitionEngine** | Determina la siguiente escena según evento y emoción. |
| 🏕️ **CampaignManager** | Guarda el progreso y estado de la campaña. |
| 🧙‍♂️ **Renderer** | Punto de salida textual (texto narrativo final). |

---

## 💬 Comandos disponibles (Telegram)

| Comando | Descripción |
|----------|--------------|
| `/start` | Mensaje de bienvenida. |
| `/createcharacter <nombre> [clase] [raza]` | Crea un personaje usando el sistema SRD 5.1.2. |
| `/join` | Une al jugador a la campaña activa. |
| `/scene` | Muestra o continúa la escena actual. |
| `/event <tipo>` | Ejecuta un evento narrativo (combat_victory, setback, rally...). |
| `/status` | Muestra el estado emocional y escena actual. |
| `/progress` | Muestra el estado de la campaña (capítulo, quests, grupo). |
| `/restart` | Reinicia la campaña actual desde el inicio. |
| `/loadcampaign <slug>` | Carga otra campaña SRD precreada. (Solo admin). |

---

## 🧩 Estructura de Carpetas

