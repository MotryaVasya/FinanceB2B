from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

statistic_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="За период")],
        [KeyboardButton(text="За месяц")],
    ],
    resize_keyboard=True
)
