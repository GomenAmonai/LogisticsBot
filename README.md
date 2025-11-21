# 🚚 Логистическая платформа

Telegram бот и веб-приложение для управления логистикой с системой ролей (клиент, менеджер, администратор).

## 🏗️ Архитектура проекта

```
IdkProject/
├── handlers/              # Обработчики команд бота
│   ├── start_handler.py
│   ├── client_handlers.py
│   ├── admin_handlers.py
│   ├── manager_handlers.py
│   ├── webapp_handler.py
│   └── admin_commands.py
│
├── keyboards/            # Inline клавиатуры
│   ├── client_keyboard.py
│   ├── admin_keyboard.py
│   └── manager_keyboard.py
│
├── models/              # Модели данных
│   └── user.py
│
├── utils/               # Утилиты
│   ├── error_handler.py
│   ├── telegram_logger.py
│   └── role_helper.py
│
├── webapp/              # Веб-приложение
│   ├── app.py           # Flask API
│   ├── react-app/        # React фронтенд
│   └── templates/        # HTML шаблоны
│
├── data/                 # База данных (создается автоматически)
├── config.py             # Конфигурация
├── database.py           # Работа с БД
├── main.py               # Точка входа бота
├── run_webapp.py         # Запуск веб-приложения
└── requirements.txt      # Python зависимости
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Python
pip install -r requirements.txt

# React (опционально, для разработки)
cd webapp/react-app && npm install
```

### 2. Настройка

Создайте `.env` в корне проекта:

```env
BOT_TOKEN=ваш_токен_от_BotFather
WEBAPP_URL=https://your-app.railway.app
LOG_GROUP_ID=-123456789
ADMIN_IDS=123456789
```

### 3. Запуск через Docker

```bash
docker-compose up -d
```

### 4. Запуск вручную

**Бот:**
```bash
python main.py
```

**Веб-приложение:**
```bash
python run_webapp.py
```

## 📋 Функционал

### 👤 Клиент
- Создание заказов через WebApp
- Просмотр своих заказов
- Отслеживание доставок
- Оплата заказов

### 👨‍💼 Менеджер
- Просмотр новых тикетов
- Принятие тикетов
- Управление заказами
- Обновление статусов

### 👑 Администратор
- Управление пользователями
- Просмотр всех заказов
- Статистика системы

## 🗄️ База данных

SQLite база данных создается автоматически в `data/bot_database.db`.

## 📊 Логирование в группу

Бот отправляет в Telegram группу:
- 🚨 Ошибки бота
- 📦 Новые заказы
- 🎫 Новые тикеты
- 🔴 API запросы с ошибками

Настройка: добавьте `LOG_GROUP_ID` в `.env`

## 🌐 Деплой на Railway

1. Подключите GitHub репозиторий
2. Добавьте переменные окружения
3. Railway автоматически соберет и запустит проект

## 🔧 Утилиты

```bash
# Проверка конфигурации
python check_config.py

# Создание администратора
python utils/create_admin.py <user_id>
```
