from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.filters import or_f
from project.bot.keyboards.reply import start_keyboard, help_keyboard, get_categories_keyboard, get_transaction_keyboard
router = Router()
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