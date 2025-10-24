import os
from core.utils.logger import safe_logger

logger = safe_logger(__name__)

# ============================================================
# Control de permisos de administrador
# ============================================================
def get_admin_ids():
    """
    Obtiene el/los IDs de administrador desde las variables de entorno.
    Soporta ADMIN_TELEGRAM_ID (único) o ADMIN_USER_IDS (múltiples, separados por coma).
    """
    single_admin = os.getenv("ADMIN_TELEGRAM_ID")
    multi_admins = os.getenv("ADMIN_USER_IDS")

    ids = set()

    if single_admin and single_admin.isdigit():
        ids.add(int(single_admin))

    if multi_admins:
        for x in multi_admins.split(","):
            x = x.strip()
            if x.isdigit():
                ids.add(int(x))

    return list(ids)


def is_admin(user_id: int) -> bool:
    """
    Verifica si el usuario actual tiene permisos de administrador.
    """
    admins = get_admin_ids()
    if user_id in admins:
        return True

    logger.warning(f"Intento de comando restringido por usuario no autorizado ({user_id})")
    return False
