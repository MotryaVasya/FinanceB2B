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

router = Router()

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
        await message.answer("Некуда возвращаться.", reply_markup=await start_keyboard())

    
@router.message(or_f(CommandStart(), Command("restart")))
async def start_handler(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        open("menu.txt","w").write(str(await save.update(user_id, "MENU")))
        open("main44.txt","w").write(str(await save.convert_to_json()))
        await message.answer(
            welcome_text,
            reply_markup=await start_keyboard()
        )
    except Exception as e:  
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")


async def reset_sost(state:FSMContext):
    await state.clear()
    await state.set_state(TransactionStates.waiting_for_transaction_description)