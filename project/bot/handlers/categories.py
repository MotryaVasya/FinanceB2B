from aiogram import Router, types, F
from aiogram.types import Message
from project.bot.states import *
from project.bot.Save import save
from project.bot.messages.messages import *
from aiogram.types import KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f,StateFilter,and_f
from project.bot.keyboards.reply import *
from project.bot.Save import save
def validate_name(name: str) -> bool:
    """
    Проверяет название по заданным правилам:
    1. Длина не более 50 символов
    2. Начинается с буквы или цифры
    3. Не содержит специальных символов @#$% и т.п.
    4. Не состоит только из цифр (должна быть хотя бы одна буква)
    
    :param name: Название для проверки
    :return: True если название валидно, False если нет
    """
    if len(name) == 0 or len(name) > 50:
        return False
    
    if not name[0].isalnum():
        return False
    
    for char in name:
        if not (char.isalnum() or char in (' ', '-', '_')): 
            return False
    
    if all(char.isdigit() for char in name if char.isalnum()):
        return False
    
    if not any(char.isalpha() for char in name):
        return False
    
    return True



router = Router()

@router.message(or_f(F.text== "Удалить",F.text=="Вернутся к списку категорий"))
async def skip_name(message: types.Message, state: FSMContext):
    await state.set_state(CategoryStates.waiting_for_delete_category)
    try:
        await message.answer(
            "🙂 Вот список ваших категорий! Какую из них хотите удалить?\n",
            reply_markup=await delete_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")


@router.message(or_f(StateFilter(CategoryStates.waiting_for_delete_category),F.text=="Нaзад"))
async def delete_categories(message: Message, state: FSMContext):
    try:
        await message.answer(
            "❗️Вы уверены, что хотите удалить эту категорию?\n",
            reply_markup=await delete_keyboard_affter()
        )
        await state.clear()
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text=="Потвердить")
async def delete_categories(message: Message, state: FSMContext):
    try:
        await message.answer(
            "🗑 Готово! Категория успешно удалена\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
        await state.set_state(CategoryStates.waiting_for_delete_deny)
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
@router.message(or_f(F.text=="Отмена",CategoryStates.waiting_for_delete_deny))
async def delete_den(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
        "🙂 Хотите удалить другую категорию или вернуться в главное меню?",
        reply_markup=await deny_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
@router.message(F.text=="Перейти к меню")
async def delete_menu(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
        "🔙 Возвращаемся в главное меню! Чем займёмся дальше? 😊",
        reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Посмотреть список существующих")
async def show_categories_list(message: Message):
    user_id = message.from_user.id
    open("show_categories.txt", "w").write(str(await save.update(user_id, "SHOW_CATEGORIES")))
    if user_id not in user_state_history:
        user_state_history[user_id] = []
    user_state_history[user_id].append("show_categories_list")
    try:
        await message.answer(
            "📂 Вот список всех категорий! 😊",
            reply_markup=await get_all_categories()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text=="Еще")
async def show_temp_categories_list(message: Message):
    user_id = message.from_user.id
    open("show_categories.txt", "w").write(str(await save.update(user_id, "SHOW_CATEGORIES")))
    if user_id not in user_state_history:
        user_state_history[user_id] = []
    user_state_history[user_id].append("show_categories_list")
    try:
        await message.answer(
            "📂 Вот список личных категорий! 😊",
            reply_markup=await temporary_all_categories()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
        
@router.message(F.text == "Добавить")
async def add_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("main44.txt", "w").write(str(await save.update(user_id, "ADD_CATEGORY")))
    await state.set_state(CategoryStates.waiting_for_category_name)
    await message.answer("✏️ Введите название вашей категории:")

@router.message(CategoryStates.waiting_for_category_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if not validate_name(name):
        await message.answer(
            """😕 Похоже, что-то не так с названием. Попробуйте ещё раз, пожалуйста.\n
 Вот несколько простых правил:\n
1. Название не должно быть слишком длинным — максимум 50 символов.\n
2. Оно должно начинаться с буквы или цифры (без специальных символов и пробелов).\n
3. Не используйте символы типа @, #, $, % и т.п.\n
"""
        )
        return
    
    await state.update_data(category_name=name)
    await message.answer(
        "🎉 Готово! Ваша категория добавлена. Пожалуйста, выберите тип:",
        reply_markup= await gety_type_keyboard()
    )
    await state.set_state(CategoryStates.waiting_for_category_type)

@router.message(or_f(F.text == "Доход", F.text == "Расход"))
async def after_add(message: Message):
    user_id = message.from_user.id
    open("main44.txt", "w").write(str(await save.update(user_id, "AFTER_ADD")))
    try:
        await message.answer(
            "🎉 Отлично! Я сохранил вашу категорию 😊\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
    except Exception as e:
        print(f"Ошибка: {e.__class__.__name__}: {e}")




@router.message(F.text == "Изменить")
async def show_categories(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    open("main44.txt", "w").write(str(await save.update(user_id, "EDIT_CATEGORY")))
    try:
            current_state = await state.get_state()
            if current_state == Context.IN_CATEGORIES:
                await message.answer(
            "🎉 Вот все ваши категории! Какую вы хотите изменить?",
            reply_markup=await make_categories_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text.in_(user_categories))
async def select_category(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    open("select_category.txt", "w").write(str(await save.update(user_id, "EDIT_SELECT_CATEGORY")))
    try:    
        user_data[user_id] = {"current_category": message.text}
        await message.answer(
            f"✨ Введите новое название для категории '{message.text}' или пропустите:",
            reply_markup=await make_skip_keyboard()
        )
        await state.set_state(CategoryStates.new_category_name)
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Пропустить")
async def skip_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not user_data.get(user_id):
        return await message.answer("Ошибка: категория не выбрана")
    try:
        await state.clear()
        await message.answer(
            "🔄 Хорошо! Давайте изменим тип вашей категории 😊",
            reply_markup=await make_type_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
        
@router.message(StateFilter(CategoryStates.new_category_name))
async def handle_text_input(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_data and "current_category" in user_data[user_id]:
        old_name = user_data[user_id]["current_category"]
        user_data[user_id]["current_category"]=message.text
        try:
            await state.clear()
            await message.answer(
                "🎉 Ура! Название категории успешно изменено!\n"
                "Теперь давайте изменим тип категории. Пожалуйста, выберите новый тип 😊\n",
                reply_markup=await make_type_keyboard()
            )
        except Exception as e:
            print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text.in_(["Доход", "Расход","Прoпустить"]))
async def set_type(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        user_data[user_id]["type"] = message.text.lower()
    try:
        await message.answer(
            "✨ Всё супер! Сохраняем изменения? 😊",
            reply_markup=await make_save_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")


@router.message(F.text == "Сохранить изменения")
async def save_changes(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        try:
            await message.answer(
                "🎉 Отлично! Я изменил вашу категорию!\n"
                "🔙 Возвращаемся в главное меню!\n",
                reply_markup=await start_keyboard()
            )
            user_data.pop(user_id)
        except Exception as e:
            print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
    else:
        await message.answer(
            "😕 Ничего не изменилось. Хотите вернуться и попробовать снова или оставить всё как есть?\n",
            reply_markup=aboba_keyboard()
        )
@router.message(F.text == "Оставить как есть")
async def set_type(message: types.Message):
    try:
        await message.answer(
            "👌 Всё оставлено как есть! Если что-то нужно будет изменить, я всегда готов помочь 😊\n"
            "🔙 Возвращаемся в главное меню!\n",
            reply_markup=await start_keyboard()
        )
    except Exception as e:
            print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
@router.message(StateFilter(CategoryStates.waiting_for_category_name))
async def process_category_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        category_name = message.text.strip()
        if not validate_name(category_name):
            await message.answer(
                "😕 Похоже, что-то не так с названием. Попробуйте ещё раз, пожалуйста.\n"
                "Вот несколько простых правил:\n"
                "1. Название не должно быть слишком длинным — максимум 50 символов.\n"
                "2. Оно должно начинаться с буквы или цифры.\n"
                "3. Не используйте специальные символы.\n"
            )
            return
        
        await state.set_state(CategoryStates.waiting_for_category_type)
        await save.update(user_id, "PROCESS_CATEGORY_TYPE")
        await message.answer(
            text=f"🎉 Готово! Ваша категория '{category_name}' добавлена.\nПожалуйста, выберите тип:\n",
            reply_markup=await gety_type_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text=="Статистика")
async def zaglushka(message:types.Message):
    user_id = message.from_user.id
    try:
        open("add_handler.txt", "w").write(str(await save.update(user_id, "ZAGLUSHKA")))
        await message.answer("В СКОРЫХ ОБНОВЛЕНИЯХ❗️🔜")
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

