#!/usr/bin/env python3
"""
Скрипт для запуска веб-приложения
"""
import os
import sys
from pathlib import Path

# Добавляем путь к webapp
sys.path.insert(0, str(Path(__file__).resolve().parent))

from webapp.app import app

if __name__ == '__main__':
    # Railway и другие платформы используют переменную PORT
    # По умолчанию используем 5000 (как в webapp/app.py и docker-compose.yml)
    port = int(os.getenv('PORT', os.getenv('WEBAPP_PORT', 5000)))
    # В продакшене отключаем debug
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Важно: Railway требует слушать на 0.0.0.0
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"🚀 Запуск веб-приложения на {host}:{port}")
    print(f"📱 URL: http://localhost:{port}")
    print(f"🌐 Debug mode: {debug}")
    print(f"🌍 Host: {host}")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Порт {port} занят!")
            print(f"💡 Попробуйте другой порт: PORT=5002 python run_webapp.py")
            print(f"💡 Или остановите процесс: lsof -ti :{port} | xargs kill -9")
        else:
            raise

