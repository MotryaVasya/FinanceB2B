from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def get_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Категории"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_categories_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Добавить категорию"),
        KeyboardButton(text="Выбрать категорию"),
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)