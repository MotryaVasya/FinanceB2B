"""
Модуль для хранения и управления состояниями пользователей

Основной класс Save предоставляет интерфейс для:
- Добавления/обновления данных пользователей
- Получения данных по ID пользователя
- Удаления записей
- Конвертации в JSON
- Вывода данных в консоль

Пример использования:
```
    saver = Save()
    await saver.update(123, "test_data")
    await saver.print()
```
"""

from typing import Dict, List
import json


class Save:
    """Класс для сохранения и управления состояниями пользователей"""
    
    def __init__(self):
        """
        Инициализация хранилища.
        
        user_states: словарь для хранения данных в формате {user_id: [data1, data2, ...]}
        """
        self.user_states: Dict[int, List[str]] = {}

    async def update(self, user_id: int, data: str) -> List[str]:
        """
        Добавляет или обновляет данные пользователя
        
        Args:
            user_id: Идентификатор пользователя
            data: Строка данных для добавления
            
        Returns:
            Обновленный список данных пользователя или пустой список при ошибке
        """
        try:
            if user_id in self.user_states:
                self.user_states[user_id].append(data)
            else:
                self.user_states[user_id] = [data]
            return self.user_states[user_id]
        except Exception as e:
            print(f"Ошибка при обновлении данных пользователя {user_id}: {e}")
            return []

    async def get(self, user_id: int) -> List[str]:
        """
        Получает данные пользователя по ID
        
        Args:
            user_id: Идентификатор пользователя
            
        Returns:
            Список данных пользователя или пустой список если данных нет/произошла ошибка
        """
        try:
            return self.user_states.get(user_id, [])
        except Exception as e:
            print(f"Ошибка при получении данных пользователя {user_id}: {e}")
            return []

    async def delete(self, user_id: int) -> bool:
        """
        Удаляет данные пользователя
        
        Args:
            user_id: Идентификатор пользователя для удаления
            
        Returns:
            True если удаление прошло успешно, False если пользователь не найден или произошла ошибка
        """
        try:
            if user_id in self.user_states:
                del self.user_states[user_id]
                return True
            return False
        except Exception as e:
            print(f"Ошибка при удалении пользователя {user_id}: {e}")
            return False

    async def convert_to_json(self) -> str:
        """
        Конвертирует все данные в JSON строку
        
        Returns:
            Строка в формате JSON или пустая строка при ошибке
        """
        try:
            return json.dumps(self.user_states)
        except Exception as e:
            print(f"Ошибка при конвертации в JSON: {e}")
            return ""

    async def print(self) -> None:
        """
        Выводит все данные в консоль в читаемом формате
        
        Формат вывода:
            User [ID]: [список данных]
        """
        try:
            if not self.user_states:
                print("Нет данных для отображения")
                return
                
            print("\nТекущие состояния пользователей:")
            for user_id, data in self.user_states.items():
                print(f"  User {user_id}: {data}")
            print()  # Пустая строка для разделения
        except Exception as e:
            print(f'Ошибка при выводе данных: {e}')
save=Save()