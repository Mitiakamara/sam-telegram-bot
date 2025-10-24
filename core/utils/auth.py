import os
from core.utils.logger import safe_logger

logger = safe_logger(__name__)

# ============================================================
# Control de roles (admins)
# ============================================================
def get_admin_ids():
    """Obtiene los IDs de admin desde las variables de entorno."""
    raw_ids = os.getenv("ADMIN_USER_IDS", "")
    return [int(x.strip()) for x in raw_ids.split(",") if x.strip().isdigit()]

def is_admin(user_id: int) -> bool:
    """Verifica si el usuario tiene permisos de administrador."""
    admins = get_admin_ids()
    if user_id in admins:
        return True
    logger.warning(f"Intento de comando restringido por usuario no autorizado ({user_id})")
    return False
