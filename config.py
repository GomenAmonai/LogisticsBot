import os
from pathlib import Path
from dotenv import load_dotenv

# Получаем путь к корневой директории проекта
BASE_DIR = Path(__file__).resolve().parent

# Загружаем .env файл из корневой директории (можно переопределить через переменную)
env_path = BASE_DIR / '.env'
if os.getenv('SKIP_DOTENV') == '1':
    pass
else:
    try:
        load_dotenv(dotenv_path=env_path)
    except PermissionError:
        # В окружениях без доступа к .env просто пропускаем загрузку
        pass

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Путь к базе данных (переопределяется через переменную окружения)
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/bot_database.db')

# Тестовый токен для защищенных админских эндпоинтов
TEST_API_TOKEN = os.getenv('TEST_API_TOKEN', '')

# URL для WebApp (можно использовать ngrok или другой сервис для разработки)
# Приоритет: 1) .env файл, 2) значение ниже, 3) автоматически из Docker
WEBAPP_URL = os.getenv('WEBAPP_URL', '')

# Если WEBAPP_URL не установлен, не используем автоматический fallback
# Telegram требует HTTPS, поэтому оставляем пустым если не установлен
if WEBAPP_URL and WEBAPP_URL == 'https://your-webapp-url.com':
    WEBAPP_URL = ''

# Настройки для админов (можно добавить список ID админов)
ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',') if os.getenv('ADMIN_IDS') else []

# ID группы для логов и уведомлений
LOG_GROUP_ID = os.getenv('LOG_GROUP_ID', '')
