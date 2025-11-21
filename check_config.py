#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации бота
"""
import os
import sys
from pathlib import Path

def check_config():
    """Проверяет конфигурацию бота"""
    print("=" * 60)
    print("🔍 Проверка конфигурации бота")
    print("=" * 60)
    print()
    
    # Проверяем наличие .env файла
    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / '.env'
    
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        print(f"   Ожидаемый путь: {env_path}")
        print()
        print("📝 Решение: Создайте файл .env в корне проекта")
        return False
    
    print(f"✅ Файл .env найден: {env_path}")
    print()
    
    # Читаем .env файл
    try:
        with open(env_path, 'r') as f:
            env_content = f.read()
    except Exception as e:
        print(f"❌ Ошибка при чтении .env: {e}")
        return False
    
    # Проверяем BOT_TOKEN
    bot_token_line = None
    for line in env_content.split('\n'):
        stripped = line.strip()
        # Пропускаем комментарии и пустые строки
        if stripped and not stripped.startswith('#'):
            if stripped.startswith('BOT_TOKEN='):
                bot_token_line = line
                break
    
    if not bot_token_line:
        print("❌ BOT_TOKEN не найден в .env файле")
        print()
        print("📝 Решение: Добавьте строку BOT_TOKEN=ваш_токен в .env")
        return False
    
    # Извлекаем токен
    token = bot_token_line.split('=', 1)[1].strip()
    
    if not token or token == 'your_bot_token_here' or token == '':
        print("❌ BOT_TOKEN не установлен или содержит placeholder!")
        print(f"   Текущее значение: {token if token else '(пусто)'}")
        print()
        print("📝 РЕШЕНИЕ:")
        print("   1. Откройте файл .env")
        print("   2. Найдите строку: BOT_TOKEN=your_bot_token_here")
        print("   3. Замените 'your_bot_token_here' на реальный токен")
        print()
        print("🔑 Как получить токен:")
        print("   - Откройте Telegram и найдите @BotFather")
        print("   - Отправьте команду /newbot")
        print("   - Следуйте инструкциям")
        print("   - Скопируйте полученный токен")
        print("   - Вставьте в .env: BOT_TOKEN=ваш_токен")
        return False
    
    # Проверяем формат токена (должен содержать : и быть достаточно длинным)
    if ':' not in token or len(token) < 20:
        print("⚠️  BOT_TOKEN выглядит неправильно")
        print(f"   Токен должен быть в формате: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        print(f"   Ваш токен: {token[:10]}... (первые 10 символов)")
        return False
    
    print(f"✅ BOT_TOKEN установлен: {token[:10]}...{token[-5:]}")
    print()
    
    # Проверяем WEBAPP_URL (опционально)
    webapp_url = None
    for line in env_content.split('\n'):
        if line.strip().startswith('WEBAPP_URL='):
            webapp_url = line.split('=', 1)[1].strip()
            break
    
    if webapp_url and webapp_url != '' and webapp_url != 'https://your-webapp-url.com':
        print(f"✅ WEBAPP_URL установлен: {webapp_url}")
    else:
        print("ℹ️  WEBAPP_URL не установлен (опционально)")
    
    print()
    print("=" * 60)
    print("✅ Конфигурация в порядке! Можно запускать бота: python main.py")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = check_config()
    sys.exit(0 if success else 1)

