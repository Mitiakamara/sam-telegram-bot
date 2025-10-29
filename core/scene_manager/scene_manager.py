# ==========================================================
# 🎬 SAM – Scene Manager (Modo Campaña Pre-Creada)
# ==========================================================
import logging
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class SceneManager:
    """
    Administra las escenas activas de la campaña o de la narrativa dinámica.
    Puede manejar tanto escenas predefinidas (desde archivos JSON de campaña)
    como escenas generadas dinámicamente durante el juego.
    """

    def __init__(self, campaign_dir: str = "data/campaigns"):
        self.campaign_dir = Path(campaign_dir)
        self.active_scene = None
        self.active_campaign = None
        self.active_chapter = None
        self.scene_history = []

    # ==========================================================
    # CAMPAÑAS (Opcional)
    # ==========================================================
    def load_campaign(self, campaign_id: str):
        """
        Carga una campaña desde data/campaigns/{campaign_id}/campaign.json
        """
        campaign_path = self.campaign_dir / campaign_id / "campaign.json"
        if not campaign_path.exists():
            logger.warning(f"[SceneManager] No se encontró la campaña: {campaign_path}")
            return None

        with open(campaign_path, "r", encoding="utf-8") as f:
            campaign = json.load(f)

        self.active_campaign = campaign.get("id")
        self.active_chapter = campaign["chapters"][0]["id"] if campaign.get("chapters") else None
        logger.info(f"[SceneManager] Campaña cargada: {campaign.get('title')}")
        return campaign

    def load_chapter(self, campaign_id: str, chapter_id: str):
        """
        Carga un capítulo desde data/campaigns/{campaign_id}/{chapter_id}.json
        """
        chapter_path = self.campaign_dir / campaign_id / f"{chapter_id}.json"
        if not chapter_path.exists():
            logger.warning(f"[SceneManager] No se encontró el capítulo: {chapter_path}")
            return None

        with open(chapter_path, "r", encoding="utf-8") as f:
            chapter = json.load(f)

        logger.info(f"[SceneManager] Capítulo cargado: {chapter_id} ({len(chapter.get('scenes', []))} escenas)")
        return chapter

    # ==========================================================
    # ESCENAS
    # ==========================================================
    def create_initial_scene(self):
        """
        Crea la primera escena del juego si no hay ninguna activa.
        """
        scene = {
            "scene_id": "intro_scene",
            "title": "Inicio de la aventura",
            "description": (
                "Una brisa fría atraviesa el valle silencioso. El grupo observa las ruinas antiguas "
                "a lo lejos, sin saber lo que el destino les depara."
            ),
            "scene_type": "intro",
            "emotion_intensity": 3,
            "status": "active",
            "objectives": ["explorar", "prepararse", "descansar"],
            "npcs": [],
            "environment": {
                "lighting": "suave",
                "weather": "templado",
                "terrain": "colinas"
            },
            "available_actions": ["avanzar", "observar", "dialogar"],
            "transitions": {}
        }
        self.active_scene = scene
        self.scene_history.append({
            "scene_id": scene["scene_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "title": scene["title"]
        })
        logger.info("[SceneManager] Escena inicial creada.")
        return scene

    def get_active_scene(self):
        """Devuelve la escena actual (si existe)."""
        return self.active_scene

    def update_scene(self, scene_data: dict):
        """
        Actualiza los datos de la escena activa con nueva información.
        """
        if not self.active_scene:
            self.active_scene = scene_data
        else:
            self.active_scene.update(scene_data)
        logger.info(f"[SceneManager] Escena actualizada: {self.active_scene.get('title')}")
        return self.active_scene

    def end_scene(self):
        """
        Marca la escena actual como finalizada y guarda su registro en el historial.
        """
        if not self.active_scene:
            logger.warning("[SceneManager] No hay escena activa para cerrar.")
            return None

        self.active_scene["status"] = "ended"
        self.active_scene["end_time"] = datetime.utcnow().isoformat()
        self.scene_history.append({
            "scene_id": self.active_scene.get("scene_id"),
            "timestamp": datetime.utcnow().isoformat(),
            "title": self.active_scene.get("title")
        })

        logger.info(f"[SceneManager] Escena finalizada: {self.active_scene.get('title')}")
        self.active_scene = None
        return True

    def should_end_scene(self, narrative_output: str) -> bool:
        """
        Determina si la escena debe cerrarse con base en el texto narrativo.
        Busca palabras clave como 'continúa', 'siguiente', 'descanso', etc.
        """
        if not narrative_output:
            return False

        keywords = ["siguiente", "continúa", "avanzan", "termina", "descanso", "nuevo capítulo"]
        for k in keywords:
            if k.lower() in narrative_output.lower():
                logger.info(f"[SceneManager] Palabra clave '{k}' detectada: cierre de escena.")
                return True
        return False

    # ==========================================================
    # UTILIDADES Y DEPURACIÓN
    # ==========================================================
    def get_scene_history(self):
        """Devuelve el historial completo de escenas jugadas."""
        return self.scene_history

    def get_campaign_status(self):
        """Devuelve información resumida de la campaña activa."""
        return {
            "campaign": self.active_campaign,
            "chapter": self.active_chapter,
            "active_scene": self.active_scene.get("title") if self.active_scene else None,
            "scenes_played": len(self.scene_history)
        }

    def reset(self):
        """Reinicia el Scene Manager (nuevo inicio de campaña o partida)."""
        logger.warning("[SceneManager] Reiniciando escenas y campaña activa.")
        self.active_scene = None
        self.active_campaign = None
        self.active_chapter = None
        self.scene_history = []
