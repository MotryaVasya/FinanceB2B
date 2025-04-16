from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
def start_keyboard():
    menuBoard= ReplyKeyboardMarkup(
        menuBoard=[
            [KeyboardButton(text="Menu")]
        ]
    )
    return menuBoard
def base_key():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Статистика"), KeyboardButton(text="Категории")],
            [KeyboardButton(text="Транзакция")],
        ],
        resize_keyboard=True
    )
    return keyboard