# 📥 Instrucciones para Hacer Pull

## ✅ Cambios Pusheados a GitHub

He hecho push de los cambios a GitHub en la rama:
`cursor/refactor-bot-repositories-gemini-3-pro-preview-e004`

## 🔄 Cómo Obtener los Cambios en Tu Máquina Local

### Opción 1: Hacer Pull de la Rama Específica

En PowerShell en tu máquina local:

```bash
cd C:\SAM\sam-telegram-bot

# Obtener todas las ramas remotas
git fetch origin

# Ver las ramas disponibles
git branch -a

# Cambiar a la rama con los cambios
git checkout cursor/refactor-bot-repositories-gemini-3-pro-preview-e004

# O crear una rama local desde la remota
git checkout -b local-updates origin/cursor/refactor-bot-repositories-gemini-3-pro-preview-e004

# Ver los cambios
git log --oneline -5
```

### Opción 2: Mergear los Cambios a Main

Si quieres los cambios en tu rama `main`:

```bash
cd C:\SAM\sam-telegram-bot

# Asegúrate de estar en main
git checkout main

# Obtener las ramas remotas
git fetch origin

# Mergear los cambios de la otra rama
git merge origin/cursor/refactor-bot-repositories-gemini-3-pro-preview-e004

# Si hay conflictos, resuélvelos y luego:
git add .
git commit -m "Merge updates from cursor branch"
```

### Opción 3: Hacer Pull Directo (Si la Rama Existe Localmente)

```bash
cd C:\SAM\sam-telegram-bot

# Crear y cambiar a la rama
git checkout -b cursor-updates origin/cursor/refactor-bot-repositories-gemini-3-pro-preview-e004

# O si ya existe localmente:
git checkout cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
git pull origin cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
```

## ✅ Verificación

Después del pull, verifica que tienes los cambios:

1. **`main.py`** debe tener:
   ```python
   from core.handlers.conversation_handler import register_conversation_handler
   from core.services.game_service import GameService
   ```

2. **Debe existir:**
   - `core/character_builder/point_buy_system.py`
   - `core/handlers/conversation_handler.py`

3. **Verifica con:**
   ```bash
   git log --oneline -1
   # Debe mostrar el commit con "point buy system"
   ```

## 🚀 Después del Pull

Una vez que tengas los cambios:

```bash
# Si estás en otra rama y quieres mergear a main:
git checkout main
git merge cursor/refactor-bot-repositories-gemini-3-pro-preview-e004

# O trabajar directamente en la rama con los cambios
git checkout cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
```

---

**Comando rápido:**
```bash
cd C:\SAM\sam-telegram-bot
git fetch origin
git checkout -b updates origin/cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
```
