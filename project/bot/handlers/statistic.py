# project/bot/handlers/statistic.py

from datetime import datetime
import httpx
import logging
from aiogram import types, Router, F
from aiogram.exceptions import TelegramAPIError
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select # Импорт для реплай клавиатуры

# --- Импорты из других файлов проекта ---
from project.bot.keyboards.reply_statistic import statistic_keyboard
from project.bot.keyboards.reply import start_keyboard # Убедитесь, что этот импорт корректен
from project.bot.keyboards.inline import (
    get_days_inline,
    get_months_inline,
    get_years_inline,
    month_keyboard
)
from project.bot.messages.statistic_message import statistic_text_start
from project.core.request_conf import URL, TRANSACTIONS, FROM_MONTH, STATISTICS
from project.db.models.category import User
# -----------------------------------------

router = Router()
user_period = {}

# --- Списки названий месяцев ---
MONTH_NAMES_NOMINATIVE = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]
MONTH_NAMES_GENITIVE = [
    "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
    "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"
]

def get_month_name(month_number: int, case: str = 'nominative') -> str:
    """Возвращает название месяца по его номеру в нужном падеже."""
    if not 1 <= month_number <= 12:
        return f"Неверный месяц ({month_number})"
    # По умолчанию или если указан 'nominative' - именительный падеж
    if case == 'genitive':
        return MONTH_NAMES_GENITIVE[month_number - 1]
    return MONTH_NAMES_NOMINATIVE[month_number - 1]

# --- Новая реплай-клавиатура с кнопкой "Меню" ---
def get_menu_only_reply_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает реплай-клавиатуру с одной кнопкой 'Меню'."""
    keyboard = [
        [KeyboardButton(text="Меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, is_persistent=False)
# ---------------------------------------------


# --- Функции для взаимодействия с API ---
# (Остаются без изменений)
async def get_statistics_from_month(month: int, user_id: int) -> dict:
    """Получает статистику за указанный месяц для пользователя."""
    try:
        async with httpx.AsyncClient() as client:
            params = {'user_id': user_id}
            url = f"{URL}{TRANSACTIONS}{FROM_MONTH}{month}"
            logging.debug(f"Requesting monthly stats from URL: {url} with params: {params}")
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logging.error(f"Ошибка запроса к API (статистика за месяц): {e}")
        raise ConnectionError(f"Не удалось подключиться к API: {e}")
    except httpx.HTTPStatusError as e:
        logging.error(f"Ошибка статуса от API (статистика за месяц): {e.response.status_code} - {e.response.text}")
        api_error_detail = e.response.text
        try:
            api_error_detail = e.response.json().get("detail", api_error_detail)
        except Exception:
            pass
        raise ValueError(f"API вернул ошибку {e.response.status_code}: {api_error_detail}")
    except Exception as e:
        logging.error(f"Неожиданная ошибка при получении статистики за месяц: {e}")
        raise

async def get_statistics_from_period(data: dict) -> dict:
    """Получает статистику за указанный период для пользователя."""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{URL}{TRANSACTIONS}{STATISTICS}"
            logging.debug(f"Requesting period stats from URL: {url} with params: {data}")
            response = await client.get(url, params=data)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logging.error(f"Ошибка запроса к API (статистика за период): {e}")
        raise ConnectionError(f"Не удалось подключиться к API: {e}")
    except httpx.HTTPStatusError as e:
        logging.error(f"Ошибка статуса от API (статистика за период): {e.response.status_code} - {e.response.text}")
        api_error_detail = e.response.text
        try:
            api_error_detail = e.response.json().get("detail", api_error_detail)
        except Exception:
            pass
        raise ValueError(f"API вернул ошибку {e.response.status_code}: {api_error_detail}")
    except Exception as e:
        logging.error(f"Неожиданная ошибка при получении статистики за период: {e}")
        raise


# --- Обработчики текстовых сообщений ---
# (show_statistic_menu, show_period_choice, show_month_choice остаются без изменений)
@router.message(F.text == "Статистика")
async def show_statistic_menu(message: types.Message):
    """Отображает меню выбора типа статистики."""
    try:
        text = await statistic_text_start()
        await message.answer(text, reply_markup=statistic_keyboard) # Убедитесь, что эта клавиатура без кнопки "Меню"
    except Exception as e:
        logging.error(f"Ошибка отображения меню статистики: {e}")
        await message.answer("Произошла ошибка при показе меню статистики.")

@router.message(F.text == "За период")
async def show_period_choice(message: types.Message):
    """Начинает процесс выбора периода."""
    user_id = message.from_user.id
    user_period[user_id] = {"step": "from", "user_id": user_id}
    logging.info(f"User {user_id} started period selection.")
    await message.answer(
        "🗓️ Выберите **день начала** периода:",
        reply_markup=get_days_inline(),
        parse_mode=ParseMode.MARKDOWN
    )

@router.message(F.text == "За месяц")
async def show_month_choice(message: types.Message):
    """Предлагает выбрать месяц для статистики."""
    await message.answer(
        "🗓️ Выберите **месяц** для просмотра статистики:",
        reply_markup=month_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

# --- Этот обработчик будет срабатывать при нажатии на реплай-кнопку "Меню" ---
@router.message(F.text == "Меню")
async def go_to_main_menu(message: types.Message):
    """Возвращает пользователя в главное меню."""
    await message.answer(
        "Возвращаемся в главное меню.",
        reply_markup=await start_keyboard() # Показываем основную реплай-клавиатуру
    )
# -----------------------------------------------------------------------


# --- Обработчики inline-кнопок для периода ---
# (select_day, select_month остаются без изменений)
@router.callback_query(F.data.startswith("day_"))
async def select_day(callback: types.CallbackQuery):
    """Обрабатывает выбор дня для начала или конца периода."""
    user_id = callback.from_user.id
    if user_id not in user_period:
        await callback.message.edit_text("🤷 Пожалуйста, начните выбор периода сначала, нажав 'За период'.")
        await callback.answer("Ошибка: состояние выбора периода не найдено.", show_alert=True)
        return

    try:
        day = int(callback.data.split("day_")[1])
        step = user_period[user_id].get("step", "from")
        user_period[user_id][f"{step}_day"] = day
        logging.info(f"User {user_id} selected day {day} for step '{step}'.")

        await callback.message.edit_text(
            f"🗓️ Выбран день {('начала' if step == 'from' else 'конца')}: {day}. Теперь выберите **месяц**:",
            reply_markup=get_months_inline(),
            parse_mode=ParseMode.MARKDOWN
        )
        await callback.answer()
    except (IndexError, ValueError):
        logging.warning(f"Invalid day callback data from user {user_id}: {callback.data}")
        await callback.answer("Некорректные данные дня.", show_alert=True)
    except TelegramAPIError as e:
        logging.error(f"Telegram API error during day selection for user {user_id}: {e}")
        await callback.answer("Ошибка связи с Telegram. Попробуйте еще раз.")


@router.callback_query(F.data.startswith("month_"))
async def select_month(callback: types.CallbackQuery):
    """Обрабатывает выбор месяца для начала или конца периода."""
    user_id = callback.from_user.id
    current_step = user_period.get(user_id, {}).get("step")
    if not current_step or f"{current_step}_day" not in user_period.get(user_id, {}):
        await callback.message.edit_text("🤷 Пожалуйста, начните выбор периода с выбора дня.")
        await callback.answer("Ошибка: предыдущий шаг (выбор дня) не выполнен.", show_alert=True)
        return

    try:
        month_num = int(callback.data.split("month_")[1])
        step = user_period[user_id].get("step", "from")
        user_period[user_id][f"{step}_month"] = month_num
        logging.info(f"User {user_id} selected month {month_num} for step '{step}'.")

        month_name = get_month_name(month_num) # Именительный падеж по умолчанию

        await callback.message.edit_text(
            f"🗓️ Выбран месяц {('начала' if step == 'from' else 'конца')}: **{month_name}**. Теперь выберите **год**:",
            reply_markup=get_years_inline(),
            parse_mode=ParseMode.MARKDOWN
        )
        await callback.answer()
    except (IndexError, ValueError):
        logging.warning(f"Invalid month callback data from user {user_id}: {callback.data}")
        await callback.answer("Некорректные данные месяца.", show_alert=True)
    except TelegramAPIError as e:
        logging.error(f"Telegram API error during month selection for user {user_id}: {e}")
        await callback.answer("Ошибка связи с Telegram. Попробуйте еще раз.")


@router.callback_query(F.data.startswith("year_"))
async def select_year(callback: types.CallbackQuery):
    """Обрабатывает выбор года и либо переходит к выбору конца периода, либо показывает статистику."""
    user_id = callback.from_user.id
    current_step = user_period.get(user_id, {}).get("step")
    if not current_step or f"{current_step}_month" not in user_period.get(user_id, {}):
        await callback.message.edit_text("🤷 Пожалуйста, начните выбор периода с выбора дня и месяца.")
        await callback.answer("Ошибка: предыдущий шаг (выбор месяца) не выполнен.", show_alert=True)
        return

    try:
        year = int(callback.data.split("year_")[1])
        step = user_period[user_id].get("step", "from")
        user_period[user_id][f"{step}_year"] = year
        logging.info(f"User {user_id} selected year {year} for step '{step}'.")

        if step == "from":
            user_period[user_id]["step"] = "to"
            from_month_name = get_month_name(user_period[user_id]['from_month'], case='genitive')
            await callback.message.edit_text(
                f"🗓️ Дата начала: **{user_period[user_id]['from_day']:02d} {from_month_name} {user_period[user_id]['from_year']} г.**\n"
                f"Теперь выберите **день конца** периода:",
                reply_markup=get_days_inline(),
                parse_mode=ParseMode.MARKDOWN
            )
            await callback.answer() # Отвечаем на колбэк после успешного обновления сообщения
        else: # step == "to"
            d = user_period[user_id]
            try:
                from_dt = datetime(d["from_year"], d["from_month"], d["from_day"]).date()
                to_dt = datetime(d["to_year"], d["to_month"], d["to_day"]).date()

                if from_dt > to_dt:
                    await callback.message.edit_text(
                        "⚠️ Ошибка: Дата начала периода не может быть позже даты окончания.\nПожалуйста, выберите период заново.",
                        reply_markup=None # Удаляем инлайн-кнопки
                    )
                    del user_period[user_id]
                    await callback.answer("Некорректный период.", show_alert=True)
                    return

                from_date_iso = from_dt.isoformat()
                to_date_iso = to_dt.isoformat()
                

                data = {"user_id": user_id, "from_date": from_date_iso, "to_date": to_date_iso}
                logging.info(f"Requesting stats for user {user_id} for period {from_date_iso} to {to_date_iso}")

                stats = await get_statistics_from_period(data)

                # --- Динамическое формирование текста (как раньше) ---
                income_data = stats.get('income', {})
                expense_data = stats.get('expense', {})
                income = income_data.get('sum', 0) if isinstance(income_data, dict) else income_data
                expense = expense_data.get('sum', 0) if isinstance(expense_data, dict) else expense_data

                top_categories = stats.get('top_categories', [])
                from_dt_str = from_dt.strftime('%d.%m.%Y')
                to_dt_str = to_dt.strftime('%d.%m.%Y')

                text = (
                    f"📊 Статистика за период {from_dt_str} – {to_dt_str}:\n\n"
                    f"📈 Доходы: {income} ₽\n"
                    f"📉 Расходы: {expense} ₽\n\n"
                    f"🔥 Топ-3 категорий расходов:"
                )
                if top_categories:
                    text += "\n"
                    for idx, item in enumerate(top_categories, 1):
                        category_name = item.get('category', 'Не указана')
                        amount = item.get('amount', 0)
                        text += f"{idx}) {category_name} — **{amount}** ₽\n"
                        if idx >= 3: break
                    for i in range(len(top_categories) + 1, 4):
                        text += f"{i}) — —\n"
                else:
                    text += " нет данных\n"
                # ---------------------------------------------------

                # Сначала редактируем сообщение, чтобы убрать инлайн кнопки выбора года
                await callback.message.answer(text, reply_markup=get_menu_only_reply_keyboard())
                await callback.answer("Статистика сформирована.") # Отвечаем на колбэк
                logging.info(f"Successfully displayed period stats for user {user_id} and cleared state.")
                del user_period[user_id] # Очищаем состояние после успешного получения статистики

  

            except (KeyError, ValueError) as e:
                logging.error(f"Data or API response error for period stats user {user_id}: {e}. Current state: {user_period.get(user_id)}")
                error_message = f"🤷 Произошла ошибка при обработке данных: {e}. Пожалуйста, попробуйте выбрать период заново."
                if isinstance(e, ValueError) and "API вернул ошибку" in str(e):
                    error_message = f"😥 Не удалось получить статистику: {e}"
                await callback.message.edit_text(error_message, reply_markup=None) # Удаляем инлайн-кнопки
                if user_id in user_period: del user_period[user_id] # Очищаем состояние
                await callback.answer("Ошибка данных.", show_alert=True)
            except ConnectionError as e:
                logging.error(f"API connection error getting period stats for user {user_id}: {e}")
                await callback.message.edit_text(f"Не удалось подключиться к серверу статистики: {e}. Попробуйте позже.", reply_markup=None) # Удаляем инлайн-кнопки
                if user_id in user_period: del user_period[user_id] # Очищаем состояние
                await callback.answer("Ошибка соединения.", show_alert=True)
            except Exception as e:
                logging.exception(f"Unexpected error during period stats processing for user {user_id}: {e}")
                await callback.message.edit_text("Произошла непредвиденная ошибка при формировании статистики. 😥", reply_markup=None) # Удаляем инлайн-кнопки
                if user_id in user_period: del user_period[user_id] # Очищаем состояние
                await callback.answer("Внутренняя ошибка.", show_alert=True)

    except (IndexError, ValueError):
        logging.warning(f"Invalid year callback data from user {user_id}: {callback.data}")
        await callback.answer("Некорректные данные года.", show_alert=True)
    except TelegramAPIError as e:
        logging.error(f"Telegram API error during year selection/processing for user {user_id}: {e}")
        await callback.answer("Ошибка связи с Telegram. Попробуйте еще раз.")
    except Exception as e:
        logging.exception(f"Critical error in select_year for user {user_id}: {e}")
        await callback.answer("Критическая ошибка обработчика.", show_alert=True)
        try:
            await callback.message.edit_text("Произошла серьезная ошибка при обработке вашего запроса. 😥", reply_markup=None) # Удаляем инлайн-кнопки
            if user_id in user_period: del user_period[user_id] # Очищаем состояние пользователя
        except Exception as inner_e:
            logging.error(f"Failed to send recovery message to user {user_id}: {inner_e}")


# --- Обработчик статистики за месяц (Inline кнопка) ---
@router.callback_query(F.data.startswith("statistic_month_"))
async def show_statistic_for_month(callback: types.CallbackQuery):
    """Показывает статистику за выбранный месяц."""
    user_id = callback.from_user.id
    try:
        month_num_str = callback.data.split("statistic_month_")[1]
        month_num = int(month_num_str)

        if not 1 <= month_num <= 12:
            raise ValueError(f"Invalid month number: {month_num}")

        logging.info(f"User {user_id} requested stats for month {month_num}.")

        stats = await get_statistics_from_month(month_num, user_id)

        # --- Динамическое формирование текста (как раньше) ---
        month_name = get_month_name(month_num) # Именительный падеж по умолчанию
        income_data = stats.get('income', {})
        expense_data = stats.get('expense', {})
        income = income_data.get('sum', 0) if isinstance(income_data, dict) else income_data
        expense = expense_data.get('sum', 0) if isinstance(expense_data, dict) else expense_data
        top_categories = stats.get("top_categories", [])

        text = f"📊 Статистика за {month_name}:\n\n" # Именительный падеж
        text += f"📈 Доходы: {income} ₽\n" \
                f"📉 Расходы: {expense} ₽\n\n" \
                f"🔥 Топ-3 категорий расходов:"

        if top_categories:
            text += "\n"
            for idx, item in enumerate(top_categories, 1):
                category_name = item.get("category", "Не указана")
                amount = item.get("amount", 0)
                text += f"{idx}) {category_name} — **{amount}** ₽\n"
                if idx >= 3: break
            for i in range(len(top_categories) + 1, 4):
                text += f"{i}) — —\n"
        else:
            text += " нет данных\n"
        # ---------------------------------------------------

        # Сначала редактируем сообщение, чтобы убрать инлайн кнопки выбора месяца
        await callback.message.answer(text, reply_markup=get_menu_only_reply_keyboard())
        logging.info(f"Successfully displayed monthly stats for user {user_id}.")
        await callback.answer("Статистика сформирована.") # Отвечаем на колбэк


    except (IndexError, ValueError) as e:
        logging.warning(f"Invalid data or API response error for user {user_id}: {callback.data} - {e}")
        error_message = f"Некорректные данные для месяца ({e})."
        if isinstance(e, ValueError) and "API вернул ошибку" in str(e):
            error_message = f"😥 Не удалось получить статистику: {e}"
        await callback.answer(error_message, show_alert=True)
        try:
            await callback.message.edit_text(f"Ошибка: {error_message}", reply_markup=None) # Удаляем инлайн-кнопки
        except TelegramAPIError: pass
    except ConnectionError as e:
        logging.error(f"API connection error getting monthly stats for user {user_id}: {e}")
        await callback.answer(f"Ошибка соединения с сервером: {e}", show_alert=True)
        try:
            await callback.message.edit_text(f"Не удалось подключиться к серверу статистики: {e}. Попробуйте позже.", reply_markup=None) # Удаляем инлайн-кнопки
        except TelegramAPIError: pass
    except TelegramAPIError as e:
        logging.error(f"Telegram API error during monthly stats display for user {user_id}: {e}")
        await callback.answer("Ошибка связи с Telegram. Попробуйте еще раз.")
    except Exception as e:
        logging.exception(f"Unexpected error during monthly stats processing for user {user_id}: {e}")
        await callback.answer("Внутренняя ошибка сервера.", show_alert=True)
        try:
            await callback.message.edit_text("Произошла непредвиденная ошибка. 😥", reply_markup=None) # Удаляем инлайн-кнопки
        except TelegramAPIError: pass

# --- Обработчик инлайн-кнопки "Меню", который был в прошлом варианте, удален,
# --- т.к. теперь используется обычная реплай-кнопка, обрабатываемая F.text == "Меню"