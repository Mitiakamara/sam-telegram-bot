"""
Use Cases Module
----------------
Casos de uso para acciones principales del sistema.
Separa la lógica de negocio de los handlers.
"""

from .process_player_action import ProcessPlayerActionUseCase

__all__ = [
    "ProcessPlayerActionUseCase",
]
