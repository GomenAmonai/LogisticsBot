import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import Database
from keyboards.manager_keyboard import get_manager_menu, get_back_to_manager_menu_keyboard
from utils.role_helper import check_user_role
from config import WEBAPP_URL

logger = logging.getLogger(__name__)
db = Database()


async def manager_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик просмотра заказов менеджера"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    orders = db.get_user_orders(user_id, 'manager')
    
    if not orders:
        message = "📦 У вас пока нет заказов"
    else:
        message = f"📦 Ваши заказы ({len(orders)}):\n\n"
        for order in orders[:10]:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🚚',
                'completed': '✅',
                'cancelled': '❌'
            }.get(order['status'], '❓')
            
            message += f"{status_emoji} Заказ #{order['id']}\n"
            message += f"   Статус: {order['status']}\n"
            message += f"   Клиент ID: {order['client_id']}\n\n"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_manager_menu_keyboard(WEBAPP_URL)
    )


async def manager_new_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик новых заказов"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    all_orders = db.get_user_orders(user_id, 'manager')
    new_orders = [o for o in all_orders if o['status'] == 'pending']
    
    if not new_orders:
        message = "📋 Новых заказов нет"
    else:
        message = f"📋 Новые заказы ({len(new_orders)}):\n\n"
        for order in new_orders[:10]:
            message += f"⏳ Заказ #{order['id']}\n"
            message += f"   Клиент ID: {order['client_id']}\n"
            message += f"   Описание: {order['description'][:50]}...\n\n"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_manager_menu_keyboard(WEBAPP_URL)
    )


async def manager_in_progress_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик заказов в работе"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    all_orders = db.get_user_orders(user_id, 'manager')
    in_progress = [o for o in all_orders if o['status'] == 'in_progress']
    
    if not in_progress:
        message = "🚚 Заказов в работе нет"
    else:
        message = f"🚚 Заказы в работе ({len(in_progress)}):\n\n"
        for order in in_progress[:10]:
            message += f"🚚 Заказ #{order['id']}\n"
            message += f"   Клиент ID: {order['client_id']}\n\n"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_manager_menu_keyboard(WEBAPP_URL)
    )


async def manager_completed_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик завершенных заказов"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    all_orders = db.get_user_orders(user_id, 'manager')
    completed = [o for o in all_orders if o['status'] == 'completed']
    
    if not completed:
        message = "✅ Завершенных заказов нет"
    else:
        message = f"✅ Завершенные заказы ({len(completed)}):\n\n"
        for order in completed[:10]:
            message += f"✅ Заказ #{order['id']}\n"
            message += f"   Клиент ID: {order['client_id']}\n\n"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_manager_menu_keyboard(WEBAPP_URL)
    )


async def manager_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик статистики менеджера"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    all_orders = db.get_user_orders(user_id, 'manager')
    
    stats = {
        'total': len(all_orders),
        'pending': len([o for o in all_orders if o['status'] == 'pending']),
        'in_progress': len([o for o in all_orders if o['status'] == 'in_progress']),
        'completed': len([o for o in all_orders if o['status'] == 'completed'])
    }
    
    message = f"""
📊 Ваша статистика:

📦 Всего заказов: {stats['total']}
⏳ Ожидают: {stats['pending']}
🚚 В работе: {stats['in_progress']}
✅ Завершено: {stats['completed']}
    """
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_manager_menu_keyboard(WEBAPP_URL)
    )


async def manager_profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик профиля менеджера"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    orders = db.get_user_orders(user_id, 'manager')
    
    message = f"""
📊 Ваш профиль (Менеджер):

🆔 ID: {user['user_id']}
👤 Имя: {user['first_name'] or 'Не указано'}
📝 Фамилия: {user['last_name'] or 'Не указано'}
🔖 Username: @{user['username'] or 'Не указано'}
📦 Заказов: {len(orders)}
👨‍💼 Роль: Менеджер
    """
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_manager_menu(WEBAPP_URL)
    )


async def manager_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик настроек менеджера"""
    query = update.callback_query
    await query.answer()
    
    message = "⚙️ Настройки\n\nЗдесь будут настройки вашего профиля."
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_back_to_manager_menu_keyboard(WEBAPP_URL)
    )


async def back_to_manager_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик возврата в главное меню менеджера"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="Главное меню",
        reply_markup=get_manager_menu(WEBAPP_URL)
    )


def register_manager_handlers(application):
    """Регистрирует обработчики для менеджеров"""
    application.add_handler(CallbackQueryHandler(manager_orders_handler, pattern="^manager_orders$"))
    application.add_handler(CallbackQueryHandler(manager_new_orders_handler, pattern="^manager_new_orders$"))
    application.add_handler(CallbackQueryHandler(manager_in_progress_handler, pattern="^manager_in_progress$"))
    application.add_handler(CallbackQueryHandler(manager_completed_handler, pattern="^manager_completed$"))
    application.add_handler(CallbackQueryHandler(manager_stats_handler, pattern="^manager_stats$"))
    application.add_handler(CallbackQueryHandler(manager_profile_handler, pattern="^manager_profile$"))
    application.add_handler(CallbackQueryHandler(manager_settings_handler, pattern="^manager_settings$"))
    application.add_handler(CallbackQueryHandler(back_to_manager_menu_handler, pattern="^back_to_manager_menu$"))

