from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from calendar import monthrange, monthcalendar

from project.bot.handlers.statistic import get_month_name

def generate_calendar(year: int, month: int, selected_day: int = None) -> InlineKeyboardMarkup:
    """Генерирует интерактивный календарь для выбранного месяца и года."""
    builder = InlineKeyboardBuilder()
    
    # Заголовок с месяцем и годом + кнопки навигации
    month_name = get_month_name(month)
    builder.row(
        InlineKeyboardButton(text="◀", callback_data=f"calendar_prev_{year}_{month}"),
        InlineKeyboardButton(text=f"{month_name} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="▶", callback_data=f"calendar_next_{year}_{month}"),
    )
    
    # Дни недели
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    builder.row(*[InlineKeyboardButton(text=day, callback_data="ignore") for day in week_days])
    
    # Дни месяца
    month_days = monthcalendar(year, month)
    for week in month_days:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                emoji = "🔘" if day == selected_day else ""
                row.append(InlineKeyboardButton(
                    text=f"{emoji}{day}", 
                    callback_data=f"calendar_day_{year}_{month}_{day}"
                ))
        builder.row(*row)
    
    # Кнопки подтверждения/отмены
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="calendar_confirm"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="calendar_cancel"),
    )
    
    return builder.as_markup()

async def get_calendar_keyboard(date: datetime = None) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру календаря для текущего или указанного месяца."""
    if date is None:
        date = datetime.now()
    return generate_calendar(date.year, date.month)


def generate_edit_calendar(year: int, month: int, selected_day: int = None) -> InlineKeyboardMarkup:
    """Генерирует интерактивный календарь для редактирования даты."""
    builder = InlineKeyboardBuilder()
    
    # Заголовок с месяцем и годом + кнопки навигации
    month_name = get_month_name(month)
    builder.row(
        InlineKeyboardButton(text="◀", callback_data=f"edit_calendar_prev_{year}_{month}"),
        InlineKeyboardButton(text=f"{month_name} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="▶", callback_data=f"edit_calendar_next_{year}_{month}"),
    )
    
    # Дни недели
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    builder.row(*[InlineKeyboardButton(text=day, callback_data="ignore") for day in week_days])
    
    # Дни месяца
    month_days = monthcalendar(year, month)
    for week in month_days:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                emoji = "🔘" if day == selected_day else ""
                row.append(InlineKeyboardButton(
                    text=f"{emoji}{day}", 
                    callback_data=f"edit_calendar_day_{year}_{month}_{day}"
                ))
        builder.row(*row)
    
    # Кнопка "Сегодня"
    today = datetime.now()
    if today.year == year and today.month == month:
        builder.row(
            InlineKeyboardButton(text="📅 Сегодня", callback_data=f"edit_calendar_day_{today.year}_{today.month}_{today.day}"),
        )
    
    # Кнопка "Назад"
    builder.row(
        InlineKeyboardButton(text="◀ Назад", callback_data="back_to_edit_menu"),
    )
    
    return builder.as_markup()

async def get_edit_calendar_keyboard(date: datetime = None) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру календаря для текущего или указанного месяца."""
    if date is None:
        date = datetime.now()
    return generate_edit_calendar(date.year, date.month)