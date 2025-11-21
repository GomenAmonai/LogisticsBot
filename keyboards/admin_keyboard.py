from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def get_admin_menu(webapp_url: str = None) -> InlineKeyboardMarkup:
    """Создает главное меню для администратора"""
    keyboard = []
    
    # Кнопка с WebApp для админа (только HTTPS)
    if webapp_url and webapp_url.strip() and webapp_url.startswith('https://'):
        keyboard.append([
            InlineKeyboardButton(
                "🌐 Админ-панель (WebApp)",
                web_app=WebAppInfo(url=webapp_url)
            )
        ])
    
    keyboard.extend([
        [
            InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users"),
            InlineKeyboardButton("📦 Все заказы", callback_data="admin_orders")
        ],
        [
            InlineKeyboardButton("👨‍💼 Управление менеджерами", callback_data="admin_managers"),
            InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton("⚙️ Настройки системы", callback_data="admin_system_settings"),
            InlineKeyboardButton("📝 Логи", callback_data="admin_logs")
        ],
        [
            InlineKeyboardButton("📊 Профиль", callback_data="admin_profile")
        ]
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_admin_panel_menu() -> InlineKeyboardMarkup:
    """Меню для админ-панели"""
    keyboard = [
        [
            InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_user_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для управления пользователями"""
    keyboard = [
        [
            InlineKeyboardButton("👥 Список клиентов", callback_data="admin_list_clients"),
            InlineKeyboardButton("👨‍💼 Список менеджеров", callback_data="admin_list_managers")
        ],
        [
            InlineKeyboardButton("➕ Назначить роль", callback_data="admin_set_role"),
            InlineKeyboardButton("🔍 Найти пользователя", callback_data="admin_find_user")
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

