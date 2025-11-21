FROM python:3.9-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для данных
RUN mkdir -p data

# Открываем порты
EXPOSE 5000

# Команда по умолчанию (можно переопределить)
CMD ["python", "run_webapp.py"]

