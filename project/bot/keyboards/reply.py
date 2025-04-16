from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardBuilder
def start_keyboard():
    keyboard= ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Menu")]
        ],
        resize_keyboard=True
    )
    return keyboard
def base_key():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Статистика"), KeyboardButton(text="Категории")],
            [KeyboardButton(text="Транзакция")],
        ],
        resize_keyboard=True
    )
    return keyboard
def get_categories_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Добавить категорию"),
        KeyboardButton(text="Выбрать категорию"),
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)