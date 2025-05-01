from aiogram import Router, F
import re
from aiogram.filters import or_f,StateFilter,and_f
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove
from project.bot.conecting_methods.methods import check_action
from project.bot.messages.messages import *
from aiogram.fsm.context import FSMContext
from project.bot.states import *
from project.bot.keyboards.reply import *
from project.bot.Save import save
from datetime import datetime
import calendar

from project.bot.conecting_methods.transactions import delete_transaction, get_transactions
from project.bot.messages.mesage_transaction import PAGE_SIZE, get_paginated_transactions
from project.bot.keyboards.inline_transactions import (back_menu_or_list_transactions,
                                                       build_pagination_keyboard_for_delete, build_pagination_keyboard_for_show, confirm_or_cancel_buttons)
from project.bot.messages.mesage_transaction import user_pages

router=Router()
abb=["1","2","3","4","5","6","7","8"]
abo=["1","2"]
avtobus=["","","",""]

@router.message(or_f(F.text == "Добaвить запись"))
async def add_transaction_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("show_categories.txt", "w").write(str(await save.update(user_id, "ADD_TRANSACTION")))
    try:
        await state.set_state(TransactionStates.in_add)
        await message.answer(
            reply_markup= await add_back_button(ReplyKeyboardMarkup(keyboard=[])),
            text=add_trans
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(StateFilter(TransactionStates.in_add))
async def add_after_transaction(message: Message, state: FSMContext):
    try:
        await message.answer(
            "📝 Введите описание для вашей записи (или пропустите):",
            reply_markup=await zapis_add()
        )
        await state.set_state(TransactionStates.waiting_for_transaction_description)
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")


@router.message(F.text=="Пропустить описание")
async def after_description(message: Message, state: FSMContext):
    try:
        await message.answer(
            "🎉Укажите теперь сумму вашей записи:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(TransactionStates.waiting_for_transaction_description)
async def after_name(message: Message, state: FSMContext):
    name = message.text.strip()
    user_id = message.from_user.id
    open("show_categories.txt", "w").write(str(await save.update(user_id, "SUM_DESCRIPTION")))
    try:
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
        await message.answer(
            "🎉Укажите теперь сумму вашей записи:",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")


@router.message(TransactionStates.waiting_for_transaction_amount)
async def after_amount(message: Message, state: FSMContext):
    name = message.text.strip()
    user_id = message.from_user.id
    open("show_categories.txt", "w").write(str(await save.update(user_id, "TRANSACTION_DESCRIPTION_DATA")))
    try:
        if name.isdigit():
            await state.set_state(TransactionStates.wait_date)
            await message.answer(
                "Ура! 🎉 Ты успешно добавил сумму! Теперь укажи дату 📅😊",
                reply_markup=await doty_keyboard(),
                )
        else:
            await message.answer(
                text_no,
                )
            return

    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")
        
@router.message(TransactionStates.wait_date)
async def after_date(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.waiting_for_transaction_amount)
        await message.answer(
            "🎉 Отлично! Я сохранил вашу запись😊\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")










@router.message(or_f(F.text == "Изменить запись",F.text=="Пропустить изменение категории"))
async def update_transaction_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        await state.set_state(TransactionStates.in_update_name)
        open("add_handler.txt", "w").write(str(await save.update(user_id, "ADD_TRANSACTION")))
        open("main44.txt", "w").write(str(await save.convert_to_json()))
        await message.answer(
            "🎉 Вот все ваши записи! Какую вы хотите изменить?\n"
            "1. название записи\n"
            "2. название записи\n"
            "итп\n",
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(TransactionStates.in_update_name)
async def del_after_choos1(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.in_update_cat)
        await message.answer(
            "✨ Выберите новую категорию, пожалуйста!\n\
            1. название\n\
            2. название\n\
            итп.\n",
            reply_markup= await skip_update_from_trans()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")


@router.message(TransactionStates.in_update_cat)
async def del_after_choos2(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.update_for_transaction_description)
        await message.answer(
            "📝 Введите описание для вашей записи (или пропустите):\n",
            reply_markup= await skip_update_desk_from_trans()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")


@router.message(F.text=="Пропустить описание записи")
async def del_after_choos3(message: Message, state: FSMContext):
    try:
        name = message.text.strip()
        avtobus[0]=name
        await state.set_state(TransactionStates.update_for_transaction_amount)
        await message.answer(
            "🎉Измените сумму вашей записи:\n",
            reply_markup= await skip_update_amount_from_trans()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")
@router.message(TransactionStates.update_for_transaction_description)
async def del_after_choos4(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.update_for_transaction_amount)
        await message.answer(
            "🎉Измените сумму вашей записи:\n",
            reply_markup= await skip_update_amount_from_trans()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(F.text=="Пропустить изменение суммы")
async def del_after_choos5(message: Message, state: FSMContext):
    try:
        name = message.text.strip()
        avtobus[1]=name
        await state.set_state(TransactionStates.wait_date_update)
        await message.answer(
            "Ура!Теперь измени дату 📅😊\n",
            reply_markup= await from_trans_skip_or_date()
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(TransactionStates.update_for_transaction_amount)
async def del_after_choos6(message: Message, state: FSMContext):
    name = message.text.strip()
    try:
        await state.set_state(TransactionStates.wait_date_update)
        if(name.isdigit()):
            await message.answer(
                "Ура! 🎉 Ты успешно добавил сумму! Теперь измени дату 📅😊\n",
                reply_markup= await from_trans_skip_or_date()
            )
        else:
            await message.answer(
                text_no
            )
            return
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")
@router.message(or_f(TransactionStates.wait_date_update,F.text=="Пропустить изменение даты"))
async def after_date_update(message: Message, state: FSMContext):
    name = message.text.strip()
    avtobus[2]=name
    try:
        if(avtobus[0]=="Пропустить описание записи" and avtobus[1]=="Пропустить изменение суммы" and avtobus[2]=="Пропустить изменение даты"):
            await state.set_state(TransactionStates.update_no_sets)
            await message.answer(
                "😕 Ничего не изменилось.\n Хотите вернуться и попробовать снова или оставить всё как есть?\n",
                reply_markup= await aboba_keyboard()
            )
        else:
            await state.clear()
            await message.answer(
                "🎉 Отлично! Я сохранил вашу запись😊\n"
                "🔙 Возвращаемся в главное меню!\n",
                reply_markup=await start_keyboard()
            )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(or_f(StateFilter(TransactionStates.update_no_sets),F.text == "Оставить как есть"))
async def set_type(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
            "👌 Всё оставлено как есть! Если что-то нужно будет изменить, я всегда готов помочь 😊\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
    except Exception as e:
            print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")







@router.message(F.text == 'Удалить запись')
async def delete_transaction_message(message: Message, state: FSMContext):
    await handle_delete_flow(message.from_user.id, message, state)

@router.callback_query(F.data == 'back_to_list_transactions')
async def back_to_list_callback(callback: CallbackQuery, state: FSMContext):
    await handle_delete_flow(callback.from_user.id, callback.message, state)

async def handle_delete_flow(user_id: int, message: Message, state: FSMContext):
    user_pages[user_id] = 0
    
    try:
        message_text, total_pages = await get_paginated_transactions(user_id, 0)
        keyboard = await build_pagination_keyboard_for_delete(0, total_pages, user_id)
        await message.answer('🙂 Вот список ваших записей! Какую из них хотите удалить?\n\n'+message_text,
                           reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Ошибка при получении транзакций: {e}")

@router.callback_query(F.data.startswith("transactionD_"))
async def handle_pagination_for_delete(callback: CallbackQuery, state: FSMContext):
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        all_transactions = await get_transactions(user_id)
        total_pages = (len(all_transactions) + PAGE_SIZE - 1) // PAGE_SIZE
        
        # Остальная логика пагинации...
        new_page = await check_action(
            action=action,
            total_pages=total_pages,
            current_page=current_page,
            callback=callback,
            state=state,
            for_delete=True,
            all_transactions=all_transactions,
            user_id=user_id
        )
        if new_page is None:  
            return
            
        user_pages[user_id] = new_page
        message_text, total_pages = await get_paginated_transactions(user_id, new_page)
        keyboard = await build_pagination_keyboard_for_delete(new_page, total_pages, user_id)
        
        await state.update_data(original_message=message_text)
        await callback.message.edit_text(text=message_text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        print(f"Ошибка пагинации: {e}")
        await callback.answer("Произошла ошибка, попробуйте позже")

@router.callback_query(F.data.startswith("select_transactionD_"))
async def handle_transaction_selection_for_delete(callback: CallbackQuery, state: FSMContext):
    transaction_id = int(callback.data.split('_')[2])
    transaction_name = str(callback.data.split('_')[3])
    await state.update_data(selected_transaction_id=transaction_id)
    await state.update_data(selected_transaction_name=transaction_name)

    # Получаем оригинальное сообщение
    data = await state.get_data()
    original_message = data.get('original_message', "Список транзакций")

    # Создание клавиатуры через билдер
    builder = await confirm_or_cancel_buttons()

    await callback.message.edit_text(
        text=f"{original_message}\n\n"
             f"Выбрана транзакция : '{transaction_name}'\n"
             "❗️Вы уверены, что хотите удалить эту запись?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_delete")
async def confirm_delete_transaction(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    transaction_id = data.get("selected_transaction_id")
    transaction_name = data.get("selected_transaction_name")

    if transaction_id is not None:
        res = await delete_transaction(transaction_id)
        if res:
            await callback.message.answer(
                text=f"🗑 Готово! Ваша запись успешно удалена 😊\n🔙 Возвращаемся в главное меню!",
                reply_markup=await start_keyboard()
            )
            
    else:
        await callback.message.edit_text("⚠️ Ошибка: ID транзакции не найден.")

    await callback.answer()
    await state.clear()

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_transaction(callback: CallbackQuery, state: FSMContext):
    builder = await back_menu_or_list_transactions()
    await callback.message.answer("🙂 Хотите удалить другую запись или вернуться в главное меню?",
            reply_markup=builder.as_markup())
    await state.clear()




@router.message(F.text == 'История моих записей')
async def show_transactions(message: Message):
    user_id = message.from_user.id
    user_pages[user_id] = 0  # Сбрасываем на первую страницу
    
    try:
        message_text, total_pages = await get_paginated_transactions(user_id, 0)
        keyboard = await build_pagination_keyboard_for_show(0, total_pages, user_id)
        await message.answer('📂 Вот список всех записей😊 :\n\n'+message_text, reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Ошибка при получении транзакций: {e}")

@router.callback_query(F.data.startswith("transactions_"))
async def handle_pagination_for_show(callback: CallbackQuery):
    try:
        data_parts = callback.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        current_page = user_pages.get(user_id, 0)
        all_transactions = await get_transactions(user_id)
        total_pages = (len(all_transactions) + PAGE_SIZE - 1) // PAGE_SIZE
        
        # Определяем новую страницу
        new_page = await check_action(action=action, total_pages=total_pages, current_page=current_page, callback=callback)
        
        user_pages[user_id] = new_page
        message_text, total_pages = await get_paginated_transactions(user_id, new_page)
        keyboard = await build_pagination_keyboard_for_show(new_page, total_pages, user_id)
        
        await callback.message.edit_text(message_text, reply_markup=keyboard)
        await callback.answer()
    
    except Exception as e:
        print(f"Ошибка пагинации: {e}")
        await callback.answer(f"Произошла ошибка, попробуйте позже")
