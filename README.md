# GenYourBot 🤖

Telegram бот для создания персональных тестов с мультиязычной поддержкой.

## Возможности

- 🌍 Поддержка 3 языков: русский, английский, фарси
- 🧪 Создание персональных тестов из 10 вопросов
- 📸 Прикрепление фото/GIF к тестам
- 💎 Система кристаллов за приглашения
- 🪙 Система монет за покупки ответов
- 💰 Вывод средств через CryptoBot (USDT)
- 🔗 Реферальная система

## Технологии

- Python 3.11+
- aiogram 3.7 (Telegram Bot API)
- Firebase Firestore (база данных)
- CryptoBot API (платежи)

## Установка

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd genyourbot
```

2. Создайте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env`:
```env
BOT_TOKEN=your_telegram_bot_token
CRYPTOBOT_API_TOKEN=your_cryptobot_token
```

5. Добавьте `serviceAccountKey.json` (Firebase credentials)

6. Запустите бота:
```bash
python predposlednii.py
```

### Деплой на сервер

#### Ubuntu VPS

1. Подключитесь к серверу и установите зависимости:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

2. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd genyourbot
```

3. Создайте виртуальное окружение:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Настройте environment variables и Firebase credentials

5. Создайте systemd service:
```bash
sudo cp genyourbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable genyourbot
sudo systemctl start genyourbot
```

6. Проверьте статус:
```bash
sudo systemctl status genyourbot
```

#### Автоматический деплой

Используйте скрипт `deploy.sh` для быстрого обновления:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Структура проекта

```
genyourbot/
├── predposlednii.py      # Основной код бота
├── requirements.txt      # Python зависимости
├── .env                 # Environment variables
├── serviceAccountKey.json # Firebase credentials
├── genyourbot.service   # Systemd service файл
├── deploy.sh           # Скрипт деплоя
└── README.md           # Документация
```

## Переменные окружения

- `BOT_TOKEN` - токен Telegram бота от @BotFather
- `CRYPTOBOT_API_TOKEN` - токен CryptoBot API

## Firebase Setup

1. Создайте проект в Firebase Console
2. Включите Firestore Database
3. Создайте Service Account и скачайте JSON ключ
4. Переименуйте в `serviceAccountKey.json`

## Мониторинг

Просмотр логов на сервере:
```bash
sudo journalctl -u genyourbot -f
```

## Поддержка

При возникновении проблем создайте issue в репозитории.
