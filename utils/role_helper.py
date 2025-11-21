from telegram import Update
from database import Database
from models.user import UserRole
from keyboards.client_keyboard import get_client_menu
from keyboards.admin_keyboard import get_admin_menu
from keyboards.manager_keyboard import get_manager_menu
from config import WEBAPP_URL


def get_user_role_menu(user_role: str, webapp_url: str = None) -> object:
    """Возвращает меню в зависимости от роли пользователя"""
    if user_role == UserRole.ADMIN:
        return get_admin_menu(webapp_url)
    elif user_role == UserRole.MANAGER:
        return get_manager_menu(webapp_url)
    else:  # CLIENT
        return get_client_menu(webapp_url)


def check_user_role(update: Update, db: Database) -> tuple:
    """Проверяет роль пользователя и возвращает (user_dict, role)"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        # Если пользователь не найден, создаем его как клиента
        db.add_user(
            user_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
            role=UserRole.CLIENT
        )
        user = db.get_user(user_id)
    
    role = user.get('role', UserRole.CLIENT)
    return user, role

