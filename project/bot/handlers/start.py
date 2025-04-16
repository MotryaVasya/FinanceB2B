from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.exceptions import AiogramError
from project.bot.keyboards.reply import start_keyboard, base_key, get_categories_keyboard, get_transaction_keyboard

router = Router()

@router.message(CommandStart())
@router.message(Command("restart"))
async def start_handler(message: types.Message):
    try:
        welcome_text = (
            "Готово! Вы в главном меню 😊 Что хотите сделать?\n"
            "Выберите действие:\n"
            "* 💰 Проверить баланс\n"
            "* 📊 Посмотреть статистику\n"
            "* 🗂 Управлять категориями\n"
            "* 💸 Открыть список транзакций\n"
            "* ❓ Нужна помощь"
        )
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