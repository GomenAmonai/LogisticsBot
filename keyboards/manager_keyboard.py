from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def get_manager_menu(webapp_url: str = None) -> InlineKeyboardMarkup:
    """Создает главное меню для менеджера логистической компании"""
    keyboard = []
    
    # Кнопка с WebApp для менеджера (только HTTPS)
    if webapp_url and webapp_url.strip() and webapp_url.startswith('https://'):
        keyboard.append([
            InlineKeyboardButton(
                "🌐 Панель управления (WebApp)",
                web_app=WebAppInfo(url=webapp_url)
            )
        ])
    
    keyboard.extend([
        [
            InlineKeyboardButton("📦 Мои заказы", callback_data="manager_orders"),
            InlineKeyboardButton("📋 Новые заказы", callback_data="manager_new_orders")
        ],
        [
            InlineKeyboardButton("🚚 В работе", callback_data="manager_in_progress"),
            InlineKeyboardButton("✅ Завершенные", callback_data="manager_completed")
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data="manager_stats"),
            InlineKeyboardButton("📊 Профиль", callback_data="manager_profile")
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data="manager_settings")
        ]
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_back_to_manager_menu_keyboard(webapp_url: str = None) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад для менеджера"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_manager_menu")]]
    return InlineKeyboardMarkup(keyboard)

