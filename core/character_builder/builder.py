# sam-telegram-bot/core/character_builder/builder.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from core.character_builder.prompts import SPECIES, CLASSES, SKILLS, SPELLS_BY_CLASS, ABILITIES, DEFAULT_LEVEL
from core.character_builder.storage import save_character
from core.character_builder.validator import validate_abilities

# ================================================================
# ESTADO DE SESIÓN (temporal)
# ================================================================
builder_state = {}

# ================================================================
# TABLA DE COSTOS 27 POINT BUY
# ================================================================
POINT_COST = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}

def total_cost(abilities: dict) -> int:
    return sum(POINT_COST.get(v, 0) for v in abilities.values())

def points_remaining(abilities: dict) -> int:
    return 27 - total_cost(abilities)

def ability_modifier(score: int) -> int:
    return (score - 10) // 2

def mod_str(score: int) -> str:
    mod = ability_modifier(score)
    sign = "+" if mod >= 0 else ""
    return f"{sign}{mod}"

# ================================================================
# COMIENZO
# ================================================================
async def start_character_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    builder_state[user_id] = {"step": 1, "data": {}}
    await update.message.reply_text("🧙‍♂️ Vamos a crear tu personaje.\n\n¿Cómo se llamará?")
    return

# ================================================================
# RESPUESTA DE TEXTO
# ================================================================
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    state = builder_state.get(user_id)
    if not state:
        return False

    step = state["step"]
    text = update.message.text.strip()

    # Paso 1: Nombre
    if step == 1:
        state["data"]["name"] = text
        state["step"] = 2
        keyboard = [[InlineKeyboardButton(r, callback_data=f"race:{r}")] for r in SPECIES]
        await update.message.reply_text("Elige la raza de tu personaje:",
                                        reply_markup=InlineKeyboardMarkup(keyboard))
        return True

    # Paso 5: Manual (valores escritos)
    if step == 5 and "abilities" not in state["data"]:
        parts = text.split()
        if len(parts) != 6:
            await update.message.reply_text("Por favor ingresa 6 valores separados por espacio (STR DEX CON INT WIS CHA). Ejemplo: 15 14 13 12 10 8")
            return True
        try:
            values = [int(x) for x in parts]
        except Exception:
            await update.message.reply_text("Solo números, por favor.")
            return True

        abilities = dict(zip(ABILITIES, values))
        if not validate_abilities(abilities):
            await update.message.reply_text("Los valores deben estar entre 1 y 20.")
            return True

        state["data"]["abilities"] = abilities
        state["step"] = 6
        await ask_skills(update.message, state)
        return True

    return True

# ================================================================
# CALLBACKS DE BOTONES
# ================================================================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    state = builder_state.get(user_id)
    if not state:
        return await query.answer("Primero usa /createcharacter")

    data = query.data
    step = state["step"]

    # Paso 2: raza
    if data.startswith("race:") and step == 2:
        race = data.split(":", 1)[1]
        state["data"]["race"] = race
        state["step"] = 3
        keyboard = [[InlineKeyboardButton(c, callback_data=f"class:{c}")] for c in CLASSES]
        await query.message.edit_text(f"Raza elegida: {race}\n\nAhora elige tu clase:",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Paso 3: clase
    if data.startswith("class:") and step == 3:
        char_class = data.split(":", 1)[1]
        state["data"]["class"] = char_class
        state["data"]["level"] = DEFAULT_LEVEL
        state["step"] = 4
        keyboard = [
            [InlineKeyboardButton("27 Point Buy", callback_data="abilities:pointbuy")],
            [InlineKeyboardButton("Manual", callback_data="abilities:manual")],
            [InlineKeyboardButton("Valores estándar (15,14,13,12,10,8)", callback_data="abilities:standard")]
        ]
        await query.message.edit_text(
            f"Clase elegida: {char_class} (nivel {DEFAULT_LEVEL}).\n\n¿Cómo quieres definir tus atributos?",
            reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Paso 4: método de atributos
    if data.startswith("abilities:") and step == 4:
        mode = data.split(":", 1)[1]
        if mode == "manual":
            state["step"] = 5
            await query.message.edit_text("Introduce tus 6 valores separados por espacio (STR DEX CON INT WIS CHA).\nEjemplo: 15 14 13 12 10 8")
            return
        if mode == "standard":
            state["data"]["abilities"] = dict(zip(ABILITIES, [15, 14, 13, 12, 10, 8]))
            state["step"] = 6
            await ask_skills(query.message, state)
            return
        if mode == "pointbuy":
            state["step"] = 5
            state["data"]["abilities"] = {a: 8 for a in ABILITIES}
            await show_pointbuy_menu(query.message, state)
            return

    # Paso 5: control del point buy
    if data.startswith("inc:") or data.startswith("dec:"):
        _, ability = data.split(":")
        ab = state["data"]["abilities"]
        current = ab.get(ability, 8)
        new_val = current

        if data.startswith("inc:") and current < 15:
            temp = ab.copy()
            temp[ability] = current + 1
            if points_remaining(temp) >= 0:
                new_val = current + 1
        elif data.startswith("dec:") and current > 8:
            new_val = current - 1

        ab[ability] = new_val
        await query.answer()
        await show_pointbuy_menu(query.message, state)
        return

    if data == "pointbuy:confirm" and step == 5:
        ab = state["data"]["abilities"]
        if points_remaining(ab) < 0:
            return await query.answer("Te pasaste de los 27 puntos.")
        state["step"] = 6
        await ask_skills(query.message, state)
        return

    # Paso 6: habilidades
    if data.startswith("skill:") and step == 6:
        skill = data.split(":", 1)[1]
        state["data"].setdefault("skills", [])
        if skill in state["data"]["skills"]:
            state["data"]["skills"].remove(skill)
        else:
            state["data"]["skills"].append(skill)
        selected = ", ".join(state["data"]["skills"]) or "ninguna"
        await query.answer(f"Habilidades: {selected}")
        if len(state["data"]["skills"]) >= 3:
            state["step"] = 7
            await ask_spells(query.message, state)
        return

    # Paso 7: conjuros
    if data.startswith("spell:") and step == 7:
        spell = data.split(":", 1)[1]
        state["data"].setdefault("spells", [])
        if spell != "none":
            state["data"]["spells"].append(spell)
        await finish_character(query.message, state)
        return

# ================================================================
# SUB-FUNCIONES
# ================================================================
async def show_pointbuy_menu(message, state):
    ab = state["data"]["abilities"]
    remain = points_remaining(ab)
    keyboard = []
    for a in ABILITIES:
        mod = mod_str(ab[a])
        label = f"{a}: {ab[a]} ({mod})"
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"dec:{a}"),
            InlineKeyboardButton(label, callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"inc:{a}")
        ])
    keyboard.append([InlineKeyboardButton("✅ Confirmar", callback_data="pointbuy:confirm")])
    text = (
        f"🧮 *27 Point Buy*\n"
        f"Puntos restantes: {remain}\n\n"
        "Usa ➕ o ➖ para ajustar cada atributo.\n"
        "_El número entre paréntesis muestra el modificador._"
    )
    await message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def ask_skills(message, state):
    keyboard = [[InlineKeyboardButton(s, callback_data=f"skill:{s}")] for s in SKILLS]
    msg = "Elige hasta 3 habilidades para tu personaje:"
    await message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def ask_spells(message, state):
    cls = state["data"]["class"]
    spells = SPELLS_BY_CLASS.get(cls)
    if not spells:
        return await finish_character(message, state)
    keyboard = [[InlineKeyboardButton(s, callback_data=f"spell:{s}")] for s in spells]
    keyboard.append([InlineKeyboardButton("Sin más hechizos", callback_data="spell:none")])
    msg = f"Selecciona hasta 3 conjuros para tu {cls}:"
    await message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def finish_character(message, state):
    data = state["data"]

    # 🧮 Calcular modificadores
    data["modifiers"] = {a: ability_modifier(v) for a, v in data["abilities"].items()}

    path = save_character(data)
    summary = (
        f"✅ *Personaje creado con éxito*\n\n"
        f"🧝 Nombre: {data['name']}\n"
        f"🏹 Raza: {data['race']}\n"
        f"⚔️ Clase: {data['class']}\n"
        f"🎚 Nivel: {data['level']}\n"
        f"💪 Atributos: {data['abilities']}\n"
        f"📈 Modificadores: {data['modifiers']}\n"
        f"🎯 Habilidades: {', '.join(data.get('skills', []))}\n"
        f"✨ Hechizos: {', '.join(data.get('spells', [])) or '—'}\n\n"
        f"Guardado en: `{path}`"
    )
    await message.reply_markdown(summary)
    builder_state.pop(message.chat.id, None)
