class ThemeTracker:
    """
    Detecta y mantiene registro de los temas dominantes de la historia:
    sacrificio, redención, traición, esperanza, corrupción, destino, etc.
    """
    def __init__(self):
        self.themes_memory = []

    def detect_theme(self, game_state):
        """Analiza el estado del juego para determinar el tema activo."""
        description = game_state.get("description", "").lower()
        if "traición" in description:
            theme = "traición"
        elif "luz" in description or "fe" in description:
            theme = "esperanza"
        elif "sangre" in description or "venganza" in description:
            theme = "venganza"
        else:
            theme = "misterio"

        self.themes_memory.append(theme)
        return theme

    def get_recurrent_theme(self):
        """Devuelve el tema más frecuente hasta el momento."""
        if not self.themes_memory:
            return None
        return max(set(self.themes_memory), key=self.themes_memory.count)
