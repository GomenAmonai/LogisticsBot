from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей в системе"""
    CLIENT = "client"  # Клиент
    ADMIN = "admin"  # Администратор
    MANAGER = "manager"  # Менеджер логистической компании


class User:
    """Модель пользователя"""
    def __init__(self, user_id, username=None, first_name=None, last_name=None, role=UserRole.CLIENT):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
    
    def is_admin(self):
        """Проверяет, является ли пользователь администратором"""
        return self.role == UserRole.ADMIN
    
    def is_manager(self):
        """Проверяет, является ли пользователь менеджером"""
        return self.role == UserRole.MANAGER
    
    def is_client(self):
        """Проверяет, является ли пользователь клиентом"""
        return self.role == UserRole.CLIENT

