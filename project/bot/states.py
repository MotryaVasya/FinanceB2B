
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from project.bot.keyboards.reply import *
from aiogram.fsm.context import FSMContext
class TransactionStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_transaction_description = State()
    waiting_for_transaction_amount = State()

class CategoryStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_category_type = State()
    new_category_name= State()

class Context(StatesGroup):
    IN_CATEGORIES = State()
    IN_TRANSACTIONS = State()

async def check_states_add(state : FSMContext,message : Message):
    match state:
        case Context.IN_CATEGORIES:
            await message.answer("✏️ Введите название вашей категории:")
        case Context.IN_TRANSACTIONS:
            await message.answer("💸 Давайте создадим транзакцию! Пожалуйста, выберите категорию:",
            reply_markup=await get_all_categories())

async def check_states_update(state : FSMContext,message : Message):
    match state:
        case Context.IN_CATEGORIES:
            await message.answer(
            "🎉 Вот все ваши категории! Какую вы хотите изменить?",
            reply_markup=await make_categories_keyboard()
        )
        case Context.IN_TRANSACTIONS:
            await message.answer("💸 Давайте создадим транзакцию! Пожалуйста, выберите категорию:",
            reply_markup=await get_all_categories())

