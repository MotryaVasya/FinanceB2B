from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from project.bot.states import TransactionStates,CategoryStates, Context
from aiogram.types import Message
from project.bot.messages.messages import *
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from project.bot.keyboards.reply import *
from project.bot.states import *
from project.bot.Save import save
from aiogram.types import Message, CallbackQuery
import project.bot.conecting_methods.user as user
router = Router()

@router.message(or_f(CommandStart(), Command("restart")))
async def start(message: Message, state: FSMContext):
    await start_handler(message, state, True)

@router.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await start_handler(callback.message, state, False)

async def start_handler(message: Message, state: FSMContext, is_start: bool = False):
    try:
        if is_start:
            data = {'firstname': message.from_user.first_name, 
                    'secondname': message.from_user.last_name, 
                    'tg_id': message.from_user.id,
                    'cash': 0}

            await user.create_user(data=data)
                
            await message.answer(
                welcome_text,
                reply_markup=await start_keyboard()
            )
            return
        
        await message.answer(
                '🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊',
                reply_markup=await start_keyboard()
            )
    except Exception as e:  
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Назад")
async def go_back(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data_list = await save.get(user_id)
    open("main44.txt","w").write(str(await save.convert_to_json()))
    if user_data_list and len(user_data_list) > 1:
        previous_state = user_data_list[-1]
        user_data_list.pop()
        await save.get(user_id)
        open("main.txt","w").write(previous_state)
        state_actions = {
            "MENU": (
                "да",
                await start_keyboard()
            ),
            "BALANCE": (
                "🔙 Возвращаемся в главное меню!\n\
                Попробуем добавить первую запись? 😊",
                await start_keyboard()
            ),
            "ADD_MONEY": (
                "💫 Ваш баланс: \nУ тебя всё под контролем! 🧘‍♂️\n",
                await add_back_button(await Money_keyboard())
            ),
            "MAIN_CATEGORY": (
                "🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊",
                await start_keyboard()
            ),
            "MAIN_TRANSACTIONS": (
                "🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊",
                await start_keyboard()
            ),
            "MAIN_HELP": (
                "🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊",
                await start_keyboard()
            ),
             "DELETE_CATEGORY": (
                 "🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊",
                await start_keyboard()
            ),
             "ZAGLUSHKA": (
                 "🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊",
                await start_keyboard()
            ),
            "ADD_CATEGORY": (
                cattegory_text,
                await get_categories_keyboard()
            ),
            "ADD_TRANSACTION": (
                trasaction_actions,
                await get_transaction_keyboard()
            ),
            "SHOW_TRANSACTIONS": (
                "🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊",
                await start_keyboard()
            ),
            "EDIT_CATEGORY": (
                "🎉 Вот все ваши категории! Какую вы хотите изменить?",
                await get_categories_keyboard()
            ),
            "SHOW_CATEGORIES": (    
                cattegory_text,
                await get_categories_keyboard()
            ),
            "AFTER_ADD": (
                cattegory_text,
                await add_back_button(await get_categories_keyboard())
            ),
            "EDIT_SELECT_CATEGORY": (
                cattegory_text,
                await add_back_button(await get_all_categories())
            ),
            "TRANSACTION_DESCRIPTION_DATA": (
                "🎉Укажите теперь сумму вашей записи:",
                await reset_sost(state)
            ),
            "ADD_TRANSACTION": (
                trasaction_actions,
                await get_transaction_keyboard()
            ),
            "SKIP_TRANSACTIONS": (
                trasaction_actions,
                await add_back_button(await get_transaction_keyboard())
            ),
            "NOT_SKIP_TRANSACTIONS": (
                trasaction_actions,
                await add_back_button(await get_transaction_keyboard())
            ),
            "TWO_SKIP": (
                "🔄 Хорошо! Давайте изменим тип вашей категории 😊",
                await make_type_keyboard()
            ),

            "handle_text_input": (
                f"✨ Введите новое название для категории '{user_data.get(user_id, {}).get('current_category', 'неизвестно')}' или пропустите:",
                await add_back_button(await make_skip_keyboard())
            ),
        }

        if previous_state in state_actions:
            text, reply_markup = state_actions[previous_state]
            await message.answer(text, reply_markup=reply_markup)
            await state.set_state(previous_state)
        else:
            await message.answer("Вы вернулись назад.", reply_markup=await start_keyboard())
    else:
        await message.answer("🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊", reply_markup=await start_keyboard())

async def reset_sost(state:FSMContext):
    await state.clear()
    await state.set_state(TransactionStates.waiting_for_transaction_description)

