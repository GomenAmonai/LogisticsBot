import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from utils.role_helper import check_user_role, get_user_role_menu
from config import WEBAPP_URL

logger = logging.getLogger(__name__)
db = Database()


def get_privacy_policy_text() -> str:
    """Возвращает текст политики конфиденциальности"""
    return """
🔒 <b>Политика конфиденциальности</b>

Перед использованием бота, пожалуйста, ознакомьтесь с нашей политикой конфиденциальности:

<b>1. Сбор данных</b>
Мы собираем следующие данные:
• Ваш Telegram ID
• Имя и фамилия
• Username (если указан)
• Данные о заказах и доставках

<b>2. Использование данных</b>
Ваши данные используются для:
• Обработки заказов
• Связи с вами по вопросам доставки
• Улучшения качества сервиса

<b>3. Защита данных</b>
Все данные хранятся в защищенной базе данных и не передаются третьим лицам без вашего согласия.

<b>4. Ваши права</b>
Вы имеете право:
• Запросить информацию о ваших данных
• Удалить ваши данные
• Отозвать согласие на обработку данных

Продолжая использование бота, вы соглашаетесь с данной политикой конфиденциальности.
    """


def get_privacy_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для принятия политики конфиденциальности"""
    keyboard = [[
        InlineKeyboardButton("✅ Принять", callback_data="accept_privacy")
    ]]
    return InlineKeyboardMarkup(keyboard)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    user_id = user.id
    
    # Получаем или создаем пользователя
    user_dict, role = check_user_role(update, db)
    
    # Приветственное сообщение
    welcome_message = f"""
👋 <b>Добро пожаловать, {user.first_name}!</b>

Добро пожаловать в систему логистики!

Здесь вы можете:
• Создавать заказы
• Отслеживать статус доставки
• Просматривать историю заказов
    """
    
    # Проверяем, принял ли пользователь политику конфиденциальности
    if not db.has_accepted_privacy(user_id):
        # Показываем приветствие и политику
        await update.message.reply_text(
            welcome_message,
            parse_mode='HTML'
        )
        
        # Показываем политику конфиденциальности
        await update.message.reply_text(
            get_privacy_policy_text(),
            reply_markup=get_privacy_keyboard(),
            parse_mode='HTML'
        )
    else:
        # Пользователь уже принял политику - показываем меню
        await update.message.reply_text(
            welcome_message,
            reply_markup=get_user_role_menu(role, WEBAPP_URL),
            parse_mode='HTML'
        )


async def accept_privacy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик принятия политики конфиденциальности"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Отмечаем, что пользователь принял политику
    db.accept_privacy(user_id)
    
    # Получаем роль пользователя
    user_dict, role = check_user_role(update, db)
    
    # Показываем главное меню
    await query.edit_message_text(
        text="✅ Политика конфиденциальности принята!\n\nВыберите действие:",
        reply_markup=get_user_role_menu(role, WEBAPP_URL)
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /menu - показывает главное меню"""
    user_dict, role = check_user_role(update, db)
    
    await update.message.reply_text(
        "Главное меню:",
        reply_markup=get_user_role_menu(role, WEBAPP_URL)
    )
