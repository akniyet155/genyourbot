import os
import json
import logging
import asyncio
import time
from uuid import uuid4
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore
from aiocryptopay import AioCryptoPay, Networks
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, 
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    BotCommand
)
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ── ENV & Firebase ────────────────────────────────────────────────────────
load_dotenv()
BOT_TOKEN           = os.getenv("BOT_TOKEN") or "7985077405:AAGjSNrBC88HXn1zKQ9t29BNv5Ozw2FD8XQ"
CRYPTOBOT_API_TOKEN = os.getenv("CRYPTOBOT_API_TOKEN") or "433506:AAaGKgWBRpixHRXf3wKJqXecLVwDmPgMMGn"
assert BOT_TOKEN and CRYPTOBOT_API_TOKEN, "Токены не заданы!"

# Firebase инициализация
firebase_key = os.getenv("FIREBASE_KEY")
print(f"DEBUG: FIREBASE_KEY exists: {firebase_key is not None}")
print(f"DEBUG: FIREBASE_KEY length: {len(firebase_key) if firebase_key else 0}")

if firebase_key:
    try:
        # Исправляем экранирование символов в JSON
        firebase_key = firebase_key.replace('\\n', '\n').replace('\\"', '"')
        firebase_data = json.loads(firebase_key)
        
        # Используем переменную окружения
        firebase_admin.initialize_app(credentials.Certificate(firebase_data))
        print("✅ Firebase инициализован через переменную окружения")
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        print(f"❌ Первые 100 символов FIREBASE_KEY: {firebase_key[:100] if firebase_key else 'None'}")
        exit(1)
    except Exception as e:
        print(f"❌ Ошибка инициализации Firebase: {e}")
        exit(1)
else:
    # Используем файл (fallback)
    try:
        with open("serviceAccountKey.json", encoding="utf-8") as f:
            firebase_admin.initialize_app(credentials.Certificate(json.load(f)))
        print("✅ Firebase инициализован через файл")
    except FileNotFoundError:
        print("❌ ОШИБКА: Не найден файл serviceAccountKey.json и переменная FIREBASE_KEY")
        print("❌ Добавьте переменную FIREBASE_KEY в Railway Variables!")
        exit(1)
db = firestore.client()
logging.basicConfig(level=logging.INFO)

# NEW: инициализируем CryptoPay
crypto = AioCryptoPay(token=CRYPTOBOT_API_TOKEN, network=Networks.MAIN_NET)

# ── Bot / Dispatcher ───────────────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Получаем username текущего бота при старте (можно также прописать вручную)
BOT_USERNAME = None

async def set_bot_username(bot):
    global BOT_USERNAME
    me = await bot.get_me()
    BOT_USERNAME = me.username

# ── Мультиязычность ──────────────────────────────────────────────────────
def get_user_language(user_id):
    """Получает язык пользователя из базы данных"""
    try:
        user_doc = db.collection("users").document(str(user_id)).get()
        if user_doc.exists:
            return user_doc.to_dict().get("language", "ru")
        return "ru"
    except:
        return "ru"

def set_user_language(user_id, lang):
    """Устанавливает язык пользователя в базе данных"""
    db.collection("users").document(str(user_id)).update({"language": lang})

# Переводы текстов
TEXTS = {
    'ru': {
        'choose_language': "🌍 Выбери язык / Choose language / زبان را انتخاب کنید",
        'language_set': "✅ Язык установлен: Русский",
        'language_command': "🌍 Выбрать язык",
        'welcome': "👋 Привет, <b>{}</b>!\n\nДобро пожаловать в <b>GenYourBot</b> — здесь ты можешь создавать персональные тесты и узнавать, насколько хорошо тебя понимают друзья.\n\n💎 Твои кристаллы: <b>{}</b>\n🪙 Твои монеты: <b>{}</b>\n\n<i>Нажми кнопку ниже, чтобы начать</i> 👇",
        'create_test': "🧪 Создать тест",
        'my_crystals': "💎 Мои кристаллы",
        'my_coins': "🪙 Мои монеты",
        'invite_friend': "🔗 Пригласить друга",
        'support': "🆘 Поддержка",
        'test_not_found': "❌ Тест не найден.",
        'test_ready': "🎯 Тест готов!\n\n💌 Поделись ссылкой и узнай,\nнасколько хорошо тебя знают друзья",
        'you_guessed': "🧠 Ты угадал {}%.\nВыбери:",
        'photo_prompt': "📸 Прикрепи фото или гифку, которая будет показана получателю теста.\n\nЭто может быть твое фото, аватарка или любая картинка, которая тебя характеризует. Фото будет доступно только тому, кто получит ссылку на твой тест.\n\n<b>Отправь файл обычным сообщением в этот чат.</b>",
        'photo_saved': "Фото/гифка сохранены! Теперь ответь на вопросы теста.",
        'menu_help': "👋 Используй кнопки меню или команды для навигации.",
        'currencies_info': "ℹ️ Подробнее о валютах:",
        'share_link': "🔗 Поделись ссылкой:\nhttps://t.me/genyourbot?start={}",
        'support_text': "Если у тебя есть вопросы или нужна помощь — нажми кнопку ниже:",
        'support_button': "Написать в поддержку",
        'crystals_count': "💎 У тебя {} кристаллов",
        'no_coins': "🪙 Пока нет монет",
        'coins_balance': "🪙 Баланс: {} монет ≈ <b>{}$</b>",
        'withdraw_button': "💵 Вывести",
        'buy_for_dollar': "💰 Узнать за 1$",
        'buy_for_crystals': "🔍 За 100💎",
        'create_own_test': "➕ Создать свой тест",
        'forward_link': "🔗 Переслать ссылку",
        'crystals_info': "🔹 <b>Что такое кристаллы?</b>\nКристаллы — это внутренняя валюта, которую ты получаешь:\n• за приглашение друга по своей реферальной ссылке\n• когда приглашённый создаст свой первый тест\n\n💎 За одного активного друга — ты получаешь 5 кристаллов\n\nКристаллы можно использовать, чтобы:\n• узнать правильные ответы на чужие тесты (100💎)",
        'coins_info': "🪙 <b>Что такое монеты?</b>\nМонеты — это внутренняя валюта, которую ты получаешь:\n• за покупку правильных ответов твоего теста другими людьми\n• в будущем: за активность и популярность\n\n34 монеты = 0.34$\n\nВывод осуществляется через <a href='http://t.me/send?start=r-6ep9g'>CryptoBot</a> — мгновенно и без комиссии.\nМинимальная сумма вывода: 0.1 USDT.",
        'choose_action': "Выберите действие…",
        'questions': [
            {"q": "Какой тип характера меня привлекает?",
             "options": ["Спокойный", "Энергичный", "Загадочный", "Открытый", "Романтичный", "Уверенный"]},
            {"q": "Что меня больше всего привлекает в людях?",
             "options": ["Юмор", "Ум", "Внешность", "Харизма", "Доброта", "Таланты"]},
            {"q": "Где бы я предпочел(а) провести идеальный вечер?",
             "options": ["Дома у камина", "В ресторане", "На природе", "В клубе", "В кино", "Где угодно с правильным человеком"]},
            {"q": "Как я выражаю свои чувства?",
             "options": ["Словами", "Поступками", "Подарками", "Прикосновениями", "Взглядами", "По-разному"]},
            {"q": "Какой стиль общения мне ближе?",
             "options": ["Прямолинейный", "Игривый", "Глубокий", "Легкий", "Эмоциональный", "Зависит от настроения"]},
            {"q": "Что для меня важнее всего в отношениях?",
             "options": ["Доверие", "Страсть", "Понимание", "Общие интересы", "Поддержка", "Свобода"]},
            {"q": "Как я отношусь к сюрпризам?",
             "options": ["Обожаю", "Нравятся иногда", "Предпочитаю планировать", "Люблю делать сам(а)", "Безразлично", "Не люблю"]},
            {"q": "Какая музыка отражает мое настроение?",
             "options": ["Поп", "Рок", "Классика", "Джаз", "Электронная", "Разная под настроение"]},
            {"q": "Что заставляет меня улыбаться?",
             "options": ["Комплименты", "Смешные истории", "Успехи близких", "Неожиданные моменты", "Красивые виды", "Внимание"]},
            {"q": "Как я предпочитаю знакомиться?",
             "options": ["Через друзей", "Случайно", "Онлайн", "На мероприятиях", "В повседневной жизни", "Не важно как"]}
        ],
        'need_crystals': "Нужно 100 кристаллов",
        'answers_title': "🔓 Ответы:",
        'inline_share_text': "👋 Я создал(а) персональный тест про себя — хочешь проверить, насколько хорошо ты меня знаешь?\n\nВопросы про мой характер, предпочтения, стиль общения и то, что мне нравится 🎯\nИнтересно, угадаешь ли ты мои ответы?\n\n👇 Жми на ссылку, чтобы пройти — потом сравним результаты ⚡",
        'more_about_crystals': "Подробнее о кристаллах 👇",
        'more_about_coins': "Подробнее о монетах 👇",
        'balance_changed': "Баланс изменился. Попробуй снова.",
        'min_withdrawal': "Минимальная сумма вывода — 0.1 USDT",
        'coins_earned': "🪙 Тебе начислено 34 монеты за покупку ответов!",
        'pay_button': "Оплатить",
        'pay_to_view': "Для просмотра ответов оплати 1 USDT по кнопке ниже:",
        'invoice_failed': "❌ Не удалось создать счёт."
    },
    'en': {
        'choose_language': "🌍 Выбери язык / Choose language / زبان را انتخاب کنید",
        'language_set': "✅ Language set: English",
        'language_command': "🌍 Choose language",
        'welcome': "👋 Hello, <b>{}</b>!\n\nWelcome to <b>GenYourBot</b> — here you can create personal tests and find out how well your friends understand you.\n\n💎 Your crystals: <b>{}</b>\n🪙 Your coins: <b>{}</b>\n\n<i>Click the button below to start</i> 👇",
        'create_test': "🧪 Create test",
        'my_crystals': "💎 My crystals",
        'my_coins': "🪙 My coins",
        'invite_friend': "🔗 Invite friend",
        'support': "🆘 Support",
        'test_not_found': "❌ Test not found.",
        'test_ready': "🎯 Test is ready!\n\n💌 Share the link and find out\nhow well your friends know you",
        'you_guessed': "🧠 You guessed {}%.\nChoose:",
        'photo_prompt': "📸 Attach a photo or GIF that will be shown to the test recipient.\n\nThis can be your photo, avatar or any picture that characterizes you. The photo will only be available to whoever receives the link to your test.\n\n<b>Send the file as a regular message to this chat.</b>",
        'photo_saved': "Photo/GIF saved! Now answer the test questions.",
        'menu_help': "👋 Use menu buttons or commands to navigate.",
        'currencies_info': "ℹ️ More about currencies:",
        'share_link': "🔗 Share the link:\nhttps://t.me/genyourbot?start={}",
        'support_text': "If you have questions or need help — click the button below:",
        'support_button': "Contact support",
        'crystals_count': "💎 You have {} crystals",
        'no_coins': "🪙 No coins yet",
        'coins_balance': "🪙 Balance: {} coins ≈ <b>{}$</b>",
        'withdraw_button': "💵 Withdraw",
        'buy_for_dollar': "💰 Learn for 1$",
        'buy_for_crystals': "🔍 For 100💎",
        'create_own_test': "➕ Create your test",
        'forward_link': "🔗 Forward link",
        'crystals_info': "🔹 <b>What are crystals?</b>\nCrystals are an internal currency that you get:\n• for inviting a friend via your referral link\n• when the invitee creates their first test\n\n💎 For one active friend — you get 5 crystals\n\nCrystals can be used to:\n• see correct answers to other people's tests (100💎)",
        'coins_info': "🪙 <b>What are coins?</b>\nCoins are an internal currency that you get:\n• when someone buys correct answers to your test\n• in the future: for activity and popularity\n\n34 coins = 0.34$\n\nWithdrawal is done through <a href='http://t.me/send?start=r-6ep9g'>CryptoBot</a> — instantly and without commission.\nMinimum withdrawal amount: 0.1 USDT.",
        'choose_action': "Choose action…",
        'questions': [
            {"q": "What type of character attracts me?",
             "options": ["Calm", "Energetic", "Mysterious", "Open", "Romantic", "Confident"]},
            {"q": "What attracts me most in people?",
             "options": ["Humor", "Intelligence", "Appearance", "Charisma", "Kindness", "Talents"]},
            {"q": "Where would I prefer to spend a perfect evening?",
             "options": ["At home by the fireplace", "In a restaurant", "In nature", "At a club", "At the movies", "Anywhere with the right person"]},
            {"q": "How do I express my feelings?",
             "options": ["With words", "With actions", "With gifts", "With touches", "With looks", "Differently"]},
            {"q": "What communication style is closer to me?",
             "options": ["Direct", "Playful", "Deep", "Light", "Emotional", "Depends on mood"]},
            {"q": "What is most important to me in relationships?",
             "options": ["Trust", "Passion", "Understanding", "Common interests", "Support", "Freedom"]},
            {"q": "How do I feel about surprises?",
             "options": ["Love them", "Like them sometimes", "Prefer to plan", "Like to do them myself", "Indifferent", "Don't like them"]},
            {"q": "What music reflects my mood?",
             "options": ["Pop", "Rock", "Classical", "Jazz", "Electronic", "Different for different moods"]},
            {"q": "What makes me smile?",
             "options": ["Compliments", "Funny stories", "Loved ones' success", "Unexpected moments", "Beautiful views", "Attention"]},
            {"q": "How do I prefer to meet people?",
             "options": ["Through friends", "Randomly", "Online", "At events", "In everyday life", "Doesn't matter how"]}
        ],
        'need_crystals': "Need 100 crystals",
        'answers_title': "🔓 Answers:",
        'inline_share_text': "👋 I created a personal test about myself — want to check how well you know me?\n\nQuestions about my character, preferences, communication style and what I like 🎯\nWonder if you can guess my answers?\n\n👇 Click the link to take it — then we'll compare results ⚡",
        'more_about_crystals': "More about crystals 👇",
        'more_about_coins': "More about coins 👇",
        'balance_changed': "Balance has changed. Try again.",
        'min_withdrawal': "Minimum withdrawal amount — 0.1 USDT",
        'coins_earned': "🪙 You earned 34 coins for answer purchase!",
        'pay_button': "Pay",
        'pay_to_view': "To view answers pay 1 USDT using the button below:",
        'invoice_failed': "❌ Failed to create invoice."
    },
    'fa': {
        'choose_language': "🌍 Выбери язык / Choose language / زبان را انتخاب کنید",
        'language_set': "✅ زبان تنظیم شد: فارسی",
        'language_command': "🌍 انتخاب زبان",
        'welcome': "👋 سلام، <b>{}</b>!\n\nبه <b>GenYourBot</b> خوش آمدید — اینجا می‌توانید تست‌های شخصی ایجاد کنید و بفهمید دوستانتان چقدر شما را می‌شناسند.\n\n💎 کریستال‌های شما: <b>{}</b>\n🪙 سکه‌های شما: <b>{}</b>\n\n<i>روی دکمه زیر کلیک کنید تا شروع کنید</i> 👇",
        'create_test': "🧪 ایجاد تست",
        'my_crystals': "💎 کریستال‌های من",
        'my_coins': "🪙 سکه‌های من",
        'invite_friend': "🔗 دعوت دوست",
        'support': "🆘 پشتیبانی",
        'test_not_found': "❌ تست یافت نشد.",
        'test_ready': "🎯 تست آماده است!\n\n💌 لینک را به اشتراک بگذارید و بفهمید\nدوستانتان چقدر شما را می‌شناسند",
        'you_guessed': "🧠 شما {}% حدس زدید.\nانتخاب کنید:",
        'photo_prompt': "📸 عکس یا گیف ضمیمه کنید که به گیرنده تست نشان داده شود.\n\nاین می‌تواند عکس شما، آواتار یا هر تصویری باشد که شما را مشخص می‌کند. عکس فقط برای کسی که لینک تست شما را دریافت می‌کند در دسترس خواهد بود.\n\n<b>فایل را به عنوان پیام معمولی به این چت ارسال کنید.</b>",
        'photo_saved': "عکس/گیف ذخیره شد! حالا به سوالات تست پاسخ دهید.",
        'menu_help': "👋 از دکمه‌های منو یا دستورات برای پیمایش استفاده کنید.",
        'currencies_info': "ℹ️ درباره ارزها:",
        'share_link': "🔗 لینک را به اشتراک بگذارید:\nhttps://t.me/genyourbot?start={}",
        'support_text': "اگر سؤالی دارید یا به کمک نیاز دارید — روی دکمه زیر کلیک کنید:",
        'support_button': "تماس با پشتیبانی",
        'crystals_count': "💎 شما {} کریستال دارید",
        'no_coins': "🪙 هنوز سکه‌ای ندارید",
        'coins_balance': "🪙 موجودی: {} سکه ≈ <b>{}$</b>",
        'withdraw_button': "💵 برداشت",
        'buy_for_dollar': "💰 یادگیری با 1$",
        'buy_for_crystals': "🔍 با 100💎",
        'create_own_test': "➕ تست خود را بسازید",
        'forward_link': "🔗 ارسال لینک",
        'crystals_info': "🔹 <b>کریستال چیست؟</b>\nکریستال‌ها ارز داخلی هستند که دریافت می‌کنید:\n• برای دعوت دوست از طریق لینک ارجاع شما\n• وقتی دعوت‌شده اولین تست خود را بسازد\n\n💎 برای یک دوست فعال — 5 کریستال دریافت می‌کنید\n\nکریستال‌ها را می‌توان برای موارد زیر استفاده کرد:\n• دیدن پاسخ‌های صحیح تست‌های دیگران (100💎)",
        'coins_info': "🪙 <b>سکه چیست؟</b>\nسکه‌ها ارز داخلی هستند که دریافت می‌کنید:\n• وقتی کسی پاسخ‌های صحیح تست شما را بخرد\n• در آینده: برای فعالیت و محبوبیت\n\n34 سکه = 0.34$\n\nبرداشت از طریق <a href='http://t.me/send?start=r-6ep9g'>CryptoBot</a> انجام می‌شود — فوری و بدون کمیسیون.\nحداقل مبلغ برداشت: 0.1 USDT.",
        'choose_action': "عملیات را انتخاب کنید…",
        'questions': [
            {"q": "چه نوع شخصیتی مرا جذب می‌کند؟",
             "options": ["آرام", "پرانرژی", "مرموز", "باز", "رمانتیک", "مطمئن"]},
            {"q": "چه چیزی در افراد بیشتر مرا جذب می‌کند؟",
             "options": ["شوخ‌طبعی", "هوش", "ظاهر", "کاریزما", "مهربانی", "استعدادها"]},
            {"q": "کجا ترجیح می‌دهم شب کاملی را بگذرانم؟",
             "options": ["خانه کنار شومینه", "رستوران", "طبیعت", "کلوب", "سینما", "هرجا با فرد مناسب"]},
            {"q": "احساساتم را چگونه بیان می‌کنم؟",
             "options": ["با کلمات", "با اعمال", "با هدایا", "با لمس", "با نگاه", "متفاوت"]},
            {"q": "چه سبک ارتباطی به من نزدیک‌تر است؟",
             "options": ["مستقیم", "بازیگوش", "عمیق", "سبک", "احساسی", "بستگی به حال دارد"]},
            {"q": "در روابط چه چیزی برایم مهم‌تر است؟",
             "options": ["اعتماد", "شور", "درک", "علایق مشترک", "حمایت", "آزادی"]},
            {"q": "نسبت به سورپریزها چه احساسی دارم؟",
             "options": ["عاشقشان", "گاهی دوستشان دارم", "ترجیح می‌دهم برنامه‌ریزی کنم", "دوست دارم خودم بدهم", "بی‌تفاوت", "دوستشان ندارم"]},
            {"q": "چه موسیقی حالم را منعکس می‌کند؟",
             "options": ["پاپ", "راک", "کلاسیک", "جاز", "الکترونیک", "متناسب با حال"]},
            {"q": "چه چیزی مرا به لبخند وا می‌دارد؟",
             "options": ["تعریف", "داستان‌های خنده‌دار", "موفقیت عزیزان", "لحظات غیرمنتظره", "مناظر زیبا", "توجه"]},
            {"q": "چطور ترجیح می‌دهم آشنا شوم؟",
             "options": ["از طریق دوستان", "تصادفی", "آنلاین", "در رویدادها", "در زندگی روزمره", "مهم نیست چطور"]}
        ],
        'need_crystals': "نیاز به ۱۰۰ کریستال",
        'answers_title': "🔓 پاسخ‌ها:",
        'inline_share_text': "👋 تست شخصی در مورد خودم ساختم — می‌خوای ببینی چقدر منو می‌شناسی؟\n\nسوالات در مورد شخصیت، سلیقه‌ها، سبک ارتباط و چیزهایی که دوست دارم 🎯\nجالبه ببینم پاسخ‌هامو درست حدس می‌زنی؟\n\n👇 روی لینک کلیک کن تا شرکت کنی — بعد نتایج رو مقایسه می‌کنیم ⚡",
        'more_about_crystals': "بیشتر در مورد کریستال‌ها 👇",
        'more_about_coins': "بیشتر در مورد سکه‌ها 👇",
        'balance_changed': "موجودی تغییر کرده. دوباره تلاش کنید.",
        'min_withdrawal': "حداقل مبلغ برداشت — 0.1 USDT",
        'coins_earned': "🪙 برای خرید پاسخ‌ها 34 سکه دریافت کردید!",
        'pay_button': "پرداخت",
        'pay_to_view': "برای مشاهده پاسخ‌ها 1 USDT با دکمه زیر پرداخت کنید:",
        'invoice_failed': "❌ ایجاد فاکتور ناموفق بود."
    }
}

def t(key, user_id, *args):
    """Возвращает текст на языке пользователя"""
    lang = get_user_language(user_id)
    text = TEXTS.get(lang, TEXTS['ru']).get(key, TEXTS['ru'][key])
    return text.format(*args) if args else text

# ── Клавиатуры ────────────────────────────────────────────────────────────
def create_language_keyboard():
    """Создает клавиатуру выбора языка"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
            [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en")],
            [InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang:fa")]
        ]
    )

def create_main_menu(user_id):
    """Создает главное меню на языке пользователя"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t('create_test', user_id))],
            [KeyboardButton(text=t('my_crystals', user_id)),
             KeyboardButton(text=t('my_coins', user_id))],
            [KeyboardButton(text=t('invite_friend', user_id))],
            [KeyboardButton(text=t('support', user_id)),
             KeyboardButton(text=t('language_command', user_id))],
        ],
        resize_keyboard=True, is_persistent=True,
        input_field_placeholder=t('choose_action', user_id)
    )

# Инлайн-клавиатура с кнопками "?"
main_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💎 ?", callback_data="info:crystals"),
            InlineKeyboardButton(text="🪙 ?", callback_data="info:coins")
        ]
    ]
)

# ── Вопросы теста ──────────────────────────────────────────────────────────
def get_questions(user_id):
    """Получает вопросы на языке пользователя"""
    lang = get_user_language(user_id)
    return TEXTS.get(lang, TEXTS['ru'])['questions']

def answers_text(idxs: list[int], user_id: str) -> str:
    questions = get_questions(user_id)
    return "\n\n".join(
        f"<b>{questions[i]['q']}</b>\n— <i>{questions[i]['options'][a]}</i>"
        for i, a in enumerate(idxs)
    )

user_states: dict[str, dict] = {}

# ── Slash-команды ──────────────────────────────────────────────────────────
async def set_commands():
    await bot.set_my_commands([
        BotCommand(command="start",    description="Начать"),
        BotCommand(command="create",   description="Создать тест"),
        BotCommand(command="crystals", description="Мои кристаллы"),
        BotCommand(command="coins",    description="Мои монеты"),
        BotCommand(command="referral", description="Пригласить друга"),
        BotCommand(command="support",  description="Поддержка"),
        BotCommand(command="language", description="Выбрать язык"),
        # BotCommand(command="stats",    description="Статистика по тестам"),  # удалено
    ])

# ── /start ─────────────────────────────────────────────────────────────────
@dp.message(CommandStart(deep_link=True))
async def cmd_start_with_param(message: Message):
    uid = str(message.from_user.id)
    param = message.text.split(' ', 1)[1] if ' ' in message.text else ''

    # Создаем пользователя если не существует
    user_ref = db.collection("users").document(uid)
    if not user_ref.get().exists:
        user_ref.set({"crystals": 0, "coins": 0, "language": "ru"})

    if param.startswith("test_"):
        test_id = param.replace("test_", "")
        test_doc = db.collection("tests").document(test_id).get()

        if not test_doc.exists:
            await message.answer(t('test_not_found', uid))
            return

        test_data = test_doc.to_dict()
        original_bot_username = test_data.get("bot_username")

        if original_bot_username != BOT_USERNAME:
            await message.answer(
                f"❗ Этот тест был создан в боте @{original_bot_username}.\n\n"
                f"Пройти его можно только здесь:\n"
                f"https://t.me/{original_bot_username}?start=test_{test_id}"
            )
            return

        # ✅ Всё нормально, запускаем прохождение теста
        # Убираем проверку на повторное прохождение - теперь можно проходить бесконечно
        
        user_states[uid] = {
            "step": 0,
            "answers": [],
            "mode": "guess",
            "test_id": test_id,
            "original": test_data["answers"],
            "owner_id": test_data["owner_id"],
        }
        await send_question(message.chat.id, uid)
        return

    elif param.startswith("gift_"):
        gift_id = param.replace("gift_", "")
        gift_doc = db.collection("gifts").document(gift_id).get()

        if not gift_doc.exists:
            await message.answer("❌ Подарок не найден.")
            return

        gift_data = gift_doc.to_dict()
        original_bot_username = gift_data.get("bot_username")

        if original_bot_username != BOT_USERNAME:
            await message.answer(
                f"❗ Этот подарок был создан в боте @{original_bot_username}.\n\n"
                f"Открыть его можно только здесь:\n"
                f"https://t.me/{original_bot_username}?start=gift_{gift_id}"
            )
            return

        # ✅ Всё нормально, обрабатываем открытие подарка
        await message.answer("🎁 Открываем подарок...")
        # Здесь запускаем основную логику подарка
        return

    # Если параметр не распознан, показываем обычное приветствие
    await message.answer("👋 Привет! Отправь /start с тестом или подарком.")

@dp.message(Command("start"))
async def cmd_start(m: Message):
    uid = str(m.from_user.id)
    arg = (m.text.split()[1] if len(m.text.split()) > 1 else None)

    user_ref = db.collection("users").document(uid)

    # Создаем пользователя если не существует
    if not user_ref.get().exists:
        user_ref.set({"crystals": 0, "coins": 0, "language": "ru"})
        # Показываем выбор языка для новых пользователей
        await m.answer(
            t('choose_language', uid),
            reply_markup=create_language_keyboard()
        )
        return

    user_data = user_ref.get().to_dict()
    
    # Если у пользователя нет языка, показываем выбор
    if not user_data.get("language"):
        await m.answer(
            t('choose_language', uid),
            reply_markup=create_language_keyboard()
        )
        return
    
    cr = user_data.get("crystals", 0)
    coins = user_data.get("coins", 0)

    # переход по ссылке-тесту (старый формат для совместимости)
    if arg and len(arg) == 6:
        tdoc = db.collection("tests").document(arg).get()
        if tdoc.exists:
            # Убираем проверку на повторное прохождение - теперь можно проходить бесконечно
            user_states[uid] = {
                "step": 0,
                "answers": [],
                "mode": "guess",
                "test_id": arg,
                "original": tdoc.to_dict()["answers"],
                "owner_id": tdoc.to_dict()["owner_id"],
            }
            await send_question(m.chat.id, uid)
            return

    await m.answer(
        t('welcome', uid, m.from_user.first_name, cr, coins),
        reply_markup=create_main_menu(uid)
    )
    await m.answer(
        t('currencies_info', uid),
        reply_markup=main_menu_inline
    )

# ── Обработчик выбора языка ──────────────────────────────────────────────
@dp.message(Command("language"))
async def cmd_language(m: Message):
    uid = str(m.from_user.id)
    await m.answer(
        t('choose_language', uid),
        reply_markup=create_language_keyboard()
    )

@dp.callback_query(F.data.startswith("lang:"))
async def handle_language_choice(cb: CallbackQuery):
    uid = str(cb.from_user.id)
    lang = cb.data.split(":")[1]
    
    # Сохраняем выбранный язык
    set_user_language(uid, lang)
    
    await cb.answer(t('language_set', uid), show_alert=True)
    
    # Получаем данные пользователя
    user_data = db.collection("users").document(uid).get().to_dict()
    cr = user_data.get("crystals", 0)
    coins = user_data.get("coins", 0)
    
    # Удаляем сообщение с выбором языка
    try:
        await cb.message.delete()
    except:
        pass
    
    # Отправляем полноценное приветствие на выбранном языке
    await cb.message.answer(
        t('welcome', uid, cb.from_user.first_name, cr, coins),
        reply_markup=create_main_menu(uid)
    )
    await cb.message.answer(
        t('currencies_info', uid),
        reply_markup=main_menu_inline
    )

# ── Создание теста ─────────────────────────────────────────────────────────
@dp.message(Command("create"))
@dp.message(F.text.in_(["🧪 Создать тест", "🧪 Create test", "🧪 ایجاد تست"]))
async def cmd_create(m: Message):
    uid = str(m.from_user.id)
    user_states[uid] = {"mode": "author", "step": 0, "answers": [], "photo": None}
    await m.answer(
        t('photo_prompt', uid),
        parse_mode=ParseMode.HTML
    )

@dp.message(F.photo | F.animation)
async def handle_photo(m: Message):
    uid = str(m.from_user.id)
    st = user_states.get(uid)
    if not st or st.get("mode") != "author" or st.get("step") != 0 or st.get("photo"):
        return  # Не в процессе создания теста или уже есть фото

    # Сохраняем file_id фото или гифки
    if m.photo:
        file_id = m.photo[-1].file_id  # самое большое фото
        media_type = "photo"
    elif m.animation:
        file_id = m.animation.file_id
        media_type = "animation"
    else:
        return

    st["photo"] = {"file_id": file_id, "media_type": media_type}
    await m.answer(t('photo_saved', uid))
    await send_question(m.chat.id, uid)

# ── Кристаллы / Монеты / Реферал ────────────────────────────────────────────

# 🔹 Клавиатуры с кнопками "Что это?"
crystals_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💎 Что это?", callback_data="info:crystals")]
    ]
)
coins_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🪙 Что это?", callback_data="info:coins")]
    ]
)

@dp.message(Command("crystals"))
@dp.message(F.text.in_(["💎 Мои кристаллы", "💎 My crystals", "💎 کریستال‌های من"]))
async def show_crystals(m: Message):
    uid = str(m.from_user.id)
    cr = db.collection("users").document(uid).get().to_dict()["crystals"]
    await m.answer(t('crystals_count', uid, cr), reply_markup=create_main_menu(uid))

@dp.message(Command("coins"))
@dp.message(F.text.in_(["🪙 Мои монеты", "🪙 My coins", "🪙 سکه‌های من"]))
async def show_coins(m: Message):
    uid   = str(m.from_user.id)
    data  = db.collection("users").document(uid).get().to_dict()
    coins = data.get("coins", 0)
    if coins == 0:
        await m.answer(t('no_coins', uid), reply_markup=create_main_menu(uid))
        return
    amount = round(coins * 0.01, 2)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t('withdraw_button', uid), callback_data=f"withdraw:{coins}")
    ]])
    await m.answer(
        t('coins_balance', uid, coins, amount),
        reply_markup=kb, parse_mode=ParseMode.HTML
    )

@dp.callback_query(F.data.startswith("withdraw:"))
async def withdraw_coins(call: CallbackQuery):
    uid   = str(call.from_user.id)
    coins = int(call.data.split(":")[1])

    # актуальный баланс
    doc  = db.collection("users").document(uid).get().to_dict()
    if doc.get("coins", 0) < coins:
        await call.answer(t('balance_changed', uid), show_alert=True)
        return

    amount = round(coins * 0.01, 2)               # 1 монета = 0.01 USDT

    # ▸ минимальный чек 0.1 USDT
    if amount < 0.1:
        await call.answer(t('min_withdrawal', uid), show_alert=True)
        return

    try:
        # создаём чек через aiocryptopay
        check = await crypto.create_check(
            asset="USDT",
            amount=amount,
            pin_to_user_id=int(uid)
        )
        print(dir(check))  # ← добавьте эту строку
    except Exception as e:
        await call.answer(f"❌ Ошибка: {e}", show_alert=True)
        return

    # списываем монеты
    db.collection("users").document(uid).update({"coins": firestore.firestore.Increment(-coins)})

    # удаляем старое сообщение (если может)
    try:
        await call.message.delete()
    except Exception:
        pass

    # новое сообщение + главное меню (ReplyKeyboardMarkup допустим тут)
    kb_check = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💸 Получить чек", url=check.bot_check_url)]
        ]
    )
    await call.message.answer(
        f"✅ <b>Чек создан!</b>\n"
        f"Получите <b>{amount} USDT</b> по кнопке ниже:",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=kb_check
    )
    await call.answer()

@dp.message(Command("referral"))
@dp.message(F.text.in_(["🔗 Пригласить друга", "🔗 Invite friend", "🔗 دعوت دوست"]))
async def show_ref(m: Message):
    uid = str(m.from_user.id)
    await m.answer(
        t('share_link', uid, m.from_user.id),
        reply_markup=create_main_menu(uid)
    )

@dp.message(Command("support"))
@dp.message(F.text.in_(["🆘 Поддержка", "🆘 Support", "🆘 پشتیبانی"]))
async def show_support(m: Message):
    uid = str(m.from_user.id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t('support_button', uid), url="https://t.me/GenYourSupportbot")]
        ]
    )
    await m.answer(
        t('support_text', uid),
        reply_markup=kb
    )

@dp.message(F.text.in_(["🌍 Выбрать язык", "🌍 Choose language", "🌍 انتخاب زبان"]))
async def handle_language_button(m: Message):
    uid = str(m.from_user.id)
    await m.answer(
        t('choose_language', uid),
        reply_markup=create_language_keyboard()
    )

# ── Вопросы / ответы ──────────────────────────────────────────────────────
from aiogram.exceptions import TelegramBadRequest

async def send_question(chat_id: int, uid: str):
    st = user_states[uid]
    # Показ фото или гифки при старте, если есть
    if st.get("step") == 0 and st.get("mode") == "guess":
        tid = st.get("test_id")
        if tid:
            tdoc = db.collection("tests").document(tid).get()
            if tdoc.exists:
                photo = tdoc.to_dict().get("photo")
                if photo:
                    try:
                        if photo["media_type"] == "photo":
                            await bot.send_photo(chat_id, photo["file_id"])
                        elif photo["media_type"] == "animation":
                            await bot.send_animation(chat_id, photo["file_id"])
                    except TelegramBadRequest:
                        logging.warning(f"[media error] Broken file_id in test {tid}, media skipped")
    
    # Получаем вопросы на языке текущего пользователя (не создателя теста)
    q  = get_questions(uid)[st["step"]]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=o, callback_data=f"ans:{st['step']}:{i}")]
        for i, o in enumerate(q["options"])
    ])
    await bot.send_message(chat_id, f"❓ {q['q']}", reply_markup=kb)

@dp.callback_query(F.data.startswith("ans:"))
async def handle_answer(cb: CallbackQuery):
    uid = str(cb.from_user.id)
    st  = user_states.get(uid)
    if not st:
        await cb.answer(); return
    _, s_idx, opt_idx = cb.data.split(":")
    if int(s_idx) != st["step"]:
        await cb.answer(); return

    st["answers"].append(int(opt_idx))
    st["step"] += 1
    questions_count = len(get_questions(uid))
    if st["step"] >= questions_count:  # конец
        if st["mode"] == "author":
            while True:
                tid = uuid4().hex[:6]
                if not db.collection("tests").document(tid).get().exists: break
            # Сохраняем file_id и тип медиа, если есть
            bot_username = BOT_USERNAME or (await bot.get_me()).username
            test_data = {
                "owner_id": uid,
                "answers": st["answers"],
                "created_at": firestore.firestore.SERVER_TIMESTAMP,
                "bot_id": str((await bot.get_me()).id),
                "bot_username": bot_username
            }
            if st.get("photo"):
                test_data["photo"] = st["photo"]
            db.collection("tests").document(tid).set(test_data)
            await cb.message.answer(
                t('test_ready', uid) + f"\n\nhttps://t.me/{bot_username}?start=test_{tid}",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(
                            text=t('forward_link', uid),
                            switch_inline_query_current_chat=(
                                t('inline_share_text', uid) + f"\n\nhttps://t.me/{bot_username}?start=test_{tid}"
                            )
                        )]
                    ]
                )
            )
        else:  # guess
            tid = st["test_id"]; orig = st["original"]
            perc = round(sum(a == b for a, b in zip(st["answers"], orig)) / len(orig) * 100)
            db.collection("guesses").document(f"{tid}_{uid}").set({
                "guesses": st["answers"],
                "result": perc,
                "at": firestore.firestore.SERVER_TIMESTAMP,
                "bot_id": str((await bot.get_me()).id)  # ← Добавим bot_id
            })
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t('buy_for_dollar', uid), callback_data=f"see:usd:{tid}")],
                [InlineKeyboardButton(text=t('buy_for_crystals', uid), callback_data=f"see:cry:{tid}")],
                [InlineKeyboardButton(text=t('create_own_test', uid), callback_data="make_test")]
            ])
            await cb.message.answer(t('you_guessed', uid, perc), reply_markup=kb)
        del user_states[uid]
    else:
        await send_question(cb.message.chat.id, uid)
    await cb.answer()

@dp.callback_query(F.data == "make_test")
async def cb_make(cb: CallbackQuery):
    await cmd_create(cb.message); await cb.answer()

# ── Узнать ответы за 100💎 ─────────────────────────────────────────────────
@dp.callback_query(F.data.startswith("see:cry:"))
async def see_cry(cb: CallbackQuery):
    uid, tid = str(cb.from_user.id), cb.data.split(":")[2]
    uref = db.collection("users").document(uid); data = uref.get().to_dict()
    if data["crystals"] < 100:
        await cb.answer(t('need_crystals', uid), show_alert=True); return
    test_doc = db.collection("tests").document(tid).get()
    if not test_doc.exists:
        await cb.answer(t('test_not_found', uid), show_alert=True); return
    uref.update({"crystals": firestore.firestore.Increment(-100)})
    await cb.message.answer(f"{t('answers_title', uid)}\n\n{answers_text(test_doc.to_dict()['answers'], uid)}",
                            reply_markup=create_main_menu(uid))
    await cb.answer()

# ── Узнать ответы за 1 USDT ───────────────────────────────────────────────
@dp.callback_query(F.data.startswith("see:usd:"))
async def see_usd(cb: CallbackQuery):
    uid, tid = str(cb.from_user.id), cb.data.split(":")[2]
    tdoc = db.collection("tests").document(tid).get()
    if not tdoc.exists:
        await cb.answer(t('test_not_found', uid), show_alert=True); return

    owner_id = tdoc.to_dict()["owner_id"]

    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_API_TOKEN}
    payload = {"asset": "USDT", "amount": 1.00,
               "description": f"Просмотр ответов {tid}",
               "hidden_message": answers_text(tdoc.to_dict()["answers"], uid),
               "expires_in": 900}
    r = requests.post("https://pay.crypt.bot/api/createInvoice",
                      headers=headers, json=payload).json()
    if not r.get("ok"):
        await cb.message.answer(t('invoice_failed', uid), reply_markup=create_main_menu(uid))
        await cb.answer(); return

    pay_url = r["result"]["pay_url"]
    db.collection("users").document(owner_id).update({"coins": firestore.firestore.Increment(+34)})
    await bot.send_message(owner_id, t('coins_earned', owner_id))

    pay_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t('pay_button', uid), url=pay_url)]
        ]
    )
    await cb.message.answer(
        t('pay_to_view', uid),
        reply_markup=pay_kb
    )
    await cb.answer()

# Короткие тексты для всплывающих окон (до 200 символов)
@dp.callback_query(F.data == "info:crystals")
async def cb_info_crystals(cb: CallbackQuery):
    uid = str(cb.from_user.id)
    await cb.answer(t('more_about_crystals', uid), show_alert=True)
    await cb.message.answer(t('crystals_info', uid), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "info:coins")
async def cb_info_coins(cb: CallbackQuery):
    uid = str(cb.from_user.id)
    await cb.answer(t('more_about_coins', uid), show_alert=True)
    await cb.message.answer(t('coins_info', uid), parse_mode=ParseMode.HTML, disable_web_page_preview=True)

# Резюме проекта

# - **Язык и стек:** Python 3.11, aiogram 3.7, Firestore, CryptoBot API.
# - **Назначение:** Telegram-бот для создания и прохождения "пошлых" тестов с возможностью монетизации.
# - **Основные функции:**
#   - Пользователь может создать тест из 10 вопросов.
#   - Перед началом теста можно прикрепить фото или гифку, которая будет показана проходящему тест.
#   - После создания теста генерируется ссылка, которую можно переслать с сопроводительным текстом.
#   - Получатель по ссылке проходит тест, видит результат в процентах совпадения.
#   - За просмотр правильных ответов владелец теста получает монеты (внутренняя валюта).
#   - Монеты можно вывести через CryptoBot (USDT).
#   - Есть система кристаллов за приглашения и активности.
#   - Главное меню с кнопками: создать тест, мои кристаллы, мои монеты, пригласить друга, поддержка.
#   - Информация о валютах и поддержке доступна через отдельные команды и кнопки.
# - **Технические детали:**
#   - Все состояния пользователя хранятся в оперативной памяти (user_states).
#   - Данные тестов и пользователей хранятся в Firestore.
#   - Для вывода монет используется интеграция с CryptoBot.
#   - Вся логика построена на aiogram 3.x (асинхронный фреймворк для Telegram-ботов).
#   - В проекте реализована обработка медиа, inline-клавиатуры, кастомные сообщения и обработка ошибок.

# ── Запуск ────────────────────────────────────────────────────────────────
async def main():
    await set_bot_username(bot)
    await set_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await crypto.close()

@dp.message(Command("статистика"))
async def show_stats(msg: Message):
    user_id = msg.from_user.id
    username = (await bot.get_me()).username

    # Кол-во тестов от этого пользователя в этом боте
    tests_ref = db.collection("tests").where("owner_id", "==", user_id).where("bot_username", "==", username)
    test_docs = tests_ref.get()
    test_ids = [doc.id for doc in test_docs]

    # Кол-во прохождений этих тестов
    results_ref = db.collection("results").where("test_id", "in", test_ids) if test_ids else []
    results_count = len(results_ref.get()) if test_ids else 0

    await msg.answer(
        f"📊 Статистика твоего бота:\n\n"
        f"• Создано тестов: {len(test_ids)}\n"
        f"• Прошли тесты: {results_count} человек"
    )

# ── Универсальный обработчик для неопознанных сообщений ──
@dp.message()
async def handle_unhandled_messages(m: Message):
    uid = str(m.from_user.id)
    
    # Любые неопознанные сообщения
    await m.answer(
        t('menu_help', uid),
        reply_markup=create_main_menu(uid)
    )

if __name__ == "__main__":
    asyncio.run(main())