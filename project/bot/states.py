
from aiogram.fsm.state import State, StatesGroup

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
