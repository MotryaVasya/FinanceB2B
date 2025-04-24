
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from project.bot.keyboards.reply import *
from aiogram.fsm.context import FSMContext
user_state_history = {}
user_data = {}
class TransactionStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_transaction_description = State()
    waiting_for_transaction_amount = State()
    in_transactions=State()


class CategoryStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_category_type = State()
    new_category_name= State()

    waiting_for_delete_category = State()
    waiting_for_delete_deny=State()
    in_categorie=State()

class Context(StatesGroup):
    IN_CATEGORIES = State()
    IN_TRANSACTIONS = State()

