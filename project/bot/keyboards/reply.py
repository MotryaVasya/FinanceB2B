from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
async def start_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает и возвращает основную клавиатуру меню.
    
    Кнопки:
        - Статистика | Категории
        - Транзакция | Баланс
        - Помощь
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с основными действиями.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Статистика"), KeyboardButton(text="Категории")],
            [KeyboardButton(text="Транзакция"), KeyboardButton(text="Баланс")],
            [KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard


async def get_categories_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает и возвращает клавиатуру для управления категориями.
    
    Кнопки:
        - Добавить | Изменить
        - Посмотреть список существующих
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура для работы с категориями.
    """
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Добавить"),
        KeyboardButton(text="Изменить"),
        KeyboardButton(text="Посмотреть список существующих"),
    )
    builder.adjust(2)  # Первые 2 кнопки в одной строке, остальные переносятся
    return builder.as_markup(resize_keyboard=True)


async def get_transaction_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает и возвращает клавиатуру для управления транзакциями.
    
    Кнопки:
        - Добавить | Удалить | Изменить
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура для работы с транзакциями.
    """
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Добавить"),
        KeyboardButton(text="Удалить"),
        KeyboardButton(text="Изменить"),
    )
    builder.adjust(3)  # Все 3 кнопки в одной строке
    return builder.as_markup(resize_keyboard=True)


async def help_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает и возвращает клавиатуру для раздела помощи.
    
    Кнопки:
        - Перейти в меню
    
    Returns:
        ReplyKeyboardMarkup: Простая клавиатура с возвратом в меню.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Перейти в меню")]
        ],
        resize_keyboard=True
    )
    return keyboard
