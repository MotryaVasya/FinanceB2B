from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from project.bot.states import TransactionStates,CategoryStates, Context
from aiogram.types import Message
from project.bot.messages.messages import *
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from project.bot.keyboards.reply import *
from project.bot.states import *
import logging
router = Router()


@router.message(F.text == "Назад")
async def go_back(message: Message, state: FSMContext):
    """Обрабатывает нажатие кнопки "Назад", возвращая к предыдущему состоянию."""
    user_id = message.from_user.id
    if user_id in user_state_history and len(user_state_history[user_id]) > 1:
        previous_state = user_state_history[user_id][-1]
        logging.info(f"Предыдущее состояние после pop: {previous_state}")

        state_actions = {
            "MENU": (
                "Вы вернулись в главное меню.",
                await start_keyboard()
            ),
            "BALANCE": (
                "Вы вернулись в раздел 'Баланс'.",
                await Money_keyboard()
            ),
            "ADD_MONEY": (
                "Вы вернулись в раздел 'Баланс'.",
                await Money_keyboard()
            ),
            "TRANSACTIONS_MAIN": (
                "Вы вернулись в раздел 'Транзакции'.",
                await get_transaction_keyboard()
            ),
            "ADD_TRANSACTION": (
                "Вы вернулись в раздел 'Транзакции'.",
                await get_transaction_keyboard()
            ),
            CategoryStates.waiting_for_category_name.state: (
                "Введите название категории:",
                await add_back_button(ReplyKeyboardMarkup(keyboard=[[]], resize_keyboard=True))
            ),
            CategoryStates.waiting_for_category_type.state: (
                "Выберите тип категории:",
                await add_back_button(await gety_type_keyboard())
            ),
            TransactionStates.waiting_for_category_name.state: (
                "Выберите категорию транзакции:",
                await add_back_button(await get_all_categories())
            ),
            Context.IN_CATEGORIES.state: (
                "Действия с категориями:",
                await add_back_button(await get_categories_keyboard())
            ),
            Context.IN_TRANSACTIONS.state: (
                "Действия с транзакциями:",
                await add_back_button(await get_transaction_keyboard())
            ),
            "handle_text_input": (
                f"✨ Введите новое название для категории '{user_data.get(user_id, {}).get('current_category', 'неизвестно')}' или пропустите:",
                await add_back_button(await make_skip_keyboard())
            ),
            "skip_name": (
                "🔄 Хорошо! Давайте изменим тип вашей категории 😊",
                await add_back_button(await make_type_keyboard())
            ),
            "set_type": (
                "✨ Всё супер! Сохраняем изменения? 😊",
                await add_back_button(await make_save_keyboard())
            ),
            "skip_type": (
                "✨ Всё супер! Сохраняем изменения? 😊",
                await add_back_button(await make_save_keyboard())
            ),
            "show_categories": (
                "🎉 Вот все ваши категории! Какую вы хотите изменить?",
                await add_back_button(await make_categories_keyboard())
            ),
            "select_category": (
                "🎉 Вот все ваши категории! Какую вы хотите изменить?",
                await add_back_button(await make_categories_keyboard())
            ),
            "show_categories_list": (
                "📂 Вот список всех категорий! 😊",
                await add_back_button(await get_all_categories())
            ),
        }

        if previous_state in state_actions:
            text, reply_markup = state_actions[previous_state]
            await message.answer(text, reply_markup=reply_markup)
        else:
            await message.answer("Вы вернулись назад.", reply_markup=await start_keyboard())
    else:
        await message.answer("Некуда возвращаться.", reply_markup=await start_keyboard())
    user_state_history.pop(user_id)
@router.message(or_f(CommandStart(), Command("restart")))
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
