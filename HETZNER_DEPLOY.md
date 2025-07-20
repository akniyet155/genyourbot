# 🇩🇪 Деплой GenYourBot на Hetzner Cloud

## 📋 Пошаговая инструкция:

### 1. Создание сервера на Hetzner

1. **Регистрация:**
   - Идите на https://www.hetzner.com/cloud
   - Создайте аккаунт
   - Подтвердите email

2. **Создание проекта:**
   - В консоли нажмите "New Project"
   - Назовите "GenYourBot"

3. **Создание сервера:**
   - Нажмите "Add Server"
   - **Location:** Nuremberg (ближе к СНГ)
   - **Image:** Ubuntu 22.04
   - **Type:** CX11 (€4.51/месяц, 1 vCPU, 2GB RAM, 20GB SSD)
   - **SSH Key:** Добавьте ваш публичный ключ
   - **Name:** genyourbot-server

### 2. Подключение к серверу

```bash
# Подключитесь по SSH (замените IP на ваш)
ssh root@YOUR_SERVER_IP
```

### 3. Автоматическая установка

Выполните эту команду на сервере:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/genyourbot/main/hetzner-install.sh | bash
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

## 🔧 Управление сервисом

```bash
# Остановить бота
sudo systemctl stop genyourbot

# Перезапустить бота
sudo systemctl restart genyourbot

# Обновить код из GitHub
cd genyourbot && git pull origin main && sudo systemctl restart genyourbot
```

## 💰 Стоимость

- **€4.51/месяц** = ~$5/месяц
- **Первый месяц часто со скидкой**
- **Оплата почасовая** - можете остановить сервер когда не нужен

## 🛡️ Безопасность

Hetzner автоматически настроит:
- ✅ Firewall (только SSH и HTTP/HTTPS)
- ✅ Автоматические обновления безопасности
- ✅ DDoS защита
- ✅ Backup возможности

## 📊 Мониторинг

В панели Hetzner вы увидите:
- 📈 Использование CPU/RAM
- 📊 Сетевой трафик
- 💾 Использование диска
- ⚡ Время работы (uptime)

## 🆘 Поддержка

- 📧 Email поддержка 24/7
- 📚 Отличная документация
- 🇬🇧 Поддержка на английском
- 💬 Активное сообщество

---

**Готовы начать?** Создайте сервер на Hetzner и запустите установочный скрипт!
