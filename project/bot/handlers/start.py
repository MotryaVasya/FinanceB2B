from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton,ReplyKeyboardRemove
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from project.bot.keyboards.reply import start_keyboard, help_keyboard, get_categories_keyboard, get_transaction_keyboard,get_all_categories,gety_type_keyboard,Money_keyboard,Afteradd_keyboard, make_save_keyboard, make_type_keyboard, make_skip_keyboard
router = Router()
user_categories = ["Еда", "Транспорт", "Развлечения", "Жильё"]
user_data = {}
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
cattegory_text =(
            "📂 Что вы хотите сделать с категориями?  Выберите действие:\n"
"* ➕ Добавить категорию\n"
"* 📝 Изменить категорию\n"
"* ❌ Удалить категорию\n"
"* 👀 Посмотреть существующие категории\n"
)
pre_help=("🔙 Возвращаемся в главное меню!\n"
"Попробуем добавить первую транзакцию? 😊\n")
pre_balance=("🔙 Возвращаемся в главное меню!\n"
"Чем займёмся дальше? 😊\n")

def validate_name(name: str) -> bool:
    """
    Проверяет название по заданным правилам:
    1. Длина не более 50 символов
    2. Начинается с буквы или цифры
    3. Не содержит специальных символов @#$% и т.п.
    4. Не состоит только из цифр (должна быть хотя бы одна буква)
    
    :param name: Название для проверки
    :return: True если название валидно, False если нет
    """
    # Проверка длины
    if len(name) == 0 or len(name) > 50:
        return False
    
    # Проверка первого символа (должен быть буква или цифра)
    if not name[0].isalnum():
        return False
    
    # Проверка на допустимые символы (только буквы, цифры, пробелы и дефисы/подчёркивания)
    for char in name:
        if not (char.isalnum() or char in (' ', '-', '_')):
            return False
    
    # Проверка, что название не состоит только из цифр
    if all(char.isdigit() for char in name if char.isalnum()):
        return False
    
    # Проверка, что есть хотя бы одна буква (включая случаи с пробелами/разделителями)
    if not any(char.isalpha() for char in name):
        return False
    
    return True


@router.message(or_f(CommandStart(), Command("restart"), F.text.in_(["Назад"])))
async def start_handler(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
            welcome_text,
            reply_markup=await start_keyboard()
        )
    except Exception as e:  
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text == "Категории")
async def categories_handler(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
            cattegory_text,
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
                "😕 Похоже, что-то не так с названием. Попробуйте ещё раз, пожалуйста.\n"
                "Вот несколько простых правил:\n"
                "1. Название не должно быть слишком длинным — максимум 50 символов.\n"
                "2. Оно должно начинаться с буквы или цифры (без специальных символов и пробелов).\n"
                "3. Не используйте символы типа @, #, $, % и т.п.\n"
            )
            return
        
        await message.answer(f"🎉 Готово! Ваша категория '{category_name}' добавлена.\n Пожалуйста, выберите тип:\n")
        
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

@router.message(or_f(F.text == "Транзакция",F.text=="Перейти к транзакциям"))
async def transaction_handler(message: Message, state: FSMContext):
    try:
        await state.clear()
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
            pre_help,
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
@router.message(F.text==("Пeрейти в меню"))
async def start_handler_for_help(message: Message):
    try:
        await message.answer(
            pre_balance,
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text=="Баланс")
async def cash_handler(message: Message):
    text=(f"💫 Ваш баланс: \nУ тебя всё под контролем! 🧘‍♂️\n ")
    try:
        await message.answer(
            text,
            reply_markup=await Money_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
@router.message(F.text=="Пополнить")
async def  Add_money_handler(message: Message):
    text=(f"💰 Хотите пополнить баланс?\n 🏦 Перейдите в раздел Транзакции для пополнения! 💳📈\n ")
    try:
        await message.answer(
            text,
            reply_markup=await Afteradd_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
@router.message(F.text == "Назад")
async def back_handler(message: Message, state: FSMContext):
    try:
        await state.clear()
        
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
        await state.clear()
        await start_handler(message)


@router.message(F.text == "Добавить")
async def categories_handler(message: Message, state: FSMContext):
    try:
        await message.answer("✏️Введите название вашей категории:")
        await state.set_state(waiting_for_category_name)
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")





async def make_categories_keyboard():
    builder = ReplyKeyboardBuilder()
    for category in user_categories:
        builder.add(KeyboardButton(text=category))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)



@router.message(F.text == "Изменить")
async def show_categories(message: types.Message):
    try:
        await message.answer(
            "🎉 Вот все ваши категории! Какую вы хотите изменить?",
            reply_markup= await make_categories_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text.in_(user_categories))
async def select_category(message: types.Message):
    try:    
        user_data[message.from_user.id] = {"current_category": message.text}
        await message.answer(
            f"✨ Введите новое название для категории '{message.text}' или пропустите:",
            reply_markup= await make_skip_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Пропустить")
async def skip_name(message: types.Message):
    if not user_data.get(message.from_user.id):
        return await message.answer("Ошибка: категория не выбрана")
    try:
        await message.answer(
            "🔄 Хорошо! Давайте изменим тип вашей категории 😊",
            reply_markup= await make_type_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}") 

@router.message(F.text.in_(["Доход", "Расход"]))
async def set_type(message: types.Message):
    if message.from_user.id in user_data:
        user_data[message.from_user.id]["type"] = message.text.lower()
    try:
        await message.answer(
            "✨ Всё супер! Сохраняем изменения? 😊",
            reply_markup= await make_save_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}") 

@router.message(F.text == "Назад")
async def go_back(message: types.Message):
    await show_categories(message)

@router.message(F.text == "Пропустить")
async def skip_type(message: types.Message):
    try:
        await message.answer(
            "✨ Всё супер! Сохраняем изменения? 😊",
            reply_markup= await make_save_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}") 

@router.message(F.text == "Сохранить изменения")
async def save_changes(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        # Здесь сохраняем изменения в БД
        category = user_data[user_id].get("current_category")
        new_type = user_data[user_id].get("type", "не изменён")
        try:
            await message.answer(
                f"🎉 Отлично! Категория '{category}' изменена!\n"
                f"Тип: {new_type}\n\n"
                "🔙 Возвращаемся в главное меню!",
                reply_markup=ReplyKeyboardRemove()
            )
        except Exception as e:
            print(f"⚠ Ошибка: {e.__class__.__name__}: {e}") 
        user_data.pop(user_id)
    else:
        await message.answer("Нечего сохранять", reply_markup=ReplyKeyboardRemove())

# Для обработки текстового ввода нового названия
@router.message()
async def handle_text_input(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and "current_category" in user_data[user_id]:
        old_name = user_data[user_id]["current_category"]
        user_data[user_id]["new_name"] = message.text
        try:
            await message.answer(
                f"Вы изменили название с '{old_name}' на '{message.text}'\n"
                "Теперь укажите тип категории:",
                reply_markup= await make_type_keyboard()
            )
        except Exception as e:
            print(f"⚠ Ошибка: {e.__class__.__name__}: {e}") 