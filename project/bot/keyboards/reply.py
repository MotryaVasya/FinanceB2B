from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder,InlineKeyboardBuilder
from datetime import datetime
import calendar
arr = [
    {"name": "Зарплата", "type": "Доход"},
    {"name": "Продукты", "type": "Расход"},
    {"name": "Кафе", "type": "Расход"},
    {"name": "Досуг", "type": "Расход"},
    {"name": "Здоровье", "type": "Расход"},
    {"name": "Транспорт", "type": "Расход"},
]
arr_transactions=[]
user_categories = [
    {"name": "Еда", "type": "Расход"},
    {"name": "Транспорт", "type": "Расход"},
    {"name": "Развлечения", "type": "Расход"},
    {"name": "Жильё", "type": "Расход"},
    {"name": "Зарплата", "type": "Доход"},
]
months = list(calendar.month_name)[1:]
async def doty_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for name in months:
        builder.add(KeyboardButton(text=name),
        )
    builder.adjust(2)
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)

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
        keyboard=[[KeyboardButton(text="Пропустить название")]],
        resize_keyboard=True
    )

async def make_type_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Доход"),
        KeyboardButton(text="Расход"),
        KeyboardButton(text="Пропустить тип")
    )
    builder.adjust(2, 1)
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
        button_text = f"{category['name']} ({category['type']})"
        builder.button(text=button_text)
    builder.adjust(2)
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)

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
        KeyboardButton(text="Добавить категорию"),
        KeyboardButton(text="Изменить категорию"),
        KeyboardButton(text="Удалить категорию"),
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
        KeyboardButton(text="Добaвить запись"),
        KeyboardButton(text="Изменить запись"),
        KeyboardButton(text="Удалить запись"),
        KeyboardButton(text="История моих записей")
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
            KeyboardButton(text="Перейти к моим записям"),
            KeyboardButton(text="Вернутся к балансу")
        )
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard

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

async def create_user_categories_inline_keyboard(user_categories: list) -> InlineKeyboardMarkup:
    """
    Создает Inline клавиатуру со списком пользовательских категорий
    и кнопкой "Назад".
    
    Args:
        user_categories: Список словарей вида [{"name": "Категория", "type": "Тип"}, ...]
    """
    builder = InlineKeyboardBuilder()
    
    if not user_categories:
        builder.add(InlineKeyboardButton(
            text="Нет категорий",
            callback_data="no_categories"
        ))
    else:
        for category in user_categories:
            button_text = f"{category['name']} ({category['type']})"
            builder.add(InlineKeyboardButton(
                text=button_text,
                callback_data=f"user_cat:{category['name']}"
            ))
    
    builder.adjust(1)
    
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_category_options"
    ))
    
    return builder.as_markup()

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

    for category in arr:
        builder.add(
            KeyboardButton(text=f"{category['name']} ({category['type']})")
        )
    builder.add( KeyboardButton(text="Еще"))
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)

async def delete_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа"""
    builder = ReplyKeyboardBuilder()
    for category in user_categories:
        builder.add(
                KeyboardButton(text=f"{category['name']} ({category['type']})")
            )
        KeyboardButton(text="Назад")
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    return await add_back_button(keyboard)

async def trans_all() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа"""
    builder = ReplyKeyboardBuilder()
    for category in user_categories:
        builder.add(
                KeyboardButton(text=f"{category['name']} ({category['type']})")
            )
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard

async def zapis_add() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Назад"),
        KeyboardButton(text="Пропустить описание"),
    )
    builder.adjust(2)
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard

async def delete_keyboard_affter() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа"""
    builder = ReplyKeyboardBuilder()
    builder.add(
            KeyboardButton(text="Подтвердить удаление категории"),
            KeyboardButton(text="Отменить удаление категории")
        )
    
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard

async def deny_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа"""
    builder = ReplyKeyboardBuilder()
    builder.add(
            KeyboardButton(text="Вернутся к списку категорий"),
            KeyboardButton(text="В меню"),
        )
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard

async def aboba_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа"""
    builder = ReplyKeyboardBuilder()
    builder.add(
            KeyboardButton(text="Оставить как есть"),
        )
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard

async def None_keyboard() -> ReplyKeyboardMarkup:
    builder=ReplyKeyboardBuilder()
    builder.add()