from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
arr = ["Зарплата","Продукты","Кафе","Досуг","Здоровье","Транспорт","Еще"]
user_categories = ["Еда", "Транспорт", "Развлечения", "Жильё"]
async def add_back_button(keyboard: ReplyKeyboardMarkup):
    buttons = [row[:] for row in keyboard.keyboard]
    buttons.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

async def make_edit_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Изменить"))
    return builder.as_markup(resize_keyboard=True)


async def make_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")]],
        resize_keyboard=True
    )


async def make_type_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Доход"),
        KeyboardButton(text="Расход"),
    )
    builder.add(KeyboardButton(text="Пропустить"))
    builder.adjust(3, 1)  # 3 кнопки в первом ряду, 1 во втором
    return builder.as_markup(resize_keyboard=True)


async def make_save_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Сохранить изменения")]],
        resize_keyboard=True
    )

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
            [KeyboardButton(text="Статистика"), KeyboardButton(text="Категории"),KeyboardButton(text="Мои записи")],
            [KeyboardButton(text="Баланс"),KeyboardButton(text="Помощь")],
        ],
        resize_keyboard=True
    )

async def make_categories_keyboard():
    builder = ReplyKeyboardBuilder()
    for category in user_categories:
        builder.add(KeyboardButton(text=category))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
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
            KeyboardButton(text="Пeрейти в меню"),
            KeyboardButton(text="Пополнить"),
        )
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard

async def Afteradd_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа"""
    builder = ReplyKeyboardBuilder()
    builder.add(
            KeyboardButton(text="Перейти к моим записям"),
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
