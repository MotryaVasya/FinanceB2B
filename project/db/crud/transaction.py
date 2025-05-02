"""
Модуль для работы с транзакциями в системе учёта финансов пользователей.

Этот модуль реализует функции для создания, получения, обновления и удаления транзакций, а также для получения статистики по транзакциям. Основные операции выполняются асинхронно с использованием SQLAlchemy и FastAPI.

Основные функции:

1. **parse_naive_datetime(date_input: str | datetime) -> datetime**:
    Преобразует строку или datetime в naive datetime (без таймзоны). Генерирует исключение HTTP 400, если формат даты некорректен или дата содержит таймзону.

2. **update_money_for_user_for_create(session: AsyncSession, data: TransactionCreate)**:
    Обновляет баланс пользователя при создании новой транзакции в зависимости от её типа (расход или доход).

3. **update_money_for_user_for_update(session: AsyncSession, data: TransactionUpdate, transaction: Transaction)**:
    Обновляет баланс пользователя при обновлении транзакции, включая откат старой суммы и учёт новой суммы.

4. **update_money_for_user_for_delete(session: AsyncSession, transaction: Transaction)**:
    Обновляет баланс пользователя при удалении транзакции.

5. **check_date(month)**:
    Возвращает диапазон дат для указанного месяца (с начала до конца месяца).

6. **create_transaction(session: AsyncSession, data: TransactionCreate) -> Transaction | None**:
    Создаёт новую транзакцию в базе данных и обновляет баланс пользователя.

7. **get_transaction(session: AsyncSession, transaction_id: int, as_pydantic: bool = True) -> Transaction | None**:
    Получает транзакцию по её ID из базы данных.

8. **get_all_transactions(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Transaction]**:
    Получает список транзакций с возможностью пагинации (skip, limit).

9. **update_transaction(session: AsyncSession, transaction_id: int, data: TransactionUpdate) -> Transaction | None**:
    Обновляет транзакцию по её ID, включая все необходимые изменения.

10. **delete_transaction(session: AsyncSession, transaction_id: int) -> bool**:
    Удаляет транзакцию по её ID и обновляет баланс пользователя.

11. **get_transactions_from_month(session: AsyncSession, month: int, user_id: int) -> TransactionStatistics**:
    Получает статистику транзакций пользователя за указанный месяц, включая доходы, расходы и топ-3 категории.

12. **get_statistics(session: AsyncSession, from_date: datetime, to_date: datetime, user_id: int) -> TransactionStatistics**:
    Получает статистику транзакций пользователя за указанный период (от даты `from_date` до `to_date`), включая доходы, расходы и топ-3 категории.

Основные исключения, с которыми работает модуль:
- HTTPException: для обработки ошибок при создании, обновлении или удалении транзакций, а также ошибок при валидации данных.
- SQLAlchemyError: для обработки ошибок, связанных с базой данных.
- Логирование ошибок в случае возникновения исключений.

Этот модуль предоставляет базовую функциональность для управления финансовыми транзакциями и генерации статистики по ним, поддерживая асинхронный подход к работе с базой данных и обработку ошибок для устойчивости приложения.

"""

from datetime import datetime, timedelta
import json
import logging
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, extract
from sqlalchemy.exc import DataError, ProgrammingError, NoResultFound, DatabaseError, SQLAlchemyError, InvalidRequestError, DBAPIError, DisconnectionError

from project.db.models.category import Transaction, Category, User # TODO потом поменять импорт из category
from project.db.schemas.transaction import CategorySum, TopCategoryOut, TransactionCreate, TransactionStatistics, TransactionUpdate


async def parse_naive_datetime(date_input: str | datetime) -> datetime:
    """
    Преобразует строку или datetime в naive datetime (без таймзоны).
    Бросает HTTPException при ошибке парсинга или наличии tzinfo.
    """
    if isinstance(date_input, str):
        try:
            date_input = datetime.fromisoformat(date_input)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Неверный формат даты. Используй ISO 8601, например: '2025-04-23T14:30:00'"
            )
    if date_input.tzinfo is not None:
        date_input = date_input.replace(tzinfo=None)
    return date_input

async def update_money_for_user_for_create(user_id: int, session: AsyncSession, data: TransactionCreate):
    """
    Обновляет баланс пользователя при создании новой транзакции.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных.
        data (TransactionCreate): Данные новой транзакции.

    Raises:
        HTTPException: Если категория или пользователь не найдены.

    Logic:
        - Если транзакция типа 'расход' (type == 0) — уменьшает баланс пользователя.
        - Если транзакция типа 'доход' (type == 1) — увеличивает баланс пользователя.
    """
    res_type = await session.execute(select(Category.type).where(Category.id == data.category_id))
    type = res_type.scalars().first()
    if type is None:
        raise HTTPException(status_code=400, detail="Не найдена категория с данным ID.")
    
    res_user = await session.execute(select(User).where(User.id == user_id))
    user = res_user.scalars().first()
    if user is None:
        raise HTTPException(status_code=400, detail="Не найден пользователь с данным ID.")

    if type == 0:
        user.cash -= Decimal(str(data.full_sum))
    else:  
        user.cash += Decimal(str(data.full_sum))

async def update_money_for_user_for_update(user_id: int, session: AsyncSession, data: TransactionUpdate, transaction: Transaction):
    """
    Обновляет баланс пользователя при обновлении существующей транзакции.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных.
        data (TransactionUpdate): Новые данные транзакции.
        transaction (Transaction): Старая версия транзакции из базы данных.

    Raises:
        HTTPException: Если старая/новая категория или пользователь не найдены.

    Logic:
        - Возвращает сумму старой транзакции в баланс пользователя.
        - Применяет сумму новой транзакции к балансу пользователя, учитывая тип категории.
    """
    old_sum = transaction.full_sum
    new_sum = data.full_sum

    res_old_type = await session.execute(select(Category.type).where(Category.id == transaction.category_id))
    old_type = res_old_type.scalars().first()
    if old_type is None:
        raise HTTPException(status_code=404, detail="Старая категория не найдена.")

    res_new_type = await session.execute(select(Category.type).where(Category.id == data.category_id))
    new_type = res_new_type.scalars().first()
    if new_type is None:
        raise HTTPException(status_code=404, detail="Новая категория не найдена.")
        
    res_user = await session.execute(select(User).where(User.id == user_id))
    user = res_user.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    old_sum_decimal = Decimal(str(old_sum))
    new_sum_decimal = Decimal(str(new_sum))

    if old_type == 0:  
        user.cash += old_sum_decimal
    elif old_type == 1: 
        user.cash -= old_sum_decimal

    if new_type == 0: 
        user.cash -= new_sum_decimal
    elif new_type == 1: 
        user.cash += new_sum_decimal

async def update_money_for_user_for_delete(session: AsyncSession, transaction: Transaction):
    """
    Обновляет баланс пользователя при удалении транзакции.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных.
        transaction (Transaction): Удаляемая транзакция.

    Logic:
        - Если транзакция была расходом (type == 0) — возвращает сумму пользователю.
        - Если транзакция была доходом (type == 1) — вычитает сумму у пользователя.
    """
    trans_sum = transaction.full_sum
    res_type = await session.execute(select(Category.type).where(Category.id == transaction.category_id))
    type = res_type.scalars().first()
    res_user = await session.execute(select(User).where(User.id == transaction.user_id))
    user = res_user.scalars().first()

    if type == 0:
        user.cash += Decimal(str(trans_sum))
    elif type == 1:
        user.cash -= Decimal(str(trans_sum))

async def check_date(month):
    """
    Определяет диапазон дат для указанного месяца в текущем году.

    Этот метод вычисляет начальную и конечную дату для указанного месяца. 
    Он возвращает начало месяца и конец месяца (включая последнюю секунду), чтобы 
    получить правильный диапазон для запросов или статистики.

    Примечание: если месяц — декабрь (12), то конечная дата будет последней секундой 
    31 декабря текущего года.

    Args:
        month (int): Месяц для вычисления диапазона дат (1-12).

    Returns:
        tuple: Кортеж из двух объектов datetime — начало месяца и конец месяца (включая последнюю секунду).
    """
    now = datetime.now()
    year = now.year
    from_date = datetime(year, month, 1)
    if month == 12:
        to_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        to_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
    return from_date, to_date

async def create_transaction(user_id: int, session: AsyncSession, data: TransactionCreate) -> Transaction | None:
    """
    Создает новую транзакцию в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (TransactionCreate): Данные для создания транзакции.

    Returns:
        Transaction: Созданный объект транзакции или None при ошибке.
    """
    try:
        parsed_date = await parse_naive_datetime(data.date)
        user_id_subquery = select(User.id).where(User.tg_id == user_id).scalar_subquery()

        transaction = Transaction(
            description=data.description,
            full_sum=data.full_sum,
            date=parsed_date,
            category_id=data.category_id,
            user_id=user_id_subquery
        )

        await update_money_for_user_for_create(user_id_subquery,session, data)

        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)

        result = transaction.to_pydantic()
        if result is None:
            raise ValueError("Не удалось преобразовать транзакцию в Pydantic модель.")
            
        return result
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используй ISO формат: YYYY-MM-DDTHH:MM:SS")
    except (DataError, ProgrammingError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания транзакции",
            "data": data.model_dump(),
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None
    except HTTPException as e:
        await session.rollback()
        raise e
    except Exception as e:
        await session.rollback()
        logging.error(f"Неизвестная ошибка: {str(e)}")
        raise HTTPException(status_code=500, detail="Произошла ошибка при создании транзакции.")

async def get_transaction(session: AsyncSession, transaction_id: int, as_pydantic: bool = True) -> Transaction | None:
    """
    Получает транзакцию по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        transaction_id (int): Идентификатор транзакции.
        as_pydantic (bool): Переводит в тип (pydantic) если True, иначе тип Transaction
    Returns:
        Transaction: Объект транзакции, если найден, иначе None.
    """
    if transaction_id <= 0:
        return None
    try:
        result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction = result.scalars().first()
        if transaction is None:
            return None
        if as_pydantic:
            return transaction.to_pydantic()
        else:
            return transaction
    except (NoResultFound, DatabaseError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения транзакции",
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all_transactions(user_id: int, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Transaction]:
    """
    Получает список транзакций с диапозоном.

    Пример использования:
        # Получить первые 10 транзакций
        transactions = await get_all_transactions(session, skip=0, limit=10)
        
        # Получить следующую порцию (транзакции 11-20)
        next_transact = await get_all_transactions(session, skip=10, limit=10)

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        skip (int): Количество пропускаемых записей (по умолчанию 0).
            Например, skip=10 пропустит первые 10 записей.
        limit (int): Максимальное количество возвращаемых записей (по умолчанию 100).
            Например, limit=20 вернет не более 20 транзакций.

    Returns:
        list[Transaction]: Список транзакций. Возвращает пустой список, если:
            - транзакции отсутствуют
            - указана комбинация skip/limit за пределами общего количества
            - произошла ошибка при запросе
    """
    try:
        user_id_subquery = select(User.id).where(User.tg_id == user_id).scalar_subquery()
        result = await session.execute(
            select(Transaction, Category.name_category.label("name_category"))
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id_subquery)
            .offset(skip)
            .limit(limit)
        )
        transactions = result.all()
        return [transaction.to_pydantic(category_name=name_category) for transaction, name_category in transactions] or []
    except (SQLAlchemyError) as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка транзакций",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
        
async def update_transaction(user_id: int, session: AsyncSession, transaction_id: int, data: TransactionUpdate) -> Transaction | None:
    """
    Обновляет транзакцию в базе данных по указанному ID.

    Этот метод выполняет следующие шаги:
    1. Проверяет, что ID транзакции больше нуля. Если нет, возвращается None.
    2. Пытается получить транзакцию по указанному ID. Если транзакция не найдена, возвращает None.
    3. Выполняет дополнительное обновление суммы для пользователя, если это необходимо.
    4. Обновляет поля транзакции на основе переданных данных, исключая неустановленные значения.
    5. Если в данных обновляется дата, она парсится в формат временной метки.
    6. После всех изменений коммитит изменения в базе данных и возвращает обновленную транзакцию в виде Pydantic модели.

    Если при обновлении происходит ошибка (например, ошибка атрибута или тип данных), транзакция откатывается и генерируется исключение с ошибкой.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        transaction_id (int): ID транзакции, которую нужно обновить.
        data (TransactionUpdate): Данные для обновления транзакции.

    Returns:
        Transaction|None: Обновленная транзакция в формате Pydantic, если обновление прошло успешно, или None, если транзакция не найдена или произошла ошибка.

    Raises:
        HTTPException: В случае ошибок при обновлении транзакции генерируется исключение с кодом 500.
    """
    if transaction_id <= 0:
        return None
    try:
        user_id_subquery = select(User.id).where(User.tg_id == user_id).scalar_subquery()
        transaction = await get_transaction(session, transaction_id, as_pydantic=False)
        if not transaction:
            return None
        
        await update_money_for_user_for_update(user_id_subquery, session, data, transaction)


        updates = data.model_dump(exclude_unset=True)

        if "date" in updates:
           updates['date'] = await parse_naive_datetime(updates["date"])

        for key, value in updates.items():
            setattr(transaction, key, value)


        await session.commit()
        await session.refresh(transaction)
        return transaction.to_pydantic()

    except (InvalidRequestError, AttributeError, TypeError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка обновления транзакции",
            "data": data.model_dump(),
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении транзакции"
        )

async def delete_transaction(session: AsyncSession, transaction_id: int) -> bool:
    """
    Удаляет транзакцию по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        transaction_id (int): Идентификатор транзакции для удаления.

    Returns:
        bool: True, если транзакция удалена, False если транзакция не найдена.
    """
    if transaction_id <= 0:
        return False
    try:
        transaction = await get_transaction(session, transaction_id, False)
        if not transaction:
            return False
        
        await update_money_for_user_for_delete(session, transaction)

        await session.delete(transaction)
        await session.commit()
        return True
    except (DBAPIError, DisconnectionError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка удаления транзакции",
            "transaction_id": transaction_id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return False


async def get_transactions_from_month(session: AsyncSession, month: int, user_id: int) -> TransactionStatistics:
    """
    Получает статистику транзакций пользователя за указанный месяц, включая общий доход, расход и топ-3 категории.

    Этот метод выполняет запрос к базе данных, чтобы собрать информацию о транзакциях пользователя за выбранный месяц,
    суммирует доходы и расходы, а также находит топ-3 категории по количеству транзакций. Возвращает статистику, 
    которая включает сумму доходов, расходов и топ-3 категории с историей транзакций.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных для выполнения запросов.
        month (int): Номер месяца, за который требуется получить статистику (от 1 до 12).
        user_id (int): ID пользователя, для которого собирается статистика.

    Returns:
        TransactionStatistics: Статистика по транзакциям за указанный месяц, включая:
            - from_date (datetime): Начало месяца.
            - to_date (datetime): Конец месяца.
            - income (CategorySum): Сумма доходов за месяц.
            - expense (CategorySum): Сумма расходов за месяц.
            - top_categories (list[TopCategoryOut]): Топ-3 категории по количеству транзакций, включая название,
                полную сумму и историю транзакций.
    
    В случае ошибки в процессе получения статистики возвращается дефолтная структура с пустыми значениями:
    доход = 0, расход = 0, топ-3 категории — пустой список.
    """
    try:
        user_id_subquery = select(User.id).where(User.tg_id == user_id).scalar_subquery()
        result = await session.execute(
            select(
                Transaction.category_id,
                Category.name_category.label("category_name"),
                func.sum(Transaction.full_sum).label("total_sum"),
                func.count(Transaction.id).label("transaction_count"),
                func.array_agg(Transaction.full_sum).label("transaction_sums"),
                Category.type.label("category_type")
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(
                extract('month', Transaction.date) == month,
                Transaction.user_id == user_id_subquery
            )
            .group_by(
                Transaction.category_id,
                Category.name_category,
                Category.type
            )
            .having(func.count(Transaction.id) > 0)
            .order_by(func.count(Transaction.id).desc())
        )

        transactions = result.all()

        # Считаем общий доход и расход
        total_income = Decimal('0')
        total_expense = Decimal('0')

        top_categories: list[TopCategoryOut] = []

        for category_id, category_name, total_sum, transaction_count, transaction_sums, category_type in transactions:
            transaction_history = '+'.join(str(float(s)) for s in transaction_sums)

            top_categories.append(
                TopCategoryOut(
                    category_name=category_name,
                    full_sum=float(total_sum),
                    transaction_history=transaction_history
                )
            )

            if category_type == 1:  # Доход
                total_income += total_sum
            elif category_type == 0:  # Расход
                total_expense += total_sum

        # Определяем диапазон дат месяца для ответа
        from_date, to_date = await check_date(month)

        statistic = TransactionStatistics(
            from_date=from_date,
            to_date=to_date,
            income=CategorySum(
                sum=float(total_income),
                type=1
            ),
            expense=CategorySum(
                sum=float(total_expense),
                type=0
            ),
            top_categories=top_categories[:3]
        )
        return statistic

    except Exception as e:
        logging.error(json.dumps({
            "message": f"Ошибка получения списка транзакций за месяц {month} для пользователя {user_id}",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

        from_date, to_date = await check_date(month)
        statistic = TransactionStatistics(
            from_date=from_date,
            to_date=to_date,
            income=CategorySum(sum=0, type=1),
            expense=CategorySum(sum=0, type=0),
            top_categories=[]
        )
        return statistic

async def get_statistics(session: AsyncSession, from_date: datetime, to_date: datetime, user_id: int) -> TransactionStatistics:
    """
    Получает статистику по транзакциям пользователя за указанный период: доходы, расходы и топ-3 категории.
    
    Args:
        session (AsyncSession): Асинхронная сессия базы данных.
        from_date (datetime): Начальная дата диапазона.
        to_date (datetime): Конечная дата диапазона.
        user_id (int): ID пользователя.

    Returns:
        TransactionStatistics: Статистика транзакций пользователя.
    """
    try:
        user_id_subquery = select(User.id).where(User.tg_id == user_id).scalar_subquery()
        result = await session.execute(
            select(
                Transaction.category_id,
                Category.name_category.label("category_name"),
                func.sum(Transaction.full_sum).label("total_sum"),
                func.count(Transaction.id).label("transaction_count"),
                func.array_agg(Transaction.full_sum).label("transaction_sums"),
                Category.type.label("category_type")
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.date >= from_date,
                Transaction.date <= to_date,
                Transaction.user_id == user_id_subquery
            )
            .group_by(
                Transaction.category_id,
                Category.name_category,
                Category.type
            )
            .having(func.count(Transaction.id) > 0)
            .order_by(func.count(Transaction.id).desc())
        )

        transactions = result.all()

        # Считаем общий доход и расход
        total_income = Decimal('0')
        total_expense = Decimal('0')

        top_categories: list[TopCategoryOut] = []

        for category_id, category_name, total_sum, transaction_count, transaction_sums, category_type in transactions:
            # Склеиваем историю транзакций в строку ("500+500+500")
            transaction_history = '+'.join(str(float(s)) for s in transaction_sums)

            top_categories.append(
                TopCategoryOut(
                    category_name=category_name,
                    full_sum=float(total_sum),
                    transaction_history=transaction_history
                )
            )

            if category_type == 1:  # Доход
                total_income += total_sum
            elif category_type == 0:  # Расход
                total_expense += total_sum

        return TransactionStatistics(
            from_date=from_date,
            to_date=to_date,
            income=CategorySum(
                sum=float(total_income),
                type=1
            ),
            expense=CategorySum(
                sum=float(total_expense),
                type=0
            ),
            top_categories=top_categories[:3]  # Только топ-3 категории
        )

    except Exception as e:
        logging.error(json.dumps({
            "message": f"Ошибка получения данных по транзакциям с {str(from_date)} до {str(to_date)} для пользователя {user_id}",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return TransactionStatistics(
            from_date=from_date,
            to_date=to_date,
            income=CategorySum(sum=0, type=1),
            expense=CategorySum(sum=0, type=0),
            top_categories=[]
        )
