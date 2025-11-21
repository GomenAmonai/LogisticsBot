from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def get_client_menu(webapp_url: str = None) -> InlineKeyboardMarkup:
    """Создает главное меню для клиента"""
    keyboard = []
    
    # Кнопка с WebApp для клиента
    # Показываем кнопку только если URL установлен, валиден и HTTPS
    if webapp_url and webapp_url.strip() and webapp_url != 'https://your-webapp-url.com':
        # Telegram требует только HTTPS для WebApp
        if webapp_url.startswith('https://'):
            keyboard.append([
                InlineKeyboardButton(
                    "🌐 Открыть приложение",
                    web_app=WebAppInfo(url=webapp_url)
                )
            ])
    
    keyboard.extend([
        [
            InlineKeyboardButton("📦 Мои заказы", callback_data="client_orders"),
            InlineKeyboardButton("➕ Создать заказ", callback_data="client_create_order")
        ],
        [
            InlineKeyboardButton("📊 Профиль", callback_data="client_profile"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="client_settings")
        ],
        [
            InlineKeyboardButton("📝 Помощь", callback_data="client_help")
        ]
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_back_to_client_menu_keyboard(webapp_url: str = None) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад для клиента"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_client_menu")]]
    return InlineKeyboardMarkup(keyboard)

