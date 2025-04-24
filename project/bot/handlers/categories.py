from aiogram import Router, types, F
from aiogram.types import Message
from project.bot.states import *
from project.bot.messages.messages import *
from aiogram.types import KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f,StateFilter
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
        
@router.message(F.text == "Добавить")
async def add_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    open("main44.txt", "w").write(str(await save.update(user_id, "ADD_CATEGORY")))
    await message.answer("✏️ Введите название вашей категории:")

@router.message(or_f(F.text == "Доход", F.text == "Расход"))
async def after_add(message: Message):
    user_id = message.from_user.id
    open("main44.txt", "w").write(str(await save.update(user_id, "AFTER_ADD")))
    try:
        await message.answer(
            "🎉 Отлично! Я сохранил вашу категорию 😊"
            "🔙 Возвращаемся в главное меню!",
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

@router.message(StateFilter(CategoryStates.new_category_name))
async def handle_text_input(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and "current_category" in user_data[user_id]:
        old_name = user_data[user_id]["current_category"]
        user_data[user_id]["new_name"] = message.text
        try:
            await message.answer(
                f"Вы изменили название с '{old_name}' на '{message.text}'\n"
                "Теперь укажите тип категории:",
                reply_markup=await make_type_keyboard()
            )
        except Exception as e:
            print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text == "Сохранить изменения")
async def save_changes(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        category = user_data[user_id].get("current_category")
        new_type = user_data[user_id].get("type", "не изменён")
        try:
            await message.answer(
                f"🎉 Отлично! Категория '{category}' изменена!\n"
                f"Тип: {new_type}\n\n"
                "🔙 Возвращаемся в главное меню!",
                reply_markup=ReplyKeyboardRemove()
            )
            user_data.pop(user_id)
        except Exception as e:
            print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")
    else:
        await message.answer("Нечего сохранять", reply_markup=ReplyKeyboardRemove())

@router.message(F.text == "Пропустить")
async def skip_name(message: types.Message):
    user_id = message.from_user.id
    if not user_data.get(user_id):
        return await message.answer("Ошибка: категория не выбрана")
    try:
        await message.answer(
            "🔄 Хорошо! Давайте изменим тип вашей категории 😊",
            reply_markup=await make_type_keyboard()
        )
    except Exception as e:
        print(f"⚠ Ошибка: {e.__class__.__name__}: {e}")

@router.message(F.text.in_(["Доход", "Расход"]))
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

@router.message(F.text == "Пропустить")
async def skip_type(message: types.Message):
    user_id = message.from_user.id
    open("main44.txt", "w").write(str(await save.update(user_id, "SKIP_TYPE")))
    try:
        await message.answer(
            "✨ Всё супер! Сохраняем изменения? 😊",
            reply_markup=await make_save_keyboard()
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