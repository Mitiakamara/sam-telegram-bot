from uuid import uuid4
from random import randint
from .models.resolution import Resolution, Step
from .models.base import CheckOutcome, IntentType


async def resolve(intent, srd, ctx):
    """
    Aplica las reglas SRD básicas y genera un objeto Resolution.
    Incluye tiradas, resultados y outcome general.
    """
    steps = []
    dice_log = []
    outcome = CheckOutcome.success

    # ============================================================
    # 🪄 Hechizos
    # ============================================================
    if intent.intent == IntentType.cast_spell:
        spell_name = intent.entities.get("spell_name", "hechizo")
        # Sleep usa 5d8 → ejemplo genérico
        rolls = [randint(1, 8) for _ in range(5)]
        total = sum(rolls)
        dice_log.append({"expr": "5d8", "rolls": rolls, "total": total})
        steps.append(
            Step(
                kind="check",
                desc=f"Lanza {spell_name} (5d8 HP afectados)",
                result_total=total,
                outcome=CheckOutcome.mixed,
            )
        )
        outcome = CheckOutcome.mixed

    # ============================================================
    # 🧠 Habilidad / Pericia
    # ============================================================
    elif intent.intent == IntentType.skill_check:
        roll = randint(1, 20)
        dice_log.append({"expr": "1d20", "rolls": [roll], "total": roll})
        steps.append(
            Step(
                kind="check",
                desc="Tirada de habilidad",
                result_total=roll,
                outcome=CheckOutcome.success if roll >= 10 else CheckOutcome.failure,
            )
        )
        outcome = CheckOutcome.success if roll >= 10 else CheckOutcome.failure

    # ============================================================
    # 💬 Interacción social
    # ============================================================
    elif intent.intent == IntentType.talk:
        steps.append(
            Step(
                kind="roleplay",
                desc="Interacción social libre",
                notes="El PNJ responde según el contexto.",
            )
        )
        outcome = CheckOutcome.mixed

    # ============================================================
    # 🔍 Investigación
    # ============================================================
    elif intent.intent == IntentType.investigate:
        roll = randint(1, 20)
        dice_log.append({"expr": "1d20", "rolls": [roll], "total": roll})
        steps.append(
            Step(
                kind="check",
                desc="Tirada de Investigación",
                result_total=roll,
                outcome=CheckOutcome.success if roll >= 12 else CheckOutcome.failure,
            )
        )
        outcome = CheckOutcome.success if roll >= 12 else CheckOutcome.failure

    # ============================================================
    # ⚔️ Ataque
    # ============================================================
    elif intent.intent == IntentType.attack:
        roll = randint(1, 20)
        dice_log.append({"expr": "1d20", "rolls": [roll], "total": roll})
        hit = roll >= 12
        steps.append(
            Step(
                kind="attack",
                desc="Ataque cuerpo a cuerpo",
                result_total=roll,
                outcome=CheckOutcome.success if hit else CheckOutcome.failure,
            )
        )
        if hit:
            dmg_roll = randint(1, 8)
            dice_log.append({"expr": "1d8", "rolls": [dmg_roll], "total": dmg_roll})
            steps.append(
                Step(
                    kind="damage",
                    desc="Daño de arma",
                    result_total=dmg_roll,
                    outcome=CheckOutcome.success,
                )
            )
        outcome = CheckOutcome.success if hit else CheckOutcome.failure

    # ============================================================
    # 🧩 Interacciones genéricas
    # ============================================================
    else:
        steps.append(Step(kind="action", desc="Acción general"))
        outcome = CheckOutcome.mixed

    # ============================================================
    # 🧾 Resultado final
    # ============================================================
    return Resolution(
        resolution_id=uuid4(),
        action_id=intent.action_id,
        intent=intent.intent,
        steps=steps,
        outcome=outcome,
        dice_log=dice_log,
    )
