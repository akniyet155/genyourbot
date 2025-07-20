#!/bin/bash

# Скрипт для деплоя бота на Ubuntu сервер

echo "🚀 Начинаем деплой GenYourBot..."

# Обновляем код из git
git pull origin main

# Активируем виртуальное окружение
source .venv/bin/activate

# Устанавливаем/обновляем зависимости
pip install -r requirements.txt

# Перезапускаем сервис
sudo systemctl restart genyourbot

# Проверяем статус
sudo systemctl status genyourbot

echo "✅ Деплой завершен!"
