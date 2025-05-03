from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from calendar import monthrange, monthcalendar

from project.bot.handlers.statistic import get_month_name

def generate_calendar(year: int, month: int, selected_day: int = None, prefix: str = "calendar_") -> InlineKeyboardMarkup:
    """Генерирует интерактивный календарь для выбранного месяца и года."""
    builder = InlineKeyboardBuilder()

    # Заголовок с месяцем и годом + кнопки навигации
    month_name = get_month_name(month)
    builder.row(
        InlineKeyboardButton(text="◀", callback_data=f"{prefix}prev_{year}_{month}"), # Используем prefix
        InlineKeyboardButton(text=f"{month_name} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="▶", callback_data=f"{prefix}next_{year}_{month}"), # Используем prefix
    )

    # Дни недели (callback_data="ignore", prefix не нужен)
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
                    callback_data=f"{prefix}day_{year}_{month}_{day}" # Используем prefix
                ))
        builder.row(*row)

    # Кнопки подтверждения/отмены
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"{prefix}confirm"), # Используем prefix
        InlineKeyboardButton(text="❌ Отмена", callback_data=f"{prefix}cancel"),    # Используем prefix
    )

    return builder.as_markup()


async def get_calendar_keyboard(date: datetime = None, prefix: str = "calendar_") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру календаря для текущего или указанного месяца."""
    if date is None:
        date = datetime.now()
    return generate_calendar(date.year, date.month, prefix=prefix)