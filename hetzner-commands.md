# 🇩🇪 Hetzner Cloud Commands Cheatsheet

## Основные команды управления сервером

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
```

### 🛡️ Безопасность
```bash
# Статус файрвола
sudo ufw status

# Просмотр попыток входа
sudo tail -f /var/log/auth.log

# Обновления безопасности
sudo apt update && sudo apt upgrade -y
```

### 💾 Бэкап и восстановление
```bash
# Создать бэкап конфигурации
sudo tar -czf /root/genyourbot-backup-$(date +%Y%m%d).tar.gz \
  /home/botuser/genyourbot/.env \
  /home/botuser/genyourbot/serviceAccountKey.json

# Просмотр бэкапов
ls -la /root/genyourbot-backup-*

# Восстановление из бэкапа
sudo tar -xzf /root/genyourbot-backup-YYYYMMDD.tar.gz -C /
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
```

### 🌐 Nginx (веб-сервер)
```bash
# Перезапустить Nginx
sudo systemctl restart nginx

# Статус Nginx
sudo systemctl status nginx

# Проверить конфигурацию
sudo nginx -t

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
```

### 📱 Быстрая проверка
```bash
# Одной командой: статус всех сервисов
sudo systemctl status genyourbot nginx

# Проверка что бот отвечает
curl -s http://localhost/health

# Узнать IP сервера
curl -s ifconfig.me
```

### 🆘 В случае проблем
```bash
# Полная диагностика
echo "=== Bot Status ===" && sudo systemctl status genyourbot
echo "=== Bot Logs ===" && sudo journalctl -u genyourbot -n 20
echo "=== System Info ===" && free -h && df -h
echo "=== Network ===" && curl -s ifconfig.me
```

## 💡 Полезные алиасы

Добавьте в `~/.bashrc` для удобства:
```bash
alias bot-status='sudo systemctl status genyourbot'
alias bot-logs='sudo journalctl -u genyourbot -f'
alias bot-restart='sudo systemctl restart genyourbot'
alias bot-update='cd /home/botuser/genyourbot && sudo -u botuser git pull && sudo systemctl restart genyourbot'
```

После добавления выполните: `source ~/.bashrc`
