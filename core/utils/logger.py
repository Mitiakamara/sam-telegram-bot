import logging
import sys

def get_logger(name: str = None) -> logging.Logger:
    """
    Retorna un logger configurado con formato estándar.
    Si el logging global ya está configurado, reutiliza la configuración existente.
    """

    logger = logging.getLogger(name if name else "sam_core")

    # Si el logger ya tiene handlers, lo reutilizamos.
    if logger.handlers:
        return logger

    # Configuración base
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Evita la duplicación de logs
    logger.propagate = False

    return logger


# Logger de respaldo en caso de que el sistema de logging falle
class NullLogger:
    def debug(self, *args, **kwargs): pass
    def info(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def exception(self, *args, **kwargs): pass


def safe_logger(name: str = None) -> logging.Logger:
    """
    Devuelve un logger funcional.
    Si ocurre un error al configurarlo, devuelve un NullLogger silencioso.
    """
    try:
        return get_logger(name)
    except Exception:
        return NullLogger()
