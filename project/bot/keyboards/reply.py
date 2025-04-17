from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
def start_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Статистика"), KeyboardButton(text="Категории")],
            [KeyboardButton(text="Транзакция"), KeyboardButton(text="Баланс")],[KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard
def get_categories_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Добавить"),
        KeyboardButton(text="Изменить"),
        KeyboardButton(text="Посмотреть список существующих"),
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_transaction_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Добавить"),
        KeyboardButton(text="Удалить"),
        KeyboardButton(text="Изменить"),
    )
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)
def help_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Перейти в меню")]
        ],
        resize_keyboard=True
    )
    return keyboard