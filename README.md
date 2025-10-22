# S.A.M. Telegram Bot (v0.1)

## Descripción
Bot de Telegram que permite interactuar con el Dungeon Master AI S.A.M. enviando acciones y recibiendo respuestas desde la Game API.

## Instalación

1. Crear entorno virtual e instalar dependencias:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configurar variables de entorno en `.env`:
   ```ini
   BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   GAME_API_URL=http://localhost:9000
   ```

3. Ejecutar el bot:
   ```bash
   python main.py
   ```

## Comandos disponibles
- `/start` — Mensaje de bienvenida.
- `/join` — Une al jugador a la partida.
- `/state` — Muestra el estado actual.
- Mensajes libres — Interpretados como acciones dentro del juego.
