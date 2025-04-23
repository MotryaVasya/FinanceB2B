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
    """Обрабатывает нажатие кнопки "Назад", возвращая к предыдущему состоянию."""
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
                "🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊",
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
            "ADD_CATEGORY": (
                "🔙 Возвращаемся в меню категорий!",
                cattegory_text,
                await add_back_button(get_categories_keyboard())
            ),
            "EDIT_CATEGORY": (
                "🔙 Возвращаемся в меню категорий!",
                cattegory_text,
                await add_back_button(get_categories_keyboard())
            ),
            "SHOW_CATEGORIES": (
                "🔙 Возвращаемся в меню категорий!",
                cattegory_text,
                await add_back_button(get_categories_keyboard())
            ),
            "AFTER_ADD": (
                "🔙 Возвращаемся в меню категорий!",
                cattegory_text,
                await add_back_button(get_categories_keyboard())
            ),
            "EDIT_SELECT_CATEGORY": (
                "🔙 Возвращаемся в меню категорий!",
                cattegory_text,
                await add_back_button(get_all_categories())
            ),
            "ADD_TRANSACTION": (
                "🔙 Возвращаемся в меню транзакций!",
                transaction_text,
                await add_back_button(get_transaction_keyboard())
            ),
            "SKIP_TRANSACTIONS": (
                "🔙 Возвращаемся в меню транзакций!",
                transaction_text,
                await add_back_button(get_transaction_keyboard())
            ),
            "NOT_SKIP_TRANSACTIONS": (
                "🔙 Возвращаемся в меню транзакций!",
                transaction_text,
                await add_back_button(get_transaction_keyboard())
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

@router.message(F.text==("Перейти в меню"))
async def start_handler_for_help(message: Message):
    try:
        await message.answer(
            pre_help,
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")