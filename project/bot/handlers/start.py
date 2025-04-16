from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.exceptions import AiogramError
from ..keyboards.reply import start_keyboard,base_key,get_categories_keyboard
#from ..keyboards.reply import get_categories_keyboard
router=Router()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    try:
        await message.answer(
            "Здравствуйте",
        reply_markup=start_keyboard()  # Меняем клавиатуру
    )
    except AiogramError as e:
        print(f"Ошиька телеграм {e}")
    except Exception as e:
        print(f"нежданчик {e}")

@router.message(lambda message: message.text == "Menu")
async def button1_click(message: types.Message):
    try:
        await message.answer(
        "Вы перешли в раздел 1:",
        reply_markup=base_key()  # Меняем клавиатуру
        )
    except AiogramError as e:
        print(f"Ошиька телеграм {e}")
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