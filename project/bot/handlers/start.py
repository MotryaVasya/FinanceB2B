from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton,ReplyKeyboardRemove
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from project.bot.keyboards.reply import skip_keyboard,start_keyboard, help_keyboard, get_categories_keyboard, get_transaction_keyboard,get_all_categories,gety_type_keyboard,Money_keyboard,Afteradd_keyboard, make_save_keyboard, make_type_keyboard, make_skip_keyboard
router = Router()
user_categories = ["Еда", "Транспорт", "Развлечения", "Жильё"]
user_data = {}
waiting_for_category_name = State("waiting_for_category_name")
waiting_for_category_type = State("waiting_for_category_type")

class Context(StatesGroup):
    IN_CATEGORIES = State()
    IN_TRANSACTIONS = State()

class TransactionStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_transaction_description = State()
    waiting_for_transaction_amount = State()

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
        await state.set_state(Context.IN_CATEGORIES)
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
        await state.set_state(Context.IN_TRANSACTIONS)
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
        current_state = await state.get_state()
        
        # Если мы в процессе добавления транзакции
        if current_state == TransactionStates.waiting_for_transaction_amount:
            await state.set_state(TransactionStates.waiting_for_transaction_description)
            await message.answer("🔙 Возвращаемся к вводу описания", 
                               reply_markup=await skip_keyboard())
            return
            
        elif current_state == TransactionStates.waiting_for_transaction_description:
            await state.set_state(Context.IN_TRANSACTIONS)
            await message.answer("🔙 Возвращаемся к выбору категории",
                               reply_markup=await get_transaction_keyboard())
            return
            
        # Если мы в процессе добавления категории
        elif current_state == waiting_for_category_type:
            await state.set_state(waiting_for_category_name)
            await message.answer("🔙 Возвращаемся к вводу названия категории\n"
                               "Введите название категории:")
            return
            
        # Если мы в разделах категорий или транзакций
        elif current_state in [Context.IN_CATEGORIES, Context.IN_TRANSACTIONS]:
            await state.clear()
            await message.answer(welcome_text,
                               reply_markup=await start_keyboard())
            return
            

        else:
            await state.clear()
            await message.answer(reply_markup=await start_keyboard())
            await message.answer("Произошла ошибка, попробуйте ещё раз")
        await state.clear()
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
        await state.clear()
        await message.answer(
            "Произошла ошибка, возвращаю в главное меню",
            reply_markup=await start_keyboard()
        )

@router.message(F.text == "Добавить")
async def add_handler(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        
        if current_state == Context.IN_CATEGORIES.state:
            await message.answer("✏️ Введите название вашей категории:")
            await state.set_state(waiting_for_category_name)
            
        elif current_state == Context.IN_TRANSACTIONS.state:
            await message.answer("💸 Давайте создадим транзакцию! Пожалуйста, выберите категорию:",
                                reply_markup=await get_all_categories())
            
    except Exception as e:
        print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text)
async def handle_category_selection(message: Message, state: FSMContext):
    categories = await get_all_categories()
    category_names = [button.text for row in categories.keyboard for button in row]
    
    if message.text in category_names:
        await state.update_data(selected_category=message.text)
        keyboard = await skip_keyboard()

        await message.answer(
            "📝 Введите описание (или пропустите):",
            reply_markup=keyboard
        )
        await state.set_state(TransactionStates.waiting_for_transaction_description)
    else:
        pass

@router.message(F.text == "Пропустить", TransactionStates.waiting_for_transaction_description)
async def handle_skip_description(message: Message, state: FSMContext):
    
    await state.update_data(transaction_description=None)
    await message.answer("🎉 Укажите сумму транзакции:")
    await state.set_state(TransactionStates.waiting_for_transaction_amount)


@router.message(TransactionStates.waiting_for_transaction_description)
async def handle_description_input(message: Message, state: FSMContext):

    await state.update_data(transaction_description=message.text)
    await message.answer("🎉 Описание добавлено! Теперь укажите сумму транзакции:")
    await state.set_state(TransactionStates.waiting_for_transaction_amount)


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

