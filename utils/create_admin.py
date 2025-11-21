#!/usr/bin/env python3
"""
Скрипт для создания администратора
Использование: python utils/create_admin.py <user_id>
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from models.user import UserRole

def create_admin(user_id: int):
    """Создает администратора с указанным user_id"""
    db = Database()
    
    # Получаем пользователя
    user = db.get_user(user_id)
    
    if user:
        # Обновляем роль
        success = db.set_user_role(user_id, UserRole.ADMIN)
        if success:
            print(f"✅ Пользователь {user_id} теперь администратор")
        else:
            print(f"❌ Ошибка при обновлении роли")
    else:
        # Создаем нового пользователя с ролью админа
        db.add_user(
            user_id=user_id,
            username=None,
            first_name="Admin",
            last_name=None,
            role=UserRole.ADMIN
        )
        print(f"✅ Создан новый администратор с ID {user_id}")
        print(f"⚠️  Не забудьте обновить данные пользователя через бота")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python utils/create_admin.py <user_id>")
        print("\nПример: python utils/create_admin.py 123456789")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
        create_admin(user_id)
    except ValueError:
        print("❌ Ошибка: user_id должен быть числом")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

