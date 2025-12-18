"""
SAM Exceptions
--------------
Excepciones de dominio para SAM.
Proporciona manejo de errores consistente y específico.
"""


class SAMException(Exception):
    """Excepción base de SAM."""
    pass


class PlayerNotFoundError(SAMException):
    """Jugador no encontrado."""
    pass


class CampaignNotFoundError(SAMException):
    """Campaña no encontrada."""
    pass


class GameAPIError(SAMException):
    """Error comunicándose con GameAPI."""
    pass


class CharacterCreationError(SAMException):
    """Error al crear personaje."""
    pass


class SceneNotFoundError(SAMException):
    """Escena no encontrada."""
    pass
