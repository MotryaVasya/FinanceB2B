from aiogram import Router, F
import re
from aiogram.filters import or_f,StateFilter,and_f
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove
from project.bot.messages.messages import *
from aiogram.fsm.context import FSMContext
from project.bot.states import *
from project.bot.keyboards.reply import *
from project.bot.Save import save
from datetime import datetime
import calendar
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







@router.message(or_f(F.text == "Удалить запись",F.text=="Вернутся к списку ваших записей"))
async def del_transaction_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(TransactionStates.in_del)
        await message.answer(
            "🙂 Вот список ваших записей! Какую из них хотите удалить?\n"        
            "1. боба\n"
            "2. биба\n"
            "итп.\n",
                            )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(StateFilter(TransactionStates.in_del))
async def del_after_choos(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
            "❗️Вы уверены, что хотите удалить эту запись?\n",
            reply_markup= await Del_from_trans(),
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(F.text=="Подтвердить удаление записи")
async def del_conf_choos(message: Message, state: FSMContext):
    try:
        await message.answer(
            "🗑 Готово! Ваша запись успешно удалена 😊\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard(),
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")

@router.message(F.text=="Отменить удаление записи")
async def del_conf_choos(message: Message, state: FSMContext):
    try:
        await message.answer(
            "🙂 Хотите удалить другую запись или вернуться в главное меню?\n",
            reply_markup=await cansel_del_from_trans(),
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")
@router.message(F.text=="Вернутся к меню")
async def del_conf_choose(message: Message, state: FSMContext):
    try:
        await message.answer(
            "🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊\n",
            reply_markup=await start_keyboard(),
        )
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении транзакции: {e.__class__.__name__}: {e}")
