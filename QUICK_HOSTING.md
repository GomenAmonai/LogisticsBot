# 🚀 Быстрый хостинг на Railway

## 1. Регистрация
- Зайдите на https://railway.app
- Войдите через GitHub

## 2. Создание проекта
- New Project → Deploy from GitHub repo
- Выберите ваш репозиторий

## 3. Переменные окружения
Добавьте в Railway:
```
BOT_TOKEN=ваш_токен
FLASK_SECRET_KEY=случайная_строка_32_символа
WEBAPP_PORT=5000
```

## 4. Получите URL
Railway выдаст: `https://your-app.railway.app`

## 5. Настройте бота
В `.env`:
```
WEBAPP_URL=https://your-app.railway.app
```

В BotFather:
- Main App → Enter URL: `https://your-app.railway.app`
- Launch Mode: Fullsize
- Save

## 6. Подключите домен (опционально)
- Settings → Domains
- Добавьте ваш домен
- Настройте DNS CNAME

Готово! 🎉
