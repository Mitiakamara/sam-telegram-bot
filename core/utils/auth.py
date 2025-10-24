import os
from telegram import Update
from core.utils.logger import safe_logger

logger = safe_logger(__name__)

# ============================================================
# Control de permisos de administrador (con estilo S.A.M.)
# ============================================================

def get_admin_ids():
    """Obtiene los IDs de admin desde las variables de entorno (Render o .env)."""
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


async def deny_access(update: Update, reason: str = None):
    """
    Envía un mensaje de acceso denegado con tono cómico.
    Llamado automáticamente cuando un usuario no autorizado intenta algo prohibido.
    """
    user = update.effective_user.first_name
    funny_responses = [
        f"🛑 {user}, tus habilidades arcánicas no son suficientes para usar este hechizo administrativo.",
        f"⚙️ *S.A.M. gruñe suavemente...* 'Lo siento, {user}, ese comando está reservado para los altos magos del servidor.'",
        f"👑 Solo el Dungeon Master puede manipular el tejido del multiverso digital, {user}.",
        f"🪄 *Intentas pronunciar las palabras místicas...* pero nada ocurre. S.A.M. sonríe y dice: 'Nice try, {user}.'",
        f"🔒 El acceso está tan cerrado que ni un hechizo de *Knock* lo abriría, {user}.",
    ]

    from random import choice
    message = choice(funny_responses)
    await update.message.reply_text(message, parse_mode="Markdown")


def is_admin(user_id: int) -> bool:
    """Verifica si el usuario tiene permisos de administrador."""
    admins = get_admin_ids()
    return user_id in admins


async def check_admin(update: Update) -> bool:
    """
    Versión asíncrona de la validación.
    Devuelve True si el usuario es admin, de lo contrario envía un mensaje cómico y devuelve False.
    """
    user_id = update.effective_user.id
    if is_admin(user_id):
        return True

    logger.warning(f"Intento de comando restringido por usuario no autorizado ({user_id})")
    await deny_access(update)
    return False
