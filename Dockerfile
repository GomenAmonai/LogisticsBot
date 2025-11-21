# Этап 1: Сборка React приложения
FROM node:18-alpine AS react-builder

WORKDIR /app/react-app

# Копируем package файлы
COPY webapp/react-app/package*.json ./

# Устанавливаем зависимости
RUN npm install --legacy-peer-deps --prefer-offline

# Копируем исходники React
COPY webapp/react-app/ .

# Собираем React приложение (выход в ../static/react согласно vite.config.js)
RUN npm run build

# Этап 2: Python приложение
FROM python:3.9-slim

WORKDIR /app

# Копируем файлы зависимостей Python
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Копируем собранный React из builder (vite собирает в ../static/react)
COPY --from=react-builder /app/static/react ./webapp/static/react

# Создаем директорию для данных
RUN mkdir -p data

# Открываем порты
EXPOSE 5000

# Команда по умолчанию
CMD ["python", "run_webapp.py"]

