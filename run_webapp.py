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
    port = int(os.getenv('WEBAPP_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Запуск веб-приложения на порту {port}")
    print(f"📱 URL: http://localhost:{port}")
    print(f"🌐 Для Telegram WebApp используйте ngrok или другой туннелинг")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

