# 🌊 Деплой GenYourBot на DigitalOcean

## 📋 Пошаговая инструкция:

### 1. Создание дроплета на DigitalOcean

1. **Регистрация:**
   - Идите на https://www.digitalocean.com
   - Создайте аккаунт
   - **Получите $200 кредитов** на 60 дней для новых пользователей!

2. **Создание дроплета:**
   - Нажмите "Create" → "Droplets"
   - **Image:** Ubuntu 22.04 LTS
   - **Size:** Basic $4/month (1GB RAM, 1 vCPU, 25GB SSD)
   - **Region:** выберите ближайший (Amsterdam, Frankfurt для СНГ)
   - **Authentication:** SSH Key (рекомендуется) или Password
   - **Hostname:** genyourbot-server

### 2. Подключение к серверу

```bash
# Подключитесь по SSH (замените IP на ваш)
ssh root@YOUR_DROPLET_IP
```

### 3. Автоматическая установка

Выполните эту команду на сервере:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/genyourbot/main/digitalocean-install.sh | bash
```

### 4. Настройка переменных окружения

```bash
# Перейдите в папку проекта
cd genyourbot

# Отредактируйте файл окружения
nano .env
```

Добавьте ваши токены:
```env
BOT_TOKEN=your_telegram_bot_token
CRYPTOBOT_API_TOKEN=your_cryptobot_token
```

### 5. Добавление Firebase ключа

```bash
# Создайте файл serviceAccountKey.json
nano serviceAccountKey.json
# Вставьте содержимое вашего Firebase ключа
```

### 6. Запуск бота

```bash
# Запустите сервис
sudo systemctl start genyourbot

# Проверьте статус
sudo systemctl status genyourbot

# Включите автозапуск
sudo systemctl enable genyourbot
```

### 7. Проверка логов

```bash
# Просмотр логов в реальном времени
sudo journalctl -u genyourbot -f

# Просмотр последних логов
sudo journalctl -u genyourbot -n 50
```

## 🔧 Управление дроплетом

```bash
# Остановить бота
sudo systemctl stop genyourbot

# Перезапустить бота
sudo systemctl restart genyourbot

# Обновить код из GitHub
cd genyourbot && git pull origin main && sudo systemctl restart genyourbot
```

## 💰 Стоимость

- **$4/месяц** за Basic дроплет
- **$200 кредитов** для новых пользователей (50 месяцев бесплатно!)
- **Почасовая оплата** - можете остановить дроплет когда не нужен
- **Snapshots** - $0.05/GB/месяц для бэкапов

## 🌍 Выбор региона

Рекомендуемые регионы для СНГ:
- **Amsterdam** (AMS3) - лучший пинг для Европы/России
- **Frankfurt** (FRA1) - хорошая альтернатива
- **London** (LON1) - тоже неплохо
- **New York** (NYC1) - если нужна стабильность

## 🛡️ Безопасность

DigitalOcean автоматически настроит:
- ✅ Cloud Firewall
- ✅ DDoS защита
- ✅ SSH ключи
- ✅ Regular security updates

## 📊 Мониторинг

В панели DigitalOcean вы увидите:
- 📈 CPU, Memory, Disk usage
- 📊 Bandwidth utilization  
- 📡 Network In/Out
- ⚡ Uptime monitoring
- 🔔 Alert policies

## 🎁 Дополнительные возможности

- **Managed Databases** - PostgreSQL, MySQL, Redis
- **Spaces** - S3-совместимое хранилище
- **Load Balancers** - для масштабирования
- **Kubernetes** - для больших проектов
- **App Platform** - PaaS альтернатива

## 🆘 Поддержка

- 📧 Ticket система 24/7
- 📚 Огромная база знаний
- 🇬🇧 Поддержка на английском
- 💬 Активное сообщество
- 📖 Подробные туториалы

## 🔄 Бэкапы

```bash
# Автоматические снапшоты через веб-интерфейс
# Или ручной бэкап конфигурации:
sudo tar -czf /root/genyourbot-backup-$(date +%Y%m%d).tar.gz \
  /home/botuser/genyourbot/.env \
  /home/botuser/genyourbot/serviceAccountKey.json
```

## 🚀 Масштабирование

Когда бот станет популярнее:
- **Resize дроплет** - больше RAM/CPU за пару кликов
- **Load Balancer** - распределение нагрузки
- **Managed Database** - отдельная БД
- **CDN** - для статических файлов

---

**🎉 С $200 кредитами вы получаете 50 месяцев бесплатного хостинга!**

Готовы начать? Создавайте дроплет на DigitalOcean и запускайте установочный скрипт!
