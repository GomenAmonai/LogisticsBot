import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import Database
from keyboards.client_keyboard import get_client_menu, get_back_to_client_menu_keyboard
from utils.role_helper import get_user_role_menu
from config import WEBAPP_URL

logger = logging.getLogger(__name__)
db = Database()


async def client_profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик просмотра профиля клиента"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    orders = db.get_user_orders(user_id, 'client')
    
    message = f"""
📊 Ваш профиль:

🆔 ID: {user['user_id']}
👤 Имя: {user['first_name'] or 'Не указано'}
📝 Фамилия: {user['last_name'] or 'Не указано'}
🔖 Username: @{user['username'] or 'Не указано'}
📦 Заказов: {len(orders)}
👤 Роль: Клиент
    """
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_client_menu(WEBAPP_URL)
    )


async def client_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик просмотра заказов клиента"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    orders = db.get_user_orders(user_id, 'client')
    
    if not orders:
        message = "📦 У вас пока нет заказов.\n\nСоздайте первый заказ через меню!"
    else:
        message = f"📦 Ваши заказы ({len(orders)}):\n\n"
        for order in orders[:10]:  # Показываем первые 10
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🚚',
                'completed': '✅',
                'cancelled': '❌'
            }.get(order['status'], '❓')
            
            message += f"{status_emoji} Заказ #{order['id']}\n"
            message += f"   Статус: {order['status']}\n"
            message += f"   Описание: {order['description'][:50]}...\n\n"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_client_menu_keyboard(WEBAPP_URL)
    )


async def client_create_order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания заказа"""
    query = update.callback_query
    await query.answer()
    
    message = """
➕ Создание нового заказа

Используйте WebApp для создания заказа или отправьте описание заказа текстом.

Для создания заказа через WebApp нажмите кнопку "🌐 Открыть приложение" в главном меню.
    """
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_client_menu_keyboard(WEBAPP_URL)
    )


async def client_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик настроек клиента"""
    query = update.callback_query
    await query.answer()
    
    message = "⚙️ Настройки\n\nЗдесь будут настройки вашего профиля."
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_client_menu_keyboard(WEBAPP_URL)
    )


async def client_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик помощи для клиента"""
    query = update.callback_query
    await query.answer()
    
    message = """
📝 Помощь

Как пользоваться ботом:

1. Создайте заказ через WebApp или меню
2. Отслеживайте статус заказа в разделе "Мои заказы"
3. Получайте уведомления об изменении статуса

Если у вас возникли вопросы, обратитесь к менеджеру.
    """
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_client_menu_keyboard(WEBAPP_URL)
    )


async def back_to_client_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик возврата в главное меню клиента"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="Главное меню",
        reply_markup=get_client_menu(WEBAPP_URL)
    )


def register_client_handlers(application):
    """Регистрирует обработчики для клиентов"""
    application.add_handler(CallbackQueryHandler(client_profile_handler, pattern="^client_profile$"))
    application.add_handler(CallbackQueryHandler(client_orders_handler, pattern="^client_orders$"))
    application.add_handler(CallbackQueryHandler(client_create_order_handler, pattern="^client_create_order$"))
    application.add_handler(CallbackQueryHandler(client_settings_handler, pattern="^client_settings$"))
    application.add_handler(CallbackQueryHandler(client_help_handler, pattern="^client_help$"))
    application.add_handler(CallbackQueryHandler(back_to_client_menu_handler, pattern="^back_to_client_menu$"))

