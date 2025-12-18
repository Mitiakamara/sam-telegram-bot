# 🎮 Adventure Loading System

## ✅ Implementado

### 1. **AdventureLoader** (`core/adventure/adventure_loader.py`)
- Carga aventuras desde archivos JSON en `adventures/`
- Valida estructura de datos
- Busca escenas por ID
- Lista aventuras disponibles

**Métodos principales:**
- `load_adventure(slug)` - Carga una aventura por nombre
- `list_available_adventures()` - Lista todas las aventuras disponibles
- `validate_adventure(data)` - Valida estructura JSON
- `find_scene_by_id(adventure_data, scene_id)` - Busca escena específica
- `get_initial_scene(adventure_data)` - Obtiene escena inicial

### 2. **StoryDirector Integration**
- `load_campaign(slug)` ahora carga aventuras reales desde JSON
- `get_current_scene()` detecta si hay aventura cargada
- `render_current_scene()` muestra narración y opciones de aventuras

**Estado guardado:**
- `adventure_data` - Datos completos de la aventura
- `current_scene_id` - ID de la escena actual
- `adventure_scenes` - Lista de todas las escenas
- `campaign_title` - Título de la aventura

### 3. **Comando `/loadcampaign` Mejorado**
- Sin argumentos: Lista aventuras disponibles
- Con argumento: Carga la aventura especificada
- Muestra información detallada (título, número de escenas, escena inicial)

## 📋 Formato de Aventura

Las aventuras deben estar en formato JSON con esta estructura:

```json
{
  "session_id": "demo_mine_v1",
  "title": "La Mina Olvidada",
  "description": "Descripción de la aventura",
  "party": {
    "name": "Nombre del grupo",
    "members": [...]
  },
  "scenes": [
    {
      "scene_id": "mine_entrance",
      "title": "Entrada de la mina",
      "narration": "Texto narrativo de la escena",
      "options_text": ["Opción 1", "Opción 2"],
      "options": [
        {
          "id": "investigate_noise",
          "type": "skill_check",
          "skill": "Perception",
          "dc": 12,
          "success_scene": "mine_tunnel",
          "fail_scene": "goblin_ambush"
        }
      ]
    }
  ]
}
```

## 🎯 Uso

1. **Cargar aventura:**
   ```
   /loadcampaign demo_mine_v1
   ```

2. **Ver escena actual:**
   ```
   /scene
   ```

3. **Listar aventuras disponibles:**
   ```
   /loadcampaign
   ```

## 📁 Estructura de Archivos

```
adventures/
  └── demo_mine_v1.json
core/
  └── adventure/
      ├── __init__.py
      └── adventure_loader.py
```

## 🔄 Próximos Pasos

1. **Navegación entre escenas** - Implementar transiciones basadas en `options`
2. **Procesamiento de opciones** - Manejar `skill_check`, `spell`, `attack`, etc.
3. **Integración con GameAPI** - Enviar acciones de aventura al GameAPI
4. **NPCs en aventuras** - Cargar y gestionar NPCs desde aventuras
5. **Recompensas** - Aplicar XP y loot al completar escenas

## ✅ Estado Actual

- ✅ Carga de aventuras desde JSON
- ✅ Validación de estructura
- ✅ Renderizado de escenas de aventura
- ✅ Comando `/loadcampaign` funcional
- ⏳ Navegación entre escenas (pendiente)
- ⏳ Procesamiento de opciones (pendiente)
