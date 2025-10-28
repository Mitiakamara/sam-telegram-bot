# sam-telegram-bot/core/character_builder/builder.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from core.character_builder.prompts import SPECIES, CLASSES, SKILLS, SPELLS_BY_CLASS, ABILITIES, DEFAULT_LEVEL
from core.character_builder.storage import save_character
from core.character_builder.validator import validate_abilities

# ================================================================
# ESTADO DE SESIÓN (temporal)
# ================================================================
builder_state = {}  # user_id -> dict


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
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = builder_state.get(user_id)
    if not state:
        return await start_character_creation(update, context)

    step = state["step"]
    text = update.message.text.strip()

    # Paso 1: Nombre
    if step == 1:
        state["data"]["name"] = text
        state["step"] = 2

        # Mostrar razas disponibles
        keyboard = [[InlineKeyboardButton(r, callback_data=f"race:{r}")] for r in SPECIES]
        await update.message.reply_text("Elige la raza de tu personaje:",
                                        reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Paso 5: atributos manuales (si llegamos aquí desde el paso 4)
    if step == 5:
        # El usuario ingresa valores tipo: "15 14 13 12 10 8"
        parts = text.split()
        if len(parts) != 6:
            await update.message.reply_text("Por favor ingresa 6 valores separados por espacio. Ejemplo: 15 14 13 12 10 8")
            return
        try:
            values = [int(x) for x in parts]
        except Exception:
            return await update.message.reply_text("Solo números, por favor.")
        abilities = dict(zip(ABILITIES, values))
        if not validate_abilities(abilities):
            return await update.message.reply_text("Los valores deben estar entre 1 y 20.")
        state["data"]["abilities"] = abilities
        state["step"] = 6
        await ask_skills(update, state)
        return


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
            [InlineKeyboardButton("Asignar manualmente", callback_data="abilities:manual")],
            [InlineKeyboardButton("Usar valores estándar (15,14,13,12,10,8)", callback_data="abilities:standard")]
        ]
        await query.message.edit_text(
            f"Clase elegida: {char_class} (nivel {DEFAULT_LEVEL}).\n\n¿Cómo quieres definir tus atributos?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Paso 4: atributos
    if data.startswith("abilities:") and step == 4:
        mode = data.split(":", 1)[1]
        if mode == "manual":
            state["step"] = 5
            await query.message.edit_text("Introduce tus 6 valores separados por espacio (STR DEX CON INT WIS CHA).\nEjemplo: 15 14 13 12 10 8")
            return
        if mode == "standard":
            state["data"]["abilities"] = dict(zip(ABILITIES, [15, 14, 13, 12, 10, 8]))
            state["step"] = 6
            await ask_skills(update, state)
            return

    # Paso 6: habilidades
    if data.startswith("skill:") and step == 6:
        skill = data.split(":", 1)[1]
        if skill in state["data"].get("skills", []):
            state["data"]["skills"].remove(skill)
        else:
            state["data"].setdefault("skills", []).append(skill)

        selected = ", ".join(state["data"].get("skills", [])) or "ninguna"
        await query.answer(f"Habilidades: {selected}")

        # Si ya seleccionó 3, pasamos a siguiente paso
        if len(state["data"]["skills"]) >= 3:
            state["step"] = 7
            await ask_spells(update, state)
        return

    # Paso 7: spells
    if data.startswith("spell:") and step == 7:
        spell = data.split(":", 1)[1]
        state["data"].setdefault("spells", []).append(spell)
        if len(state["data"]["spells"]) >= 3 or spell == "none":
            await finish_character(update, state)
        return


# ================================================================
# SUB-FUNCIONES
# ================================================================
async def ask_skills(update, state):
    keyboard = [[InlineKeyboardButton(s, callback_data=f"skill:{s}")] for s in SKILLS]
    msg = "Elige hasta 3 habilidades para tu personaje:"
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


async def ask_spells(update, state):
    cls = state["data"]["class"]
    spells = SPELLS_BY_CLASS.get(cls)
    if not spells:
        return await finish_character(update, state)

    keyboard = [[InlineKeyboardButton(s, callback_data=f"spell:{s}")] for s in spells]
    keyboard.append([InlineKeyboardButton("Sin más hechizos", callback_data="spell:none")])
    msg = f"Selecciona hasta 3 conjuros para tu {cls}:"
    await update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


async def finish_character(update, state):
    data = state["data"]
    path = save_character(data)
    summary = (
        f"✅ *Personaje creado con éxito*\n\n"
        f"🧝 Nombre: {data['name']}\n"
        f"🏹 Raza: {data['race']}\n"
        f"⚔️ Clase: {data['class']}\n"
        f"🎚 Nivel: {data['level']}\n"
        f"💪 Atributos: {data['abilities']}\n"
        f"🎯 Habilidades: {', '.join(data.get('skills', []))}\n"
        f"✨ Hechizos: {', '.join(data.get('spells', [])) or '—'}\n\n"
        f"Guardado en: `{path}`"
    )
    await update.effective_message.reply_markdown(summary)
    builder_state.pop(update.effective_user.id, None)
