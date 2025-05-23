
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from project.bot.keyboards.reply import *
from aiogram.fsm.context import FSMContext
user_state_history = {}
user_data = {}
class TransactionStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_transaction_description = State()
    waiting_for_transaction_amount = State()
    in_transactions=State()
    wait_date=State()
    wait_date_update=State()
    in_del=State()
    in_add=State()
    in_update=State()
    in_update_name=State()
    in_update_cat=State()
    update_for_transaction_description = State()
    update_for_transaction_amount=State()
    update_no_sets=State()

class UpdateTransactionForm(StatesGroup):
    select_transaction = State()
    edit_field = State()
    select_category = State()
    new_value = State()
    confirmation = State()
    enter_page_number = State()

class CategoryStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_category_type = State()
    waiting_for_save_confirmation = State()
    new_category_name= State()
    first= State()
    second= State()

    waiting_for_delete_category = State()
    waiting_for_delete_deny=State()
    in_categorie=State()

class Context(StatesGroup):
    IN_CATEGORIES = State()
    IN_TRANSACTIONS = State()
    popa=State()
    biba=State()
