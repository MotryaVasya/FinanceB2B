from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
arr = ["Зарплата","Продукты","Кафе","Досуг","Здоровье","Транспорт","Еще"]

async def add_back_button(keyboard: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
    new_keyboard = keyboard.keyboard.copy()
    new_keyboard.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=new_keyboard, resize_keyboard=True)

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
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Статистика"), KeyboardButton(text="Категории"),KeyboardButton(text="Транзакция")],
            [KeyboardButton(text="Баланс"),KeyboardButton(text="Помощь")],
        ],
        resize_keyboard=True
    )


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
        KeyboardButton(text="Удалить"),
        KeyboardButton(text="Посмотреть список существующих"),
    )
    builder.adjust(3, 1, 1)
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)

async def skip_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Пропустить")
    )
    builder.adjust(2)
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)

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
    builder.adjust(3)
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)

async def Money_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа"""
    builder = ReplyKeyboardBuilder()
    builder.add(
            KeyboardButton(text="Перейти в меню"),
            KeyboardButton(text="Пополнить"),
        )
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard

async def Afteradd_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа"""
    builder = ReplyKeyboardBuilder()
    builder.add(
            KeyboardButton(text="Перейти к транзакциям"),
        )
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)
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

async def gety_type_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа"""
    builder = ReplyKeyboardBuilder()
    builder.add(
            KeyboardButton(text="Доход"), KeyboardButton(text="Расход"),
        )
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)
async def get_all_categories() -> ReplyKeyboardMarkup:
    """
    Создает и возвращает клавиатуру для выбора категории.
    
    Кнопки:
        - Добавить | Изменить
        - Посмотреть список существующих
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура для работы с категориями.
    """
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text=arr[0]),
        KeyboardButton(text=arr[1]),
        KeyboardButton(text=arr[2]),
        KeyboardButton(text=arr[3]),
        KeyboardButton(text=arr[4]),
        KeyboardButton(text=arr[5]),
        KeyboardButton(text=arr[6])
    )
    builder.adjust(1)  # Первые 2 кнопки в одной строке, остальные переносятся
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)
