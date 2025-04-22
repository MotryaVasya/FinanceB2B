from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from project.bot.states import TransactionStates,CategoryStates, Context
from aiogram.types import Message
from project.bot.messages.messages import *
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from project.bot.keyboards.reply import *
router = Router()
user_data = {}


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

@router.message(F.text==("Перейти в меню"))
async def start_handler_for_help(message: Message):
    try:
        await message.answer(
            pre_help,
            reply_markup=await start_keyboard()
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
        elif current_state == CategoryStates.waiting_for_category_type:
            await state.set_state(CategoryStates.waiting_for_category_name)
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



#TODO разделить логику на 2 метода(транзакции и категории бунтуют)
# @router.message(F.text == "Добавить")
# async def add_handler(message: Message, state: FSMContext):
#     try:
#         current_state = await state.get_state()
        
#         if current_state == Context.IN_CATEGORIES.state:
#             await message.answer("✏️ Введите название вашей категории:")
#             await state.set_state(CategoryStates.waiting_for_category_name)
            
#         elif current_state == Context.IN_TRANSACTIONS.state:
#             await message.answer("💸 Давайте создадим транзакцию! Пожалуйста, выберите категорию:",
#                                 reply_markup=await get_all_categories())
            
#     except Exception as e:
#         print(f"⚠️ Ошибка: {e.__class__.__name__}: {e}")

# @router.message(F.text)
# async def handle_category_selection(message: Message, state: FSMContext):
#     current_state = await state.get_state()
#     categories = await get_all_categories()
#     category_names = [button.text for row in categories.keyboard for button in row]
    
#     if message.text in category_names:
#         if current_state == Context.IN_CATEGORIES.state:
#             await message.answer(
#                 "📂 Вот список всех категорий! 😊",
#                 reply_markup=await get_all_categories()
#             )
#         elif current_state == Context.IN_TRANSACTIONS.state:
#             await state.update_data(selected_category=message.text)
#             keyboard = await skip_keyboard()

#             await message.answer(
#                 "📝 Введите описание (или пропустите):",
#                 reply_markup=keyboard
#             )
#             await state.set_state(TransactionStates.waiting_for_transaction_description)
#     else:
#         pass
