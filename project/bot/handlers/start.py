from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.exceptions import AiogramError
from project.bot.keyboards.reply import start_keyboard, help_keyboard, get_categories_keyboard, get_transaction_keyboard
cash=4
router = Router()
welcome_text = (
            "Готово! Вы в главном меню 😊 Что хотите сделать?\n"
            "Выберите действие:\n"
            "* 💰 Проверить баланс\n"
            "* 📊 Посмотреть статистику\n"
            "* 🗂 Управлять категориями\n"
            "* 💸 Открыть список транзакций\n"
            "* ❓ Нужна помощь"
        )
pre_text=("🔙 Возвращаемся в главное меню!\n "
         "Чем займёмся дальше? 😊\n ")
@router.message(CommandStart())
@router.message(Command("restart"))
async def start_handler(message: types.Message):
    try:
        await message.answer(
                welcome_text,
            reply_markup=start_keyboard()
        )
    except AiogramError as e:
        print(f"Ошибка телеграм {e}")
    except Exception as e:
        print(f"нежданчик {e}")
@router.message(F.text == "Категории")
async def categories_handler(message: types.Message):
    try:
        await message.answer(
            "Выберите действие:",
            reply_markup=get_categories_keyboard()
        )
    except AiogramError as e:
        print(f"⚠ Ошибка Telegram: {e}")
    except Exception as e:
        print(f"⚠ Неожиданная ошибка: {e}")      
@router.message(F.text == "Транзакция")
async def transaction_handler(message: types.Message):
    try:
        await message.answer(
            "Выберите действие с транзакциями:",
            reply_markup=get_transaction_keyboard()
        )
    except AiogramError as e:
        print(f"⚠ Ошибка Telegram: {e}")
    except Exception as e:
        print(f"⚠ Неожиданная ошибка: {e}")
@router.message(F.text=="Помощь")
async def help_handler(message: types.Message):
    try:
        mess=("Привет! 👋 Вот как я могу помочь:\n"
            "💸 Транзакция — добавь доход или расход.\n"
            "📂 Категории — управляй своими категориями.\n"
            "📊 Статистика — покажу аналитику твоих расходов и доходов.\n"
            "💰 Баланс — узнаешь текущий остаток средств.\n"
            "Если не знаешь с чего начать — попробуй добавить первую транзакцию! 😊\n")
        await message.answer(
            mess,reply_markup=help_keyboard()
        )
    except AiogramError as e:
        print(f"⚠ Ошибка Telegram: {e}")
    except Exception as e:
        print(f"⚠ Неожиданная ошибка: {e}")
@router.message(F.text==("Перейти в меню"))
async def start_handler_for_help(message: types.Message):
    try:
        await message.answer(
            pre_text,
            reply_markup=start_keyboard()
        )
    except AiogramError as e:
        print(f"Ошибка телеграм {e}")
    except Exception as e:
        print(f"нежданчик {e}")
@router.message(F.text=="Баланс")
async def cash_handler(message: types.Message):
    text=(f"💫 Ваш баланс: {cash}\nУ тебя всё под контролем! 🧘‍♂️\n ")
    try:
        await message.answer(
            text,
            reply_markup=help_keyboard()
        )
    except AiogramError as e:
        print(f"Ошибка телеграм {e}")
    except Exception as e:
        print(f"нежданчик {e}")