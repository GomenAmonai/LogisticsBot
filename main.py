#!/usr/bin/env python3
"""
Главный файл для запуска Telegram бота
"""
import logging
import os
from telegram.ext import Application
from config import BOT_TOKEN
from handlers.start_handler import start_handler, menu_handler, accept_privacy_handler
from handlers.client_handlers import register_client_handlers
from handlers.admin_handlers import register_admin_handlers
from handlers.manager_handlers import register_manager_handlers
from handlers.webapp_handler import register_webapp_handlers
from handlers.admin_commands import register_admin_commands
from utils.error_handler import register_error_handler
from utils.telegram_logger import init_log_group
from config import LOG_GROUP_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Основная функция запуска бота"""
    # Проверяем наличие .env файла
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        logger.warning(f"⚠️  Файл .env не найден по пути {env_path}")
        logger.info("Создайте файл .env в корне проекта")
    
    if not BOT_TOKEN or BOT_TOKEN == 'your_bot_token_here' or BOT_TOKEN.strip() == '':
        logger.error("=" * 60)
        logger.error("❌ BOT_TOKEN не установлен или содержит placeholder!")
        logger.error("=" * 60)
        logger.error("")
        logger.error("📝 ИНСТРУКЦИЯ:")
        logger.error("1. Откройте файл .env в корне проекта")
        logger.error("2. Найдите строку: BOT_TOKEN=your_bot_token_here")
        logger.error("3. Замените 'your_bot_token_here' на реальный токен от @BotFather")
        logger.error("")
        logger.error("🔑 Как получить токен:")
        logger.error("   - Откройте Telegram и найдите @BotFather")
        logger.error("   - Отправьте команду /newbot")
        logger.error("   - Следуйте инструкциям")
        logger.error("   - Скопируйте полученный токен")
        logger.error("   - Вставьте в .env: BOT_TOKEN=ваш_токен")
        logger.error("")
        logger.error("=" * 60)
        return
    
    # Создаем директорию для данных, если её нет
    os.makedirs('data', exist_ok=True)
    
    # Создаем приложение
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ Приложение создано успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка при создании приложения: {e}")
        return
    
    # Регистрируем обработчики команд
    from telegram.ext import CommandHandler, CallbackQueryHandler
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("menu", menu_handler))
    application.add_handler(CallbackQueryHandler(accept_privacy_handler, pattern="^accept_privacy$"))
    
    # Регистрируем обработчики для разных ролей
    register_client_handlers(application)
    register_admin_handlers(application)
    register_manager_handlers(application)
    
    # Регистрируем обработчики WebApp
    register_webapp_handlers(application)
    
    # Регистрируем административные команды
    register_admin_commands(application)
    
    # Регистрируем обработчик ошибок
    register_error_handler(application)
    
    # Инициализируем группу для логов
    if LOG_GROUP_ID:
        if init_log_group(LOG_GROUP_ID):
            logger.info(f"✅ Группа для логов инициализирована: {LOG_GROUP_ID}")
        else:
            logger.warning(f"⚠️ Не удалось инициализировать группу для логов: {LOG_GROUP_ID}")
    else:
        logger.info("ℹ️ LOG_GROUP_ID не установлен, логи в группу не отправляются")
    
    logger.info("✅ Все обработчики зарегистрированы")
    logger.info("🚀 Бот запущен и готов к работе...")
    logger.info(f"📱 WebApp URL: {os.getenv('WEBAPP_URL', 'Не установлен')}")
    
    # Запускаем бота
    try:
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("⏹️  Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}")


if __name__ == '__main__':
    main()

