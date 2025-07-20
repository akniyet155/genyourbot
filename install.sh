#!/bin/bash

# Скрипт автоматической установки GenYourBot на Ubuntu сервер
# Запуск: curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/genyourbot/main/install.sh | bash

set -e

echo "🚀 Установка GenYourBot..."

# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
sudo apt install -y python3 python3-pip python3-venv git curl

# Клонируем репозиторий
if [ ! -d "genyourbot" ]; then
    git clone https://github.com/YOUR_USERNAME/genyourbot.git
fi

cd genyourbot

# Создаем виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем файл .env
if [ ! -f ".env" ]; then
    echo "📝 Создаем файл .env..."
    echo "BOT_TOKEN=your_bot_token_here" > .env
    echo "CRYPTOBOT_API_TOKEN=your_cryptobot_token_here" >> .env
    echo "⚠️  ВАЖНО: Отредактируйте файл .env и добавьте ваши токены!"
    echo "nano .env"
fi

# Устанавливаем systemd service
sudo cp genyourbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable genyourbot

echo "✅ Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте .env файл: nano .env"
echo "2. Добавьте serviceAccountKey.json"
echo "3. Запустите бота: sudo systemctl start genyourbot"
echo "4. Проверьте статус: sudo systemctl status genyourbot"
