import json
import os
from statistics import mean

class AttributeAnalyzer:
    """
    Transforma los atributos del personaje o del grupo
    en un perfil narrativo para el motor de historia adaptativa.
    """

    def __init__(self, mapping_path=None):
        base_path = os.path.dirname(__file__)
        self.mapping_path = mapping_path or os.path.join(base_path, "attribute_to_narrative_map.json")
        self.attribute_map = self._load_mapping()

    def _load_mapping(self):
        with open(self.mapping_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _normalize(self, value, min_val=1, max_val=20):
        """Normaliza los atributos (1–20) a un rango de 0–1."""
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

    def analyze_character(self, attributes):
        """
        Recibe un dict con los atributos del personaje:
        {
            "strength": 15,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 13,
            "charisma": 8
        }
        Devuelve un dict con ponderaciones narrativas.
        """
        profile = {k: 0.0 for k in ["brute", "graceful", "clever", "resilient", "insightful", "charming"]}

        for attr, score in attributes.items():
            if attr in self.attribute_map:
                normalized = self._normalize(score)
                for trait, weight in self.attribute_map[attr].items():
                    profile[trait] += normalized * weight

        # normaliza los valores entre 0 y 1
        min_val = min(profile.values())
        max_val = max(profile.values())
        if max_val - min_val > 0:
            for k in profile:
                profile[k] = round((profile[k] - min_val) / (max_val - min_val), 3)
        return profile

    def analyze_party(self, party_attributes):
        """
        Recibe una lista de personajes (cada uno con sus atributos).
        Devuelve el promedio del perfil narrativo del grupo.
        """
        profiles = [self.analyze_character(attrs) for attrs in party_attributes]
        combined = {}

        for key in profiles[0].keys():
            combined[key] = round(mean([p[key] for p in profiles]), 3)

        return combined


# =============================
# Ejemplo de uso
# =============================
if __name__ == "__main__":
    analyzer = AttributeAnalyzer()

    # Personaje individual
    hero = {
        "strength": 16,
        "dexterity": 14,
        "constitution": 13,
        "intelligence": 11,
        "wisdom": 10,
        "charisma": 8
    }
    print("Perfil narrativo del héroe:")
    print(analyzer.analyze_character(hero))

    # Grupo de prueba
    party = [
        hero,
        {"strength": 8, "dexterity": 16, "constitution": 10, "intelligence": 15, "wisdom": 12, "charisma": 14}
    ]
    print("\nPerfil narrativo del grupo:")
    print(analyzer.analyze_party(party))
