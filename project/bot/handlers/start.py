from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from project.bot.keyboards.reply import skip_keyboard,start_keyboard, help_keyboard, get_categories_keyboard, get_transaction_keyboard,get_all_categories,gety_type_keyboard,Money_keyboard,Afteradd_keyboard
router = Router()
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
                "❌ Некорректное название!\n"
                "Требования:\n"
                "- Макс. 50 символов\n"
                "- Начинается с буквы/цифры\n"
                "- Без спецсимволов (@, # и др.)\n"
                "Введите снова:"
            )
            return
        
        await message.answer(f"🎉 Готово! Ваша категория '{category_name}' добавлена.")
        
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
            
        # Во всех остальных случаях возвращаем в главное меню
        else:
            await state.clear()
            await message.answer(pre_text,
                               reply_markup=await start_keyboard())
            
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
        await message.answer("Произошла ошибка, попробуйте ещё раз")
        await state.clear()


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