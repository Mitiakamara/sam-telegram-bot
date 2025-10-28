import time
import random
from datetime import datetime

from core.scene_manager.scene_manager import SceneManager
from core.story_director.story_director import StoryDirector
from core.emotion.tone_adapter import ToneAdapter
from core.emotion.mood_manager import MoodManager
from core.action_handler.action_handler import ActionHandler
from core.renderer.renderer import Renderer
from core.emotion.emotional_feedback import EmotionalFeedbackLoop

# ================================================================
# 🤖 AUTO NARRATOR (Fase 6.13)
# ================================================================
# Ejecuta automáticamente una secuencia de escenas completas,
# utilizando todo el ecosistema emocional de S.A.M.
# ================================================================


class AutoNarrator:
    def __init__(self, max_scenes: int = 5, delay: float = 2.0):
        self.max_scenes = max_scenes
        self.delay = delay  # segundos entre escenas
        self.scene_manager = SceneManager()
        self.story_director = StoryDirector()
        self.tone_adapter = ToneAdapter()
        self.mood_manager = MoodManager()
        self.action_handler = ActionHandler()
        self.renderer = Renderer()

    # ------------------------------------------------------------
    # 🧠 Simulación principal
    # ------------------------------------------------------------
    async def run(self, update=None):
        """
        Ejecuta una mini campaña narrativa de forma autónoma.
        Puede funcionar tanto en consola como en el bot Telegram.
        """
        messages = []

        intro = "🌌 *MODO NARRADOR AUTOMÁTICO ACTIVADO*\nLa historia comienza..."
        if update:
            await update.message.reply_text(intro, parse_mode="Markdown")
        else:
            print(intro)

        for i in range(1, self.max_scenes + 1):
            # 1️⃣ Decidir tipo de escena
            next_type = self.story_director.decide_next_scene_type()
            title = f"Escena {i}: {next_type.title()}"
            description = f"Los aventureros enfrentan una etapa de tipo '{next_type}'."
            scene = self.scene_manager.create_scene(title, description, next_type)

            # 2️⃣ Generar narrativa inicial
            opening = self.renderer.render_scene(scene, self.mood_manager.current_tone)
            messages.append(f"🎬 *{title}*\n{opening}")

            # 3️⃣ Simular acciones (aleatorias o adaptadas al tono)
            simulated_actions = random.sample(
                ["explora", "ataca", "negocia", "investiga", "cura", "descansa"], k=3
            )
            for action in simulated_actions:
                self.action_handler.register_action(action)
                act_text = self.renderer.render_action(scene, action, self.mood_manager.current_tone)
                messages.append(f"🗡️ *Acción:* {action}\n{act_text}")
                await asyncio.sleep(self.delay / 2) if update else time.sleep(self.delay / 2)

            # 4️⃣ Cerrar escena
            self.story_director.evaluate_scene_outcome(random.uniform(0.4, 0.9))
            self.scene_manager.end_scene(
                self.tone_adapter, self.mood_manager,
                self.story_director, self.action_handler, self.renderer
            )

            # 5️⃣ Procesar ciclo emocional
            feedback = EmotionalFeedbackLoop(self.tone_adapter, self.mood_manager, self.story_director)
            result = feedback.process_feedback()

            summary = (
                f"📘 *Escena finalizada:* {scene.title}\n"
                f"🎭 Tono global: {result['tone_score']['label']}\n"
                f"📈 Tendencia: {result['trend']['direction']}\n"
                f"💫 Ajuste: {result['adjustment']['tone']}\n"
                f"🏷️ Próxima escena sugerida: {result['next_scene_type']}\n"
            )
            messages.append(summary)

            # 6️⃣ Espera breve antes de la siguiente
            await asyncio.sleep(self.delay) if update else time.sleep(self.delay)

        closing = "🌟 *La historia llega a su fin.*\nLos ecos emocionales permanecen en la memoria de S.A.M."
        messages.append(closing)

        # Mostrar todo en Telegram o consola
        if update:
            for msg in messages:
                await update.message.reply_text(msg, parse_mode="Markdown")
                await asyncio.sleep(1)
        else:
            for msg in messages:
                print(msg)
                time.sleep(1)

        return messages
