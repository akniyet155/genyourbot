# 🌊 DigitalOcean Commands Cheatsheet

## Основные команды управления дроплетом

### 🚀 Управление ботом
```bash
# Запустить бота
sudo systemctl start genyourbot

# Остановить бота  
sudo systemctl stop genyourbot

# Перезапустить бота
sudo systemctl restart genyourbot

# Статус бота
sudo systemctl status genyourbot

# Включить автозапуск
sudo systemctl enable genyourbot

# Отключить автозапуск
sudo systemctl disable genyourbot
```

### 📊 Просмотр логов
```bash
# Логи в реальном времени
sudo journalctl -u genyourbot -f

# Последние 50 строк логов
sudo journalctl -u genyourbot -n 50

# Логи за сегодня
sudo journalctl -u genyourbot --since today

# Логи за последний час
sudo journalctl -u genyourbot --since "1 hour ago"

# Логи с детализацией
sudo journalctl -u genyourbot -o verbose
```

### 🔄 Обновление кода
```bash
# Перейти в папку проекта
cd /home/botuser/genyourbot

# Скачать обновления
sudo -u botuser git pull origin main

# Установить новые зависимости (если есть)
sudo -u botuser ./venv/bin/pip install -r requirements.txt

# Перезапустить бота
sudo systemctl restart genyourbot

# Или одной командой (с алиасом)
bot-update
```

### 🔧 Редактирование файлов
```bash
# Редактировать настройки бота
sudo -u botuser nano /home/botuser/genyourbot/.env

# Редактировать Firebase ключ
sudo -u botuser nano /home/botuser/genyourbot/serviceAccountKey.json

# Редактировать код бота
sudo -u botuser nano /home/botuser/genyourbot/predposlednii.py
```

### 📈 Мониторинг системы
```bash
# Использование CPU и памяти
htop

# Свободное место на диске
df -h

# Использование памяти
free -h

# Активные процессы
ps aux | grep python

# Сетевые подключения
netstat -tulpn

# Информация о дроплете
curl -s http://169.254.169.254/metadata/v1/
```

### 🛡️ Безопасность и файрвол
```bash
# Статус UFW файрвола
sudo ufw status verbose

# Добавить правило файрвола
sudo ufw allow from YOUR_IP to any port 22

# Статус Fail2Ban
sudo fail2ban-client status

# Заблокированные IP
sudo fail2ban-client status sshd

# Просмотр попыток входа
sudo tail -f /var/log/auth.log

# Обновления безопасности
sudo apt update && sudo apt upgrade -y
```

### 💾 Бэкапы и снапшоты
```bash
# Создать бэкап конфигурации
sudo tar -czf /root/genyourbot-backup-$(date +%Y%m%d).tar.gz \
  /home/botuser/genyourbot/.env \
  /home/botuser/genyourbot/serviceAccountKey.json

# Создать полный бэкап проекта
sudo tar -czf /root/genyourbot-full-$(date +%Y%m%d).tar.gz \
  /home/botuser/genyourbot/

# Просмотр бэкапов
ls -la /root/genyourbot-backup-*

# Восстановление из бэкапа
sudo tar -xzf /root/genyourbot-backup-YYYYMMDD.tar.gz -C /

# Создание снапшота через DigitalOcean API
curl -X POST "https://api.digitalocean.com/v2/droplets/$DROPLET_ID/actions" \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"snapshot","name":"genyourbot-snapshot-'$(date +%Y%m%d)'"}'
```

### 🔍 Диагностика проблем
```bash
# Проверить, работает ли Python
sudo -u botuser /home/botuser/genyourbot/venv/bin/python --version

# Проверить зависимости
sudo -u botuser /home/botuser/genyourbot/venv/bin/pip list

# Тест импорта модулей
sudo -u botuser /home/botuser/genyourbot/venv/bin/python -c "import aiogram, firebase_admin; print('OK')"

# Проверить доступность портов
netstat -tlnp | grep :80

# Тест соединения с Telegram API
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe"

# Проверка работы веб-сервера
curl -s http://localhost/health
```

### 🌐 Nginx и веб-сервер
```bash
# Перезапустить Nginx
sudo systemctl restart nginx

# Статус Nginx
sudo systemctl status nginx

# Проверить конфигурацию
sudo nginx -t

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Перезагрузить конфигурацию
sudo nginx -s reload
```

### 🔧 Управление дроплетом
```bash
# Информация о дроплете
curl -s http://169.254.169.254/metadata/v1/droplet_id
curl -s http://169.254.169.254/metadata/v1/region
curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address

# Ресурсы системы
echo "=== CPU Usage ===" && top -bn1 | grep "Cpu(s)"
echo "=== Memory Usage ===" && free -h
echo "=== Disk Usage ===" && df -h
echo "=== Load Average ===" && uptime

# Сетевая статистика
iftop -i eth0  # требует установки: sudo apt install iftop
```

### 📱 Быстрые команды (алиасы)
```bash
# Статус всех сервисов
bot-status

# Логи в реальном времени  
bot-logs

# Перезапуск бота
bot-restart

# Обновление из GitHub
bot-update

# Бэкап конфигурации
bot-backup

# Статистика дроплета
droplet-stats
```

### 🆘 Экстренная диагностика
```bash
# Полная диагностика системы
echo "=== Bot Status ===" && sudo systemctl status genyourbot
echo "=== Bot Logs ===" && sudo journalctl -u genyourbot -n 20
echo "=== System Resources ===" && free -h && df -h
echo "=== Network Info ===" && curl -s ifconfig.me
echo "=== Firewall Status ===" && sudo ufw status
echo "=== Failed Logins ===" && sudo fail2ban-client status sshd
```

### 💡 DigitalOcean специфичные команды
```bash
# Метаданные дроплета
curl -s http://169.254.169.254/metadata/v1/ | jq .

# Информация о соседях (если доступно)
curl -s http://169.254.169.254/metadata/v1/neighbors

# Теги дроплета
curl -s http://169.254.169.254/metadata/v1/tags

# Резервирование плавающего IP (через API)
curl -X POST "https://api.digitalocean.com/v2/floating_ips" \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"assign","resource":"$DROPLET_ID"}'
```

## 🎯 Полезные советы для DigitalOcean

1. **Мониторинг** - включите алерты в панели DO
2. **Снапшоты** - делайте еженедельные снапшоты перед обновлениями
3. **Floating IP** - зарезервируйте статический IP для продакшена
4. **Load Balancer** - используйте при росте нагрузки
5. **Managed Database** - переходите на отдельную БД при масштабировании
