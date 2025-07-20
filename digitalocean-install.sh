#!/bin/bash

# 🌊 DigitalOcean Auto-Install Script for GenYourBot
# Скрипт автоматической установки бота на DigitalOcean

set -e

echo "🌊 Starting GenYourBot installation on DigitalOcean..."

# Обновление системы
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Установка необходимых пакетов
echo "🔧 Installing required packages..."
apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx htop ufw fail2ban

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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Nginx конфигурация для мониторинга
cat > /etc/nginx/sites-available/genyourbot << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        return 200 "GenYourBot is running on DigitalOcean! 🌊";
        add_header Content-Type text/plain;
    }
    
    location /health {
        return 200 "OK";
        add_header Content-Type text/plain;
    }
    
    location /status {
        return 200 "DigitalOcean Droplet Active";
        add_header Content-Type text/plain;
    }
}
EOF

# Активация Nginx сайта
ln -sf /etc/nginx/sites-available/genyourbot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Тестирование и перезапуск Nginx
nginx -t && systemctl restart nginx

# Настройка UFW Firewall
echo "🛡️ Configuring UFW firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'

# Настройка Fail2Ban для защиты SSH
echo "🔒 Configuring Fail2Ban..."
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
cat >> /etc/fail2ban/jail.local << 'EOF'

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Создание файла .env (шаблон)
echo "📝 Creating environment template..."
sudo -u botuser cat > /home/botuser/genyourbot/.env.template << 'EOF'
BOT_TOKEN=your_telegram_bot_token_here
CRYPTOBOT_API_TOKEN=your_cryptobot_api_token_here
EOF

# Установка автоматических обновлений безопасности
echo "🔄 Setting up automatic security updates..."
apt install -y unattended-upgrades
echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades

# Настройка swap файла (рекомендуется для 1GB дроплета)
echo "💾 Setting up swap file..."
if [ ! -f /swapfile ]; then
    fallocate -l 1G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Оптимизация для DigitalOcean
echo "⚡ Optimizing for DigitalOcean..."
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf

# Создание полезных алиасов
echo "🔧 Creating useful aliases..."
cat >> /home/botuser/.bashrc << 'EOF'
# GenYourBot aliases
alias bot-status='sudo systemctl status genyourbot'
alias bot-logs='sudo journalctl -u genyourbot -f'
alias bot-restart='sudo systemctl restart genyourbot'
alias bot-update='cd ~/genyourbot && git pull && sudo systemctl restart genyourbot'
alias bot-backup='sudo tar -czf ~/backup-$(date +%Y%m%d).tar.gz ~/genyourbot/.env ~/genyourbot/serviceAccountKey.json'
alias droplet-stats='echo "=== System Info ===" && free -h && echo && df -h && echo "=== Network ===" && curl -s ifconfig.me'
EOF

# Перезагрузка systemd
systemctl daemon-reload

# Информация о DigitalOcean Droplet
DROPLET_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
DROPLET_REGION=$(curl -s http://169.254.169.254/metadata/v1/region)

echo ""
echo "🎉 GenYourBot installation completed successfully on DigitalOcean!"
echo ""
echo "💧 Droplet Information:"
echo "  • IP Address: $DROPLET_IP"
echo "  • Region: $DROPLET_REGION"
echo "  • Size: 1GB RAM, 1 vCPU, 25GB SSD"
echo "  • Cost: $4/month"
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
echo "- Update bot: cd /home/botuser/genyourbot && git pull && systemctl restart genyourbot"
echo "- System stats: free -h && df -h"
echo ""
echo "🌐 Web endpoints:"
echo "- Health check: http://$DROPLET_IP/health"
echo "- Status page: http://$DROPLET_IP/status"
echo ""
echo "🛡️ Security features enabled:"
echo "- ✅ UFW Firewall (SSH + HTTP/HTTPS only)"
echo "- ✅ Fail2Ban (SSH brute-force protection)"
echo "- ✅ Automatic security updates"
echo "- ✅ 1GB Swap file for better performance"
echo ""
echo "💰 DigitalOcean perks:"
echo "- 🎁 $200 credits for new users (50 months free!)"
echo "- 📊 Built-in monitoring in DO panel"
echo "- 🔄 Easy droplet resizing"
echo "- 📸 Snapshot backups available"
echo ""
echo "✅ GenYourBot is ready to deploy on DigitalOcean! 🌊"
