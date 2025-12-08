"""
Point Buy System for D&D 5e Character Creation
Allows players to allocate 27 points to attributes using inline buttons.
"""
from typing import Dict, Any, List, Tuple

# Point buy costs (SRD 5e standard)
POINT_BUY_COSTS = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9,
    16: 11,
    17: 13,
    18: 15,
}

# Reverse lookup: cost -> possible values
COST_TO_VALUES = {
    0: [8],
    1: [9],
    2: [10],
    3: [11],
    4: [12],
    5: [13],
    7: [14],
    9: [15],
    11: [16],
    13: [17],
    15: [18],
}

# Standard array (alternative to point buy)
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
STANDARD_ARRAY_COST = 27  # Total cost of standard array

# Attribute order
ATTRIBUTES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]


class PointBuySystem:
    """
    Manages point buy attribute allocation with 27 points.
    """

    def __init__(self):
        self.total_points = 27
        self.min_value = 8
        self.max_value = 15  # Can't buy above 15 with points (racial bonuses can push to 18)

    def get_cost(self, value: int) -> int:
        """Returns the point cost for a given attribute value."""
        return POINT_BUY_COSTS.get(value, 999)  # Invalid values cost infinite

    def is_valid_value(self, value: int) -> bool:
        """Checks if a value is valid for point buy (8-15 before racial bonuses)."""
        return self.min_value <= value <= self.max_value

    def calculate_total_cost(self, attributes: Dict[str, int]) -> int:
        """Calculates total point cost for a set of attributes."""
        total = 0
        for attr, value in attributes.items():
            total += self.get_cost(value)
        return total

    def get_remaining_points(self, attributes: Dict[str, int]) -> int:
        """Calculates remaining points after current allocation."""
        used = self.calculate_total_cost(attributes)
        return self.total_points - used

    def can_increase(self, current_value: int, remaining_points: int) -> bool:
        """Checks if an attribute can be increased."""
        if current_value >= self.max_value:
            return False
        next_cost = self.get_cost(current_value + 1)
        return remaining_points >= next_cost

    def can_decrease(self, current_value: int) -> bool:
        """Checks if an attribute can be decreased."""
        return current_value > self.min_value

    def get_button_options(self, current_value: int, remaining_points: int) -> List[Tuple[str, str]]:
        """
        Returns list of (button_text, callback_data) for attribute adjustment.
        Format: [("-", "attr_decr"), ("+", "attr_incr"), ("✓", "attr_done")]
        """
        options = []
        
        # Decrease button
        if self.can_decrease(current_value):
            options.append(("➖", f"dec_{current_value}"))
        
        # Current value display (not clickable, just info)
        options.append((f"{current_value}", f"val_{current_value}"))
        
        # Increase button
        if self.can_increase(current_value, remaining_points):
            next_value = current_value + 1
            next_cost = self.get_cost(next_value)
            options.append((f"➕ ({next_cost})", f"inc_{next_value}"))
        
        return options

    def apply_standard_array(self) -> Dict[str, int]:
        """Returns attributes using standard array."""
        return dict(zip(ATTRIBUTES, STANDARD_ARRAY))

    def validate_allocation(self, attributes: Dict[str, int]) -> Tuple[bool, str]:
        """
        Validates a complete attribute allocation.
        Returns (is_valid, error_message)
        """
        # Check all attributes are present
        for attr in ATTRIBUTES:
            if attr not in attributes:
                return False, f"Falta el atributo {attr}"
        
        # Check all values are valid
        for attr, value in attributes.items():
            if not self.is_valid_value(value):
                return False, f"{attr} tiene un valor inválido: {value}"
        
        # Check total cost
        total_cost = self.calculate_total_cost(attributes)
        if total_cost > self.total_points:
            return False, f"Coste total ({total_cost}) excede los puntos disponibles ({self.total_points})"
        if total_cost < self.total_points:
            return False, f"Debes usar todos los puntos. Usados: {total_cost}/{self.total_points}"
        
        return True, ""
