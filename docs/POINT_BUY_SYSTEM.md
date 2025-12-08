# 📊 Point Buy System for Character Creation

## Overview

SAM now includes a **Point Buy system** for attribute allocation during character creation, with interactive inline buttons for easy attribute assignment.

## Features

### ✅ Point Buy (27 points)
- Allocate 27 points across 6 attributes
- Range: 8-15 per attribute (before racial bonuses)
- Point costs follow SRD 5e standard:
  - 8-13: 0-5 points
  - 14: 7 points
  - 15: 9 points
  - 16-18: Not available in point buy (racial bonuses can push to 18)

### ✅ Standard Array (Alternative)
- Quick option: 15, 14, 13, 12, 10, 8
- One-click application
- Can switch from point buy to standard array anytime

### ✅ Interactive Buttons
- ➖ **Decrease** button to reduce attribute value
- ➕ **Increase** button to raise attribute value (shows cost)
- ◀️ **Previous** / **Next** ▶️ to navigate between attributes
- ✅ **Confirm** when all 27 points are used
- 🔄 **Switch to Standard Array** option

## How It Works

### Flow

1. **Choose Method**
   ```
   After selecting background:
   → Choose: Point Buy or Standard Array
   ```

2. **Point Buy Interface**
   ```
   💪 Point Buy - STR
   
   Valor actual: 8
   Puntos restantes: 27/27
   
   📊 Atributos:
   👉 STR: 8 (0 pts)
      DEX: 8 (0 pts)
      CON: 8 (0 pts)
      ...
   
   [➖ Reducir] [Valor: 8] [➕ Aumentar (1 pt)]
   [◀️ Anterior] [Siguiente ▶️]
   [🔄 Usar Array Estándar]
   ```

3. **Navigation**
   - Use Previous/Next to move between attributes
   - Increase/Decrease to adjust values
   - System tracks remaining points
   - Can't confirm until all 27 points are used

4. **Validation**
   - Must use exactly 27 points
   - All attributes must be 8-15
   - Can switch to standard array at any time

## Point Costs

| Value | Cost | Notes |
|-------|------|-------|
| 8 | 0 | Minimum |
| 9 | 1 | |
| 10 | 2 | |
| 11 | 3 | |
| 12 | 4 | |
| 13 | 5 | |
| 14 | 7 | |
| 15 | 9 | Maximum in point buy |
| 16+ | N/A | Only via racial bonuses |

## Example Allocations

### Balanced Build (27 points)
- STR: 15 (9 pts)
- DEX: 14 (7 pts)
- CON: 13 (5 pts)
- INT: 12 (4 pts)
- WIS: 10 (2 pts)
- CHA: 8 (0 pts)
**Total: 27 points**

### Specialized Build (27 points)
- STR: 15 (9 pts)
- DEX: 15 (9 pts)
- CON: 13 (5 pts)
- INT: 8 (0 pts)
- WIS: 8 (0 pts)
- CHA: 12 (4 pts)
**Total: 27 points**

### Standard Array
- 15, 14, 13, 12, 10, 8
- Total cost: 27 points
- Pre-assigned, no customization

## User Experience

### Before (Text Input)
```
User: "18 18 18 18 18 18"
Bot: ❌ Formato inválido (values too high)
```

### After (Interactive Buttons)
```
User clicks buttons to adjust:
- Click ➕ on STR → 9 (1 pt used)
- Click ➕ on STR → 10 (2 pts used)
- Navigate to DEX
- Click ➕ on DEX → 9 (3 pts used)
...
- Click ✅ when 27 points used
```

## Technical Implementation

### Files
- `core/character_builder/point_buy_system.py` - Point buy logic
- `core/handlers/createcharacter_handler.py` - UI integration

### Key Classes
- `PointBuySystem` - Manages point costs and validation
- Handler functions - Manage button interactions

### State Management
- Attributes stored in `context.user_data["character_data"]`
- Point buy system in `context.user_data["point_buy_system"]`
- Current attribute index tracked for navigation

## Benefits

1. **User-Friendly**: No need to calculate point costs manually
2. **Visual Feedback**: See remaining points in real-time
3. **Error Prevention**: Can't use invalid values
4. **Flexible**: Can switch to standard array anytime
5. **SRD Compliant**: Follows official D&D 5e point buy rules

---

**Version**: 7.12  
**Status**: ✅ Implemented  
**Last Updated**: 2025-01-XX
