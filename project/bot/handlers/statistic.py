# project/bot/handlers/statistic.py

from aiogram import types, Router, F
from project.bot.keyboards.reply_statistic import statistic_keyboard
from project.bot.messages.statistic_message import statistic_text_start, statistic_text_period, statistic_text_month
from project.bot.keyboards.reply import start_keyboard
from project.bot.keyboards.inline import get_days_inline, get_months_inline, get_years_inline, month_keyboard

router = Router()

# --- Обработчики текстовых сообщений ---

@router.message(F.text == "Статистика")
async def show_statistic_menu(message: types.Message):
    try:
        await message.answer(await statistic_text_start(), reply_markup=statistic_keyboard)
    except Exception as e:
        print(f"⚠ Ошибка при отображении меню статистики: {e.__class__.__name__}: {e}")
        await message.answer("Произошла ошибка при обработке статистики.")

@router.message(F.text == "За период")
async def show_period_choice(message: types.Message):
    try:
        await message.answer("Выберите дату начала:", reply_markup=get_days_inline())
    except Exception as e:
        print(f"⚠ Ошибка при отображении выбора периода: {e.__class__.__name__}: {e}")
        await message.answer("Произошла ошибка.")

@router.message(F.text == "За месяц")
async def show_month_choice(message: types.Message):
    try:
        await message.answer("Выберите месяц:", reply_markup=month_keyboard())  # тут всё ок
    except Exception as e:
        print(f"⚠ Ошибка при отображении выбора месяца: {e.__class__.__name__}: {e}")
        await message.answer("Произошла ошибка.")


@router.message(F.text == "Меню")
async def go_to_main_menu(message: types.Message):
    try:
        await message.answer("Возвращаемся в меню.", reply_markup=start_keyboard)
    except Exception as e:
        print(f"⚠ Ошибка при возврате в меню: {e.__class__.__name__}: {e}")
        await message.answer("Произошла ошибка.")

# --- Обработчики колбэков (callback_query) ---

@router.callback_query(F.data.startswith("day_"))
async def select_start_date(callback: types.CallbackQuery):
    try:
        await callback.message.answer("Выберите месяц начала:", reply_markup=get_months_inline())
        await callback.answer()
    except Exception as e:
        print(f"⚠ Ошибка при выборе дня начала: {e.__class__.__name__}: {e}")
        await callback.message.answer("Произошла ошибка.")

@router.callback_query(F.data.startswith("month_"))
async def select_start_month(callback: types.CallbackQuery):
    try:
        await callback.message.answer("Выберите год начала:", reply_markup=get_years_inline())
        await callback.answer()
    except Exception as e:
        print(f"⚠ Ошибка при выборе месяца начала: {e.__class__.__name__}: {e}")
        await callback.message.answer("Произошла ошибка.")

@router.callback_query(F.data.startswith("year_"))
async def select_start_year(callback: types.CallbackQuery):
    try:
        await callback.message.answer("Теперь выбери дату конца:", reply_markup=get_days_inline())
        await callback.answer()
    except Exception as e:
        print(f"⚠ Ошибка при выборе года начала: {e.__class__.__name__}: {e}")
        await callback.message.answer("Произошла ошибка.")

@router.callback_query(F.data.startswith("Priority"))
async def finish_period_selection(callback: types.CallbackQuery):
    try:
        await callback.message.answer(await statistic_text_period(), reply_markup=start_keyboard)
        await callback.answer()
    except Exception as e:
        print(f"⚠ Ошибка при завершении выбора периода: {e.__class__.__name__}: {e}")
        await callback.message.answer("Произошла ошибка.")

@router.callback_query(F.data.startswith("statistic_month_"))
async def show_statistic_for_month(callback: types.CallbackQuery):
    try:
        month_number = int(callback.data.split("_")[2])
        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        month_name = months[month_number - 1]
        await callback.message.answer(await statistic_text_month(month_name), reply_markup=start_keyboard)
        await callback.answer()
    except Exception as e:
        print(f"⚠ Ошибка при отображении статистики за месяц: {e.__class__.__name__}: {e}")
        await callback.message.answer("Произошла ошибка.")
