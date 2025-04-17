from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from project.bot.keyboards.reply import start_keyboard, help_keyboard, get_categories_keyboard, get_transaction_keyboard,get_all_categories,gety_type_keyboard
router = Router()
waiting_for_category_name = State("waiting_for_category_name")
waiting_for_category_type = State("waiting_for_category_type")
help_text=("Привет! 👋 Вот как я могу помочь:\n"
            "💸 Транзакция — добавь доход или расход.\n"
            "📂 Категории — управляй своими категориями.\n"
            "📊 Статистика — покажу аналитику твоих расходов и доходов.\n"
            "💰 Баланс — узнаешь текущий остаток средств.\n"
            "Если не знаешь с чего начать — попробуй добавить первую транзакцию! 😊\n")

welcome_text = (
            "Готово! Вы в главном меню 😊 Что хотите сделать?\n"
            "Выберите действие:\n"
            "* 💰 Проверить баланс\n"
            "* 📊 Посмотреть статистику\n"
            "* 🗂 Управлять категориями\n"
            "* 💸 Открыть список транзакций\n"
            "* ❓ Нужна помощь"
        )

pre_text=("🔙 Возвращаемся в главное меню!\n "
         "Чем займёмся дальше? 😊\n ")


def validate_name(name: str) -> bool:
    """
    Проверяет название по заданным правилам:
    1. Длина не более 50 символов
    2. Начинается с буквы или цифры
    3. Не содержит специальных символов @#$% и т.п.
    
    :param name: Название для проверки
    :return: True если название валидно, False если нет
    """
    # Проверка длины
    if len(name) > 50:
        return False
    
    # Проверка первого символа (должен быть буква или цифра)
    if not name[0].isalnum():
        return False
    
    # Проверка на допустимые символы (только буквы, цифры, пробелы и дефисы/подчёркивания)
    
    return True


@router.message(or_f(CommandStart(), Command("restart"), F.text.in_(["Перейти в меню", "Назад"])))
async def start_handler(message: Message):
    try:
        await message.answer(
            welcome_text,
            reply_markup=await start_keyboard()
        )
    except Exception as e:  
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text == "Категории")
async def categories_handler(message: Message):
    try:
        await message.answer(
            "Выберите действие:",
            reply_markup=await get_categories_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(waiting_for_category_name)
async def process_category_name(message: Message, state: FSMContext):
    try:
        category_name = message.text.strip()
        
        if not validate_name(category_name):
            await message.answer(
                "❌ Некорректное название!\n"
                "Требования:\n"
                "- Макс. 50 символов\n"
                "- Начинается с буквы/цифры\n"
                "- Без спецсимволов (@, # и др.)\n"
                "Введите снова:"
            )
            return
        
        await message.answer(f"✅ название '{category_name}' добавлено!")
        await state.set_state(waiting_for_category_type)
        await message.answer("Выберите тип",
                             reply_markup=await gety_type_keyboard()
                             )
    except Exception as e:
        await message.answer("⚠️ Произошла ошибка, попробуйте позже")
        print(f"Ошибка: {e.__class__.__name__}: {e}")

        
@router.message(or_f(F.text == "Доход",F.text == "Расход"))
async def after_add(message: Message):
    try:
        await message.answer("🎉 Отлично! Я сохранил вашу категорию 😊"
        "🔙 Возвращаемся в главное меню!",
        reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text=="Посмотреть список существующих")
async def categories_handler(message: Message):
    try:
        await message.answer(
            "📂 Вот список всех категорий! 😊",
            reply_markup= await get_all_categories()
        )
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Транзакция")
async def transaction_handler(message: Message):
    try:
        await message.answer(
            "Выберите действие с транзакциями:",
            reply_markup=await get_transaction_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text == "Помощь")
async def help_handler(message: Message):
    try:
        await message.answer(
            help_text,
            reply_markup=await help_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text==("Перейти в меню"))
async def start_handler_for_help(message: Message):
    try:
        await message.answer(
            pre_text,
            reply_markup=start_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text=="Баланс")
async def cash_handler(message: Message):
    text=(f"💫 Ваш баланс: \nУ тебя всё под контролем! 🧘‍♂️\n ")
    try:
        await message.answer(
            text,
            reply_markup=await help_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Назад")
async def back_handler(message: Message):
    try:
        prev_text = message.reply_to_message.text if message.reply_to_message else ""
        
        if "категори" in prev_text.lower():
            await categories_handler(message)
        elif "транзакци" in prev_text.lower():
            await transaction_handler(message)
        elif "помощь" in prev_text.lower():
            await help_handler(message)
        else:
            await start_handler(message)
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
        await start_handler(message)
@router.message(F.text == "Добавить")
async def categories_handler(message: Message, state: FSMContext):
    try:
        await message.answer("Введите название вашей категории:")
        await state.set_state(waiting_for_category_name)
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")

