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
class SaveUserData:
    '''
    Класс для сохранения и изменения списка задач для пользователей\n
    :param user_data (dict): список в котором хранится\n
    :param key (str): ID пользователя\n
    :param value (dict): остальные данные по типу: <b>user_id, task_name, task_description, start_date_task, end_date_task </b>и<b> priority</b>
    '''
    def __init__(self):
        self.user_data = {int: {}}
        del self.user_data[int]

    async def update_dict(self, user_id: int, data: {}):
        '''
        <i>Этот метод обновляет или добавляет новый список по 'user_id'</i>\n 
        :param user_id (str): ID пользователя
        :param data (dict): Данные для добавления/обновления
        '''
        try:
            if self.user_data.get(user_id):
                current_data = self.user_data.get(user_id)
                current_data.update(data)
                self.user_data[user_id] = current_data
            else:
                self.user_data.update({user_id: data})
        except Exception as e:
            print(f'Error occurred while updating dictionary: {str(e)}')

    async def delete_id(self, user_id: int):
        '''
        <i>Этот метод удаляет список по 'user_id', если его нету то он выикдывает ошибку</i>\n
        :param user_id (str): ID пользователя
        '''
        try:
            del self.user_data[user_id]
        except Exception as e:
            print(f'Error occurred while deleting ID: {str(e)}')

    async def find_element_by_user_id(self, user_id):
        '''
        <i>Этот метод возвращает список по 'user_id', если его нету то он выикдывает ошибку</i>\n
        :param user_id (str): ID пользователя
        :return: dict
        '''
        try:
            return self.user_data[user_id]
        except Exception as e:
            print(f'Error occurred while finding ID: {str(e)}')

    async def convert_to_json(self):
        '''
        <i>Этот метод возвращает список в формате JSON, если что-то пошло не так, он выкидывает ошибку но не завершает программу</i>\n
        :return: JSON
        '''
        try:
            return json.dumps(self.user_data, indent=4)
        except Exception as e:
            print(f'Error occurred while converting to JSON: {str(e)}')

    async def print(self):
        '''
        <i>Этот метод выводит список в консоль</i>\n
        '''
        try:
            for item in self.user_data.items():
                print(item)
        except Exception as e:
            print(f'Error occurred while printing: {str(e)}')
        
    
    # TODO до конца не уверен рабоатет это или нет, надо будет проверить, я не до конца понимаю как работает __call__
    async def __call__(self, user_id: int, key: str):
        ''' 
        <i>Этот метод возвращает True если по 'user_id' есть 'key' который имеет значение, иначе False</i>\n
        :param user_id (str): ID пользователя
        :param key (str): ключ
        :return: bool
        '''
        return self.user_data[user_id].get(key) is not None
save_user_data=SaveUserData()
save=Save()