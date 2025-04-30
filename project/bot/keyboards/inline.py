# project/bot/keyboards/inline.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# --- Календарь: Выбор дней ---
def get_days_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{j}", callback_data=f"day_{j}") for j in range(i, min(i + 5, 32))]
            for i in range(1, 32, 5)
        ]
    )

# --- Календарь: Выбор месяцев (для периода) ---
def get_months_inline() -> InlineKeyboardMarkup:
    months = [
        "Январь", "Февраль", "Март", "Апрель",
        "Май", "Июнь", "Июль", "Август",
        "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=months[j-1], callback_data=f"month_{j}") for j in range(i, min(i + 2, 13))]
            for i in range(1, 13, 2)
        ]
    )

# --- Календарь: Выбор годов ---
def get_years_inline() -> InlineKeyboardMarkup:
    current_year = datetime.now().year
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{year}", callback_data=f"year_{year}") for year in range(i, min(i + 3, current_year + 1))]
            for i in range(current_year - 10, current_year + 1, 3)
        ]
    )

# --- Выбор месяца для статистики за месяц ---
def month_keyboard() -> InlineKeyboardMarkup:
    months = [
        ("Январь", 1), ("Февраль", 2), ("Март", 3), ("Апрель", 4),
        ("Май", 5), ("Июнь", 6), ("Июль", 7), ("Август", 8),
        ("Сентябрь", 9), ("Октябрь", 10), ("Ноябрь", 11), ("Декабрь", 12)
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"statistic_month_{num}") for name, num in months[i:i+2]]
            for i in range(0, 12, 2)
        ]
    )
