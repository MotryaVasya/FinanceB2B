from aiogram import Router, types, F
from aiogram.types import Message
from project.bot.states import *
import re
from project.bot.Save import save
from project.bot.messages.messages import *
from aiogram.types import KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f,StateFilter,and_f
from project.bot.keyboards.reply import *
from project.bot.Save import save, save_user_data

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

@router.callback_query(F.data.startswith("user_cat:"))
async def process_user_category_callback(callback_query: types.CallbackQuery):
    """
    Обрабатывает нажатие на кнопку с пользовательской категорией.
    """
    category_name = callback_query.data.split(":", 1)[1]
    user_id = callback_query.from_user.id

    try:
        await callback_query.answer(f"Вы выбрали категорию: {category_name}")
        await callback_query.message.edit_text(
            f"📂 Список личных категорий.\nВы выбрали: *{category_name}*",
            parse_mode="Markdown",
            reply_markup=callback_query.message.reply_markup
        )
    except Exception as e:
        print(f"⚠ Ошибка в process_user_category_callback: {e.__class__.__name__}: {e}")
        await callback_query.answer("Произошла ошибка при обработке выбора.", show_alert=True)

@router.callback_query(F.data == "back_to_category_options")
async def process_back_to_category_options(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие кнопки "Назад" из inline-клавиатуры категорий.
    Возвращает пользователя в главное меню.
    """
    try:
        await callback_query.answer("Возвращаемся...")
        await callback_query.message.delete()
        await callback_query.message.answer(
            "🔙 Возвращаемся в главное меню!\nЧем займёмся дальше? 😊",
            reply_markup=await get_categories_keyboard()
        )
        await state.clear()
    except Exception as e:
        print(f"⚠ Ошибка в process_back_to_main_menu: {e.__class__.__name__}: {e}")
        await callback_query.answer("Не удалось вернуться в меню.", show_alert=True)

@router.message(or_f(F.text== "Удалить категорию",F.text=="Вернутся к списку категорий"))
async def skip_name(message: types.Message, state: FSMContext):
    await state.set_state(CategoryStates.waiting_for_delete_category)
    try:
        user_id = message.from_user.id
        open("show_categories.txt", "w").write(str(await save.update(user_id, "DELETE_CATEGORY")))
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

@router.message(F.text=="Подтвердить удаление категории")
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

@router.message(F.text=="Пeрейти в меню")
async def delete_menu(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer(
        "🔙 Возвращаемся в главное меню!\n"
        "Чем займёмся дальше? 😊",
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
    try:
        current_user_categories = user_categories
        if not current_user_categories:
             await message.answer("У вас пока нет личных категорий.")
             return
        await message.answer(
            "📂 Вот список ваших личных категорий! 😊\n"
            "(Нажмите на категорию для выбора - действие пока не задано)",
            reply_markup=await create_user_categories_inline_keyboard(current_user_categories)
        )
    except Exception as e:
        print(f"⚠ Ошибка в show_temp_categories_list: {e.__class__.__name__}: {e}")
        await message.answer("Не удалось отобразить список категорий.")

@router.message(F.text == "Добавить категорию")
async def add_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id

    open("main44.txt", "w").write(str(await save.update(user_id, "ADD_CATEGORY")))
    await state.set_state(CategoryStates.waiting_for_category_name)
    await message.answer(
            "✏️ Введите название вашей категории:",
            reply_markup= await add_back_button(ReplyKeyboardMarkup(keyboard=[]))
    )

@router.message(CategoryStates.waiting_for_category_name)
async def process_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.text.strip()
    if not validate_name(name):
        await message.answer(
            """😕 Похоже, что-то не так с названием. Попробуйте ещё раз, пожалуйста.\n
�Вот несколько простых правил:\n
1. Название не должно быть слишком длинным — максимум 50 символов.\n
2. Оно должно начинаться с буквы или цифры (без специальных символов и пробелов).\n
3. Не используйте символы типа @, #, $, % и т.п.\n
"""
        )
        return
    
    await save_user_data.update_dict(user_id, {'category_name': name})
    await message.answer(
        "🎉 Готово! Ваша категория добавлена. Пожалуйста, выберите тип:",
        reply_markup= await gety_type_keyboard()
    )
    await state.set_state(CategoryStates.waiting_for_category_type)

@router.message(CategoryStates.waiting_for_category_type, F.text.in_(["Доход", "Расход"]))
async def set_type(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("select_category.txt", "w").write(str(await save.update(user_id, "DOHOD")))
    category_type = message.text.lower() 
    user_data = await save_user_data.find_element_by_user_id(user_id)
    if user_data is None or 'category_name' not in user_data:
        await message.answer("😕 Ошибка: не найдено имя категории. Пожалуйста, начните сначала (/start или 'Добавить категорию').")
        await state.clear()
        return       
    await save_user_data.update_dict(user_id, {"type": category_type})

    try:
        await state.set_state(CategoryStates.waiting_for_save_confirmation)
        await message.answer(
            "✨ Всё супер! Сохраняем изменения? 😊",
            reply_markup=await make_save_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка при отправке подтверждения: {e.__class__.__name__}: {e}")
        await message.answer("Произошла ошибка при подготовке к сохранению.")
        await state.clear()

@router.message(F.text == "Изменить категорию")
async def show_categories(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    open("main44.txt", "w").write(str(await save.update(user_id, "EDIT_CATEGORY")))
    try:
        await message.answer(
            "🎉 Вот все ваши категории! Какую вы хотите изменить?",
            reply_markup=await make_categories_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text.in_([f"{cat['name']} ({cat['type']})" for cat in user_categories]))
async def select_category(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    open("select_category.txt", "w").write(str(await save.update(user_id, "EDIT_SELECT_CATEGORY")))
    
    try:
        category_name = message.text.split(' (')[0]
        
        user_data[user_id] = {"current_category": category_name}
        await message.answer(
            f"✨ Введите новое название для категории '{category_name}' или пропустите:",
            reply_markup=await make_skip_keyboard()
        )
        await state.set_state(CategoryStates.new_category_name)
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Пропустить название")
async def skip_name(message: types.Message, state: FSMContext):
    
    user_id = message.from_user.id
    open("select_category.txt", "w").write(str(await save.update(user_id, "EDIT_SELECT_CATEGORY_TYPE")))
    if not user_data.get(user_id):
        return await message.answer("Ошибка: категория не выбрана")
    try:
        await state.clear()
        await state.set_state(CategoryStates.first)
        await message.answer(
            "🔄 Хорошо! Давайте изменим тип вашей категории 😊",
            reply_markup= await make_type_keyboard()
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


@router.message(F.text.in_(["Доход", "Расход"]))
async def set_type(message: types.Message):
    user_id = message.from_user.id
    open("select_category.txt", "w").write(str(await save.update(user_id, "DOHOD")))
    if user_data[user_id]["type"] is None:
        user_data[user_id]["type"] = message.text.lower()
    try:
        await message.answer(
            "✨ Всё супер! Сохраняем изменения? 😊",
            reply_markup=await make_save_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text=="Пропустить тип")
async def set_type(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    current_state = await state.get_state()
    
    if current_state == CategoryStates.first.state:
        await state.set_state(CategoryStates.second)
        await message.answer(
            "😕 Ничего не изменилось.\n Хотите вернуться и попробовать снова или оставить всё как есть?\n",
            reply_markup=await add_back_button(await aboba_keyboard())
        )
        open("select_category.txt", "w").write(str(await save.update(user_id, "TWO_SKIP")))
        return
    
    try:
        if user_data.get(user_id).get("type") is not None:
            await message.answer(
                "✨ Всё супер! Сохраняем изменения? 😊",
                reply_markup=await make_save_keyboard()
            )
            await state.clear()
        else:
            await message.answer(
                "Ну ладно, не хотите как хотите!😕\n 🔙 Возвращаемся в главное меню!",
                reply_markup=await start_keyboard()
            )
            await state.clear()
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(CategoryStates.waiting_for_save_confirmation, F.text == "Сохранить изменения")
async def save_changes(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_info = await save_user_data.find_element_by_user_id(user_id)

    if user_info is None or 'category_name' not in user_info or 'type' not in user_info:
        await message.answer(
            "😕 Ошибка: не найдены данные для сохранения. Пожалуйста, начните процесс добавления сначала.",
             reply_markup=await start_keyboard()
             )
        await state.clear()
        return

    try:
        category_name = user_info['category_name']
        category_type = user_info['type']
        user_id = user_info[user_id]
        
        print(f"Сохранена категория: {category_name} ({category_type}) для {user_id}. Временные ключи не удалены.")

        await message.answer(
                f"🎉 Отлично! Категория '{category_name}' ({category_type}) сохранена😊\n"
                "🔙 Возвращаемся в главное меню!\n",
                reply_markup=await start_keyboard()
            )
        await state.clear()
    except Exception as e:
        print(f"⚠ Ошибка при финальном сохранении категории: {e.__class__.__name__}: {e}")
        await message.answer(
            "Произошла ошибка во время сохранения. Попробуйте еще раз.",
            reply_markup=await start_keyboard()
        )
        await state.clear()

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
