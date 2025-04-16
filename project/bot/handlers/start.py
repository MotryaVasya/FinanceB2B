from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.exceptions import AiogramError
from project.bot.keyboards.reply import get_main_keyboard, get_categories_keyboard
router=Router()
@router.message(CommandStart())
async def start_handler(message: types.Message):   
    try:
        await message.answer("Здравствуйте!")
    except AiogramError as e:
        print(f"⚠ Ошибка Telegram: {e}")
    except Exception as e:
        print(f"⚠ Неожиданная ошибка: {e}")

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