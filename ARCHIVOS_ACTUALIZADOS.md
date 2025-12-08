# 📋 Archivos Actualizados - Resumen Completo

## ⚠️ IMPORTANTE

Los cambios están en el **workspace remoto de Cursor**, NO en tu máquina local ni en GitHub.

Tu `main.py` local está desactualizado. Necesitas copiar los archivos actualizados.

---

## 📝 Archivos que Necesitas Actualizar

### 1. `main.py` - ACTUALIZAR COMPLETAMENTE

**Tu versión actual** (líneas 1-10):
```python
from core.handlers.player_handler import register_player_handlers
```

**Versión actualizada** (debe tener líneas 10-17):
```python
from core.handlers.player_handler import register_player_handlers
from core.handlers.narrative_handler import register_narrative_handlers
from core.handlers.campaign_handler import register_campaign_handlers
from core.handlers.conversation_handler import register_conversation_handler
# importa StoryDirector
from core.story_director.story_director import StoryDirector
# importa GameService
from core.services.game_service import GameService
```

**Y en la función `main()`** debe tener:
- `story_director = StoryDirector()`
- `game_service = GameService()`
- `register_narrative_handlers(application)`
- `register_campaign_handlers(application)`
- `register_conversation_handler(application, game_service, campaign_manager)`

---

### 2. Archivos Nuevos que Debes Crear

#### `core/character_builder/point_buy_system.py` - NUEVO
Este archivo NO existe en tu máquina. Debes crearlo.

#### `core/handlers/conversation_handler.py` - NUEVO
Este archivo NO existe en tu máquina. Debes crearlo.

---

### 3. Archivos Modificados

#### `core/campaign/campaign_manager.py`
- Agregar métodos: `get_party_chat_id()`, `get_all_party_chat_ids()`
- Modificar `add_to_active_party()` para aceptar `chat_id`
- Mejorar `_load_state()` para migrar formato antiguo

#### `core/handlers/createcharacter_handler.py`
- Agregar import: `from core.character_builder.point_buy_system import PointBuySystem, ATTRIBUTES`
- Agregar estado: `ATTRIBUTE_METHOD`
- Agregar funciones: `attribute_method_step()`, `attributes_step()` (con botones)
- Modificar `background_step()` para mostrar opciones Point Buy/Array

#### `core/handlers/player_handler.py`
- Modificar `/join` para aceptar `chat_id`
- Agregar límite de 8 jugadores
- Mejorar mensajes

#### `core/services/game_service.py`
- Cambiar `player_id` → `player`
- Agregar métodos: `join_party()`, `get_party()`, `start_game()`, `get_game_state()`
- Mejorar manejo de errores

#### `core/srd_client.py`
- Actualizar endpoints a `/srd/{resource}`
- Mejorar parsing de respuestas

---

## 🔧 Cómo Obtener los Archivos

### Opción 1: Copiar desde Cursor (Más Fácil)

1. En Cursor, abre cada archivo actualizado
2. Selecciona todo (Ctrl+A)
3. Copia (Ctrl+C)
4. Pega en tu máquina local (Ctrl+V)

### Opción 2: Usar Git (Si las ramas están sincronizadas)

```bash
cd C:\SAM\sam-telegram-bot
git fetch origin
git checkout cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
# O mergear los cambios a main
git checkout main
git merge cursor/refactor-bot-repositories-gemini-3-pro-preview-e004
```

### Opción 3: Te doy los archivos completos

Puedo darte el contenido completo de cada archivo para que los copies manualmente.

---

## ✅ Checklist de Verificación

Después de actualizar, verifica:

- [ ] `main.py` tiene `register_conversation_handler`
- [ ] `main.py` tiene `GameService` y `StoryDirector`
- [ ] Existe `core/character_builder/point_buy_system.py`
- [ ] Existe `core/handlers/conversation_handler.py`
- [ ] `core/handlers/createcharacter_handler.py` tiene `PointBuySystem`
- [ ] `core/campaign/campaign_manager.py` tiene `get_party_chat_id()`

---

¿Quieres que te dé los archivos completos para copiar?
