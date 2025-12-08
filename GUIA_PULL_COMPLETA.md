# 📥 Guía Completa: Cómo Hacer Pull desde Git

## ✅ Estado Actual

Los cambios están en GitHub en la rama:
**`cursor/refactor-bot-repositories-gemini-3-pro-preview-e004`**

## 🔄 Pasos para Obtener los Cambios

### Paso 1: Abre PowerShell en tu máquina local

```bash
cd C:\SAM\sam-telegram-bot
```

### Paso 2: Obtén todas las ramas remotas

```bash
git fetch origin
```

Esto descarga información sobre todas las ramas en GitHub sin modificar tus archivos locales.

### Paso 3: Ver las ramas disponibles

```bash
git branch -a
```

Deberías ver:
- `main` (tu rama local actual)
- `remotes/origin/main`
- `remotes/origin/cursor/refactor-bot-repositories-gemini-3-pro-preview-e004` ← Esta tiene los cambios

### Paso 4: Obtener los cambios

**Opción A: Trabajar en la rama con los cambios**
```bash
# Crear una rama local desde la remota
git checkout -b updates origin/cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
```

**Opción B: Mergear los cambios a main (Recomendado)**
```bash
# Asegúrate de estar en main
git checkout main

# Mergear los cambios de la otra rama
git merge origin/cursor/refactor-bot-repositories-gemini-3-pro-preview-e004

# Si hay conflictos, resuélvelos manualmente
# Luego:
git add .
git commit -m "Merge: Add point buy system and multi-player features"
```

**Opción C: Hacer pull directo (si la rama ya existe localmente)**
```bash
git checkout cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
git pull origin cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
```

## ✅ Verificación

Después del pull/merge, verifica:

1. **Abre `main.py`** y busca:
   ```python
   from core.handlers.conversation_handler import register_conversation_handler
   ```
   Si lo encuentras, ✅ los cambios están ahí.

2. **Verifica que existen estos archivos:**
   ```bash
   ls core/handlers/conversation_handler.py
   ls core/character_builder/point_buy_system.py
   ```

3. **Ver el último commit:**
   ```bash
   git log --oneline -1
   ```

## 🚀 Comandos Rápidos (Copia y Pega)

### Para mergear a main:
```bash
cd C:\SAM\sam-telegram-bot
git fetch origin
git checkout main
git merge origin/cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
```

### Para trabajar en la rama con cambios:
```bash
cd C:\SAM\sam-telegram-bot
git fetch origin
git checkout -b updates origin/cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
```

## ⚠️ Si Hay Conflictos

Si git dice que hay conflictos:

1. Abre los archivos con conflictos
2. Busca las marcas `<<<<<<<`, `=======`, `>>>>>>>`
3. Elige qué código mantener
4. Elimina las marcas de conflicto
5. Guarda el archivo
6. Ejecuta:
   ```bash
   git add .
   git commit -m "Resolve merge conflicts"
   ```

## 📝 Archivos que Deberías Ver

Después del pull, estos archivos deben existir/modificarse:

**Nuevos:**
- ✅ `core/character_builder/point_buy_system.py`
- ✅ `core/handlers/conversation_handler.py`

**Modificados:**
- ✅ `main.py` (debe tener más imports)
- ✅ `core/campaign/campaign_manager.py`
- ✅ `core/handlers/createcharacter_handler.py`
- ✅ `core/handlers/player_handler.py`
- ✅ `core/services/game_service.py`
- ✅ `core/srd_client.py`

---

**¿Listo?** Ejecuta los comandos y me dices si funcionó! 🚀
