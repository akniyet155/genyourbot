# Python 3.11  |  aiogram 3.7

import asyncio, json, logging, os, time
from uuid import uuid4
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    BotCommand, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, Message, ReplyKeyboardMarkup)
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from aiocryptopay import AioCryptoPay, Networks
import requests
from aiogram import F
from aiogram.types import Message
from aiogram.filters import CommandStart

# ── ENV & Firebase ────────────────────────────────────────────────────────
load_dotenv()
BOT_TOKEN           = os.getenv("BOT_TOKEN")
CRYPTOBOT_API_TOKEN = os.getenv("CRYPTOBOT_API_TOKEN")
assert BOT_TOKEN and CRYPTOBOT_API_TOKEN, "Токены не заданы!"

with open("serviceAccountKey.json", encoding="utf-8") as f:
    firebase_admin.initialize_app(credentials.Certificate(json.load(f)))
db = firestore.client()
logging.basicConfig(level=logging.INFO)

# NEW: инициализируем CryptoPay
crypto = AioCryptoPay(token=CRYPTOBOT_API_TOKEN, network=Networks.MAIN_NET)

# ── Мультиязычность ──────────────────────────────────────────────────────
def get_user_language(user):
    """Определяет язык пользователя"""
    lang = user.language_code if user.language_code else 'ru'
    supported = ['ru', 'en', 'fa']  # русский, английский, фарси
    return lang if lang in supported else 'ru'

# Переводы текстов
TEXTS = {
    'ru': {
        'welcome': "👋 Привет, <b>{}</b>!\n\nДобро пожаловать в <b>GenYourBot</b> — здесь ты можешь создавать персональные тесты и узнавать, насколько хорошо тебя понимают друзья.\n\n💎 Твои кристаллы: <b>{}</b>\n🪙 Твои монеты: <b>{}</b>\n\n<i>Нажми кнопку ниже, чтобы начать</i> 👇",
        'create_test': "🧪 Создать тест",
        'my_crystals': "💎 Мои кристаллы",
        'my_coins': "🪙 Мои монеты",
        'invite_friend': "🔗 Пригласить друга",
        'support': "🆘 Поддержка",
        'test_not_found': "❌ Тест не найден.",
        'already_taken': "❗ Ты уже проходил этот тест.",
        'test_ready': "🎯 Тест готов!\n\n💌 Поделись ссылкой и узнай,\nнасколько хорошо тебя знают друзья",
        'you_guessed': "🧠 Ты угадал {}%.\nВыбери:",
        'photo_prompt': "📸 Прикрепи фото или гифку, которая будет показана получателю теста.\n\nЭто может быть твое фото, аватарка или любая картинка, которая тебя характеризует. Фото будет доступно только тому, кто получит ссылку на твой тест.\n\n<b>Отправь файл обычным сообщением в этот чат.</b>",
        'photo_saved': "Фото/гифка сохранены! Теперь ответь на вопросы теста.",
        'menu_help': "👋 Используй кнопки меню или команды для навигации."
    },
    'en': {
        'welcome': "👋 Hello, <b>{}</b>!\n\nWelcome to <b>GenYourBot</b> — here you can create personal tests and find out how well your friends understand you.\n\n💎 Your crystals: <b>{}</b>\n🪙 Your coins: <b>{}</b>\n\n<i>Click the button below to start</i> 👇",
        'create_test': "🧪 Create test",
        'my_crystals': "💎 My crystals",
        'my_coins': "🪙 My coins",
        'invite_friend': "🔗 Invite friend",
        'support': "🆘 Support",
        'test_not_found': "❌ Test not found.",
        'already_taken': "❗ You have already taken this test.",
        'test_ready': "🎯 Test is ready!\n\n💌 Share the link and find out\nhow well your friends know you",
        'you_guessed': "🧠 You guessed {}%.\nChoose:",
        'photo_prompt': "📸 Attach a photo or GIF that will be shown to the test recipient.\n\nThis can be your photo, avatar or any picture that characterizes you. The photo will only be available to whoever receives the link to your test.\n\n<b>Send the file as a regular message to this chat.</b>",
        'photo_saved': "Photo/GIF saved! Now answer the test questions.",
        'menu_help': "👋 Use menu buttons or commands to navigate."
    },
    'fa': {
        'welcome': "👋 سلام، <b>{}</b>!\n\nبه <b>GenYourBot</b> خوش آمدید — اینجا می‌توانید تست‌های شخصی ایجاد کنید و بفهمید دوستانتان چقدر شما را می‌شناسند.\n\n💎 کریستال‌های شما: <b>{}</b>\n🪙 سکه‌های شما: <b>{}</b>\n\n<i>روی دکمه زیر کلیک کنید تا شروع کنید</i> 👇",
        'create_test': "🧪 ایجاد تست",
        'my_crystals': "💎 کریستال‌های من",
        'my_coins': "🪙 سکه‌های من",
        'invite_friend': "🔗 دعوت دوست",
        'support': "🆘 پشتیبانی",
        'test_not_found': "❌ تست یافت نشد.",
        'already_taken': "❗ شما قبلاً این تست را انجام داده‌اید.",
        'test_ready': "🎯 تست آماده است!\n\n💌 لینک را به اشتراک بگذارید و بفهمید\nدوستانتان چقدر شما را می‌شناسند",
        'you_guessed': "🧠 شما {}% حدس زدید.\nانتخاب کنید:",
        'photo_prompt': "📸 عکس یا گیف ضمیمه کنید که به گیرنده تست نشان داده شود.\n\nاین می‌تواند عکس شما، آواتار یا هر تصویری باشد که شما را مشخص می‌کند. عکس فقط برای کسی که لینک تست شما را دریافت می‌کند در دسترس خواهد بود.\n\n<b>فایل را به عنوان پیام معمولی به این چت ارسال کنید.</b>",
        'photo_saved': "عکس/گیف ذخیره شد! حالا به سوالات تست پاسخ دهید.",
        'menu_help': "👋 از دکمه‌های منو یا دستورات برای پیمایش استفاده کنید."
    }
}

def t(key, user, *args):
    """Возвращает текст на языке пользователя"""
    lang = get_user_language(user)
    text = TEXTS.get(lang, TEXTS['ru']).get(key, TEXTS['ru'][key])
    return text.format(*args) if args else text

# ── Клавиатуры ────────────────────────────────────────────────────────────
def create_main_menu(user):
    """Создает главное меню"""
    keyboard = [
        [KeyboardButton(text=t('create_test', user))],
        [KeyboardButton(text=t('my_crystals', user)), KeyboardButton(text=t('my_coins', user))],
        [KeyboardButton(text=t('invite_friend', user)), KeyboardButton(text=t('support', user))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ── DB Helpers ───────────────────────────────────────────────────────────
def get_user_doc(user_id):
    """Получает документ пользователя"""
    ref = db.collection('users').document(str(user_id))
    doc = ref.get()
    if not doc.exists:
        data = {'crystals': 50, 'coins': 0, 'created_at': time.time()}
        ref.set(data)
        return data
    return doc.to_dict()

def update_user_data(user_id, data):
    """Обновляет данные пользователя"""
    db.collection('users').document(str(user_id)).update(data)

# ── Bot & Dispatcher ─────────────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ── Обработчики ──────────────────────────────────────────────────────────
@dp.message(CommandStart())
async def start_handler(message: Message):
    """Обработчик команды /start"""
    user_data = get_user_doc(message.from_user.id)
    
    # Проверяем наличие deep link для прохождения теста
    if message.text and len(message.text.split()) > 1:
        test_id = message.text.split()[1]
        await take_test(message, test_id)
        return
    
    # Обычный старт
    await message.answer(
        t('welcome', message.from_user, message.from_user.first_name, 
          user_data['crystals'], user_data['coins']),
        reply_markup=create_main_menu(message.from_user)
    )

@dp.message(F.text.contains('🧪'))
async def create_test_handler(message: Message):
    """Начало создания теста"""
    await message.answer(t('photo_prompt', message.from_user))

@dp.message(F.photo | F.animation | F.video)
async def photo_handler(message: Message):
    """Обработчик фото/гифок для теста"""
    # Сохраняем файл в состоянии пользователя
    user_state = {'photo': message.photo[-1].file_id if message.photo else message.animation.file_id}
    
    # В реальном проекте лучше использовать FSM (Finite State Machine)
    # Для простоты храним в глобальном словаре
    if not hasattr(photo_handler, 'user_states'):
        photo_handler.user_states = {}
    photo_handler.user_states[message.from_user.id] = user_state
    
    await message.answer(t('photo_saved', message.from_user))

async def take_test(message: Message, test_id: str):
    """Прохождение теста по ID"""
    # Получаем тест из базы
    test_ref = db.collection('tests').document(test_id)
    test_doc = test_ref.get()
    
    if not test_doc.exists:
        await message.answer(t('test_not_found', message.from_user))
        return
    
    test_data = test_doc.to_dict()
    
    # Убираем проверку на повторное прохождение - теперь можно проходить бесконечно
    # Начинаем тест (здесь будет логика прохождения)
    await message.answer(f"🎯 Начинаем тест от {test_data.get('creator_name', 'Неизвестно')}!")

@dp.message()
async def other_messages_handler(message: Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(t('menu_help', message.from_user), 
                        reply_markup=create_main_menu(message.from_user))

# ── Основная функция ─────────────────────────────────────────────────────
async def main():
    """Основная функция запуска бота"""
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота")
    ])
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
