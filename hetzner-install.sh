#!/bin/bash

# 🇩🇪 Hetzner Cloud Auto-Install Script for GenYourBot
# Скрипт автоматической установки бота на Hetzner Cloud

set -e

echo "🇩🇪 Starting GenYourBot installation on Hetzner Cloud..."

# Обновление системы
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Установка необходимых пакетов
echo "🔧 Installing required packages..."
apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Создание пользователя для бота
echo "👤 Creating bot user..."
if ! id "botuser" &>/dev/null; then
    useradd -m -s /bin/bash botuser
    usermod -aG sudo botuser
fi

# Переход в домашнюю папку пользователя
cd /home/botuser

# Клонирование репозитория (замените на ваш GitHub)
echo "📥 Cloning repository..."
if [ ! -d "genyourbot" ]; then
    sudo -u botuser git clone https://github.com/YOUR_USERNAME/genyourbot.git
    cd genyourbot
else
    cd genyourbot
    sudo -u botuser git pull origin main
fi

# Создание виртуального окружения
echo "🐍 Setting up Python virtual environment..."
sudo -u botuser python3 -m venv venv
sudo -u botuser ./venv/bin/pip install --upgrade pip

# Установка зависимостей
echo "📚 Installing Python dependencies..."
sudo -u botuser ./venv/bin/pip install -r requirements.txt

# Создание файлов конфигурации
echo "⚙️ Creating configuration files..."

# Systemd service файл
cat > /etc/systemd/system/genyourbot.service << 'EOF'
[Unit]
Description=GenYourBot Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=/home/botuser/genyourbot
Environment=PATH=/home/botuser/genyourbot/venv/bin
ExecStart=/home/botuser/genyourbot/venv/bin/python predposlednii.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Nginx конфигурация для мониторинга (опционально)
cat > /etc/nginx/sites-available/genyourbot << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        return 200 "GenYourBot is running!";
        add_header Content-Type text/plain;
    }
    
    location /health {
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
EOF

# Активация Nginx сайта
ln -sf /etc/nginx/sites-available/genyourbot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Перезапуск Nginx
systemctl restart nginx

# Настройка firewall
echo "🛡️ Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'

# Создание файла .env (шаблон)
echo "📝 Creating environment template..."
sudo -u botuser cat > /home/botuser/genyourbot/.env.template << 'EOF'
BOT_TOKEN=your_telegram_bot_token_here
CRYPTOBOT_API_TOKEN=your_cryptobot_api_token_here
EOF

# Установка автоматических обновлений безопасности
echo "🔒 Setting up automatic security updates..."
apt install -y unattended-upgrades
echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades

# Перезагрузка systemd
systemctl daemon-reload

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Create .env file: cp /home/botuser/genyourbot/.env.template /home/botuser/genyourbot/.env"
echo "2. Edit .env file: nano /home/botuser/genyourbot/.env"
echo "3. Add your serviceAccountKey.json file"
echo "4. Start the bot: systemctl start genyourbot"
echo "5. Enable autostart: systemctl enable genyourbot"
echo ""
echo "🔍 Useful commands:"
echo "- Check status: systemctl status genyourbot"
echo "- View logs: journalctl -u genyourbot -f"
echo "- Restart bot: systemctl restart genyourbot"
echo ""
echo "💰 Your server costs: €4.51/month (~$5/month)"
echo "🌐 Server IP: $(curl -s ifconfig.me)"
echo ""
echo "✅ GenYourBot is ready to deploy on Hetzner Cloud!"
