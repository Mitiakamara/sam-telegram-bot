# 🎞️ S.A.M. – Flujo Narrativo Adaptativo

Este documento describe el flujo completo de información entre los módulos narrativos del sistema **S.A.M. (Story Adaptive Machine)**, que permite una narrativa coherente, emocional y dinámica en partidas de D&D 5e.

---

## ⚙️ Arquitectura General

```text
┌───────────────────────────────┐
│         PLAYER INPUT          │
│ (mensajes, acciones, emociones)│
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│         TELEGRAM BOT          │
│  (/join, /continue, texto, …) │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│          ORCHESTRATOR         │
│  🔗 Coordina todo el flujo     │
│  - Llama GameService           │
│  - Controla StoryDirector      │
│  - Sincroniza MoodManager      │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│          GAMESERVICE          │
│  🎲 Lógica jugable y reglas D&D│
│  - Recibe acción del jugador  │
│  - Devuelve resultado narrativo│
│    {"action": ..., "emotion": ...}│
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│         DIRECTORLINK          │
│  🧠 Interpreta resultado       │
│  - Lee "emotion", "outcome"   │
│  - Ajusta MoodManager         │
│  - Genera texto adaptado      │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│        STORY DIRECTOR         │
│  🎬 Motor narrativo adaptativo │
│  - Crea/cierra escenas         │
│  - Coordina transición tonal   │
│  - Integra ToneAdapter y Mood  │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│          MOOD MANAGER         │
│  🎭 Gestor de tono global      │
│  - Calcula mood global         │
│  - Guarda histórico            │
│  - Alinea género y emoción     │
│  - Sugiere transiciones        │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│          TONE ADAPTER         │
│  🎨 Ajusta lenguaje y estilo   │
│  según emoción e intensidad    │
│  - Usa data/emotion/emotional_scale.json│
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│           RENDERER            │
│  🗨️ Da formato al texto final │
│  - Markdown/Telegram friendly  │
│  - Envía salida al bot         │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│         TELEGRAM BOT          │
│  💬 Envía texto al jugador     │
│  (ajustado al clima narrativo) │
└───────────────────────────────┘
