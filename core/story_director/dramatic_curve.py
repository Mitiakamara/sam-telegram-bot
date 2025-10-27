import random

class DramaticCurve:
    """
    Controla la progresión del ritmo narrativo en arcos:
    introducción → ascenso → clímax → caída → epílogo.
    """
    def __init__(self):
        self.stages = ["inicio", "ascenso", "climax", "caida", "epilogo"]
        self.current_stage = "inicio"
        self.progress_counter = 0

    def get_stage(self):
        """Devuelve el estado dramático actual."""
        return self.current_stage

    def advance(self):
        """Progresa la curva dramática según eventos importantes."""
        self.progress_counter += 1
        index = min(self.progress_counter // 3, len(self.stages) - 1)
        self.current_stage = self.stages[index]
        return self.current_stage

    def reset(self):
        self.current_stage = "inicio"
        self.progress_counter = 0
