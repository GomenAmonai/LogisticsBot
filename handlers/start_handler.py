import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import Database
from utils.role_helper import check_user_role, get_user_role_menu
from config import WEBAPP_URL

logger = logging.getLogger(__name__)
db = Database()


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    user_id = user.id
    
    # Получаем или создаем пользователя
    user_dict, role = check_user_role(update, db)
    
    welcome_messages = {
        'admin': f"""
👋 Привет, {user.first_name}!

Вы вошли как **Администратор** системы.

Доступные функции:
• Управление пользователями
• Управление заказами
• Статистика и аналитика
• Настройки системы
        """,
        'manager': f"""
👋 Привет, {user.first_name}!

Вы вошли как **Менеджер логистической компании**.

Доступные функции:
• Управление заказами
• Отслеживание доставок
• Статистика работы
        """,
        'client': f"""
👋 Привет, {user.first_name}!

Добро пожаловать в систему логистики!

Вы можете:
• Создавать заказы
• Отслеживать статус доставки
• Просматривать историю заказов
        """
    }
    
    message = welcome_messages.get(role, welcome_messages['client'])
    
    await update.message.reply_text(
        message,
        reply_markup=get_user_role_menu(role, WEBAPP_URL),
        parse_mode='Markdown'
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /menu - показывает главное меню"""
    user_dict, role = check_user_role(update, db)
    
    await update.message.reply_text(
        "Главное меню:",
        reply_markup=get_user_role_menu(role, WEBAPP_URL)
    )

