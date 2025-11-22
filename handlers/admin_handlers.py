import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import Database
from models.user import UserRole
from keyboards.admin_keyboard import get_admin_menu, get_admin_panel_menu, get_user_management_keyboard
from utils.role_helper import check_user_role
from config import WEBAPP_URL

logger = logging.getLogger(__name__)
db = Database()


async def admin_users_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик управления пользователями"""
    query = update.callback_query
    await query.answer()
    
    user_dict, role = check_user_role(update, db)
    
    if role != UserRole.ADMIN:
        await query.answer("❌ У вас нет доступа к этой функции", show_alert=True)
        return
    
    message = "👥 Управление пользователями\n\nВыберите действие:"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_user_management_keyboard()
    )


async def admin_list_clients_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик списка клиентов"""
    query = update.callback_query
    await query.answer()
    
    clients = db.get_all_users(role=UserRole.CLIENT)
    
    if not clients:
        message = "👥 Клиентов не найдено"
    else:
        message = f"👥 Список клиентов ({len(clients)}):\n\n"
        for client in clients[:20]:  # Показываем первых 20
            message += f"• {client['first_name']} (@{client['username'] or 'нет username'})\n"
            message += f"  ID: {client['user_id']}\n\n"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_admin_panel_menu()
    )


async def admin_list_managers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик списка менеджеров"""
    query = update.callback_query
    await query.answer()
    
    managers = db.get_all_users(role=UserRole.MANAGER)
    
    if not managers:
        message = "👨‍💼 Менеджеров не найдено"
    else:
        message = f"👨‍💼 Список менеджеров ({len(managers)}):\n\n"
        for manager in managers[:20]:
            message += f"• {manager['first_name']} (@{manager['username'] or 'нет username'})\n"
            message += f"  ID: {manager['user_id']}\n\n"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_admin_panel_menu()
    )


async def admin_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик просмотра всех заказов"""
    query = update.callback_query
    await query.answer()
    
    orders = db.get_user_orders(0, UserRole.ADMIN)  # Админ видит все заказы
    
    if not orders:
        message = "📦 Заказов не найдено"
    else:
        message = f"📦 Все заказы ({len(orders)}):\n\n"
        for order in orders[:10]:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🚚',
                'completed': '✅',
                'cancelled': '❌'
            }.get(order['status'], '❓')
            
            message += f"{status_emoji} Заказ #{order['id']}\n"
            message += f"   Клиент ID: {order['client_id']}\n"
            message += f"   Статус: {order['status']}\n\n"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_admin_panel_menu()
    )


async def admin_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик статистики"""
    query = update.callback_query
    await query.answer()
    
    all_users = db.get_all_users()
    clients = db.get_all_users(role=UserRole.CLIENT)
    managers = db.get_all_users(role=UserRole.MANAGER)
    orders = db.get_user_orders(0, UserRole.ADMIN)
    
    message = f"""
📊 Статистика системы:

👥 Всего пользователей: {len(all_users)}
   • Клиентов: {len(clients)}
   • Менеджеров: {len(managers)}
   • Админов: {len(all_users) - len(clients) - len(managers)}

📦 Всего заказов: {len(orders)}
    """
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_admin_panel_menu()
    )


async def admin_profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик профиля админа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    message = f"""
📊 Ваш профиль (Администратор):

🆔 ID: {user['user_id']}
👤 Имя: {user['first_name'] or 'Не указано'}
📝 Фамилия: {user['last_name'] or 'Не указано'}
🔖 Username: @{user['username'] or 'Не указано'}
👑 Роль: Администратор
    """
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_admin_menu(WEBAPP_URL)
    )


async def admin_system_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик настроек системы"""
    query = update.callback_query
    await query.answer()
    
    message = "⚙️ Настройки системы\n\nЗдесь будут настройки системы."
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_admin_panel_menu()
    )


async def admin_logs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик логов"""
    query = update.callback_query
    await query.answer()
    
    message = "📝 Логи системы\n\nЗдесь будут логи системы."
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_admin_panel_menu()
    )


async def back_to_admin_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик возврата в главное меню админа"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="Главное меню",
        reply_markup=get_admin_menu(WEBAPP_URL)
    )


async def admin_set_role_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик назначения роли пользователю"""
    query = update.callback_query
    await query.answer()
    
    user_dict, role = check_user_role(update, db)
    
    if role != UserRole.ADMIN:
        await query.answer("❌ У вас нет доступа к этой функции", show_alert=True)
        return
    
    message = "➕ Назначить роль\n\nОтправьте команду в формате:\n/setrole <user_id> <role>\n\nРоли: client, manager, admin"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_admin_panel_menu()
    )


async def admin_find_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик поиска пользователя"""
    query = update.callback_query
    await query.answer()
    
    user_dict, role = check_user_role(update, db)
    
    if role != UserRole.ADMIN:
        await query.answer("❌ У вас нет доступа к этой функции", show_alert=True)
        return
    
    message = "🔍 Найти пользователя\n\nОтправьте команду в формате:\n/finduser <user_id> или /finduser @username"
    
    await query.edit_message_text(
        text=message,
        reply_markup=get_admin_panel_menu()
    )


def register_admin_handlers(application):
    """Регистрирует обработчики для администраторов"""
    application.add_handler(CallbackQueryHandler(admin_users_handler, pattern="^admin_users$"))
    application.add_handler(CallbackQueryHandler(admin_list_clients_handler, pattern="^admin_list_clients$"))
    application.add_handler(CallbackQueryHandler(admin_list_managers_handler, pattern="^admin_list_managers$"))
    application.add_handler(CallbackQueryHandler(admin_orders_handler, pattern="^admin_orders$"))
    application.add_handler(CallbackQueryHandler(admin_stats_handler, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_profile_handler, pattern="^admin_profile$"))
    application.add_handler(CallbackQueryHandler(admin_system_settings_handler, pattern="^admin_system_settings$"))
    application.add_handler(CallbackQueryHandler(admin_logs_handler, pattern="^admin_logs$"))
    application.add_handler(CallbackQueryHandler(admin_set_role_handler, pattern="^admin_set_role$"))
    application.add_handler(CallbackQueryHandler(admin_find_user_handler, pattern="^admin_find_user$"))
    application.add_handler(CallbackQueryHandler(back_to_admin_menu_handler, pattern="^back_to_admin_menu$"))

