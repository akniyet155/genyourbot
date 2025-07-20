FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY predposlednii.py .

# Создаем непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Запускаем бота
CMD ["python", "predposlednii.py"]
