import sqlite3
import os
from typing import Optional, List, Tuple
from config import DATABASE_PATH
from models.user import UserRole


class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        # Создаем директорию для БД, если её нет
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Создает и возвращает соединение с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Инициализирует базу данных и создает необходимые таблицы"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Создаем таблицу пользователей с ролью
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                role TEXT DEFAULT 'client',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем таблицу для хранения данных пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                data_key TEXT,
                data_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Создаем таблицу для заказов с расширенными полями
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                manager_id INTEGER,
                status TEXT DEFAULT 'pending',
                description TEXT,
                from_address TEXT,
                to_address TEXT,
                from_contact TEXT,
                to_contact TEXT,
                weight REAL,
                price REAL,
                payment_status TEXT DEFAULT 'unpaid',
                payment_method TEXT,
                tracking_number TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES users(user_id),
                FOREIGN KEY (manager_id) REFERENCES users(user_id)
            )
        ''')
        
        # Создаем таблицу для тикетов (назначение заказов менеджерам)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                manager_id INTEGER,
                status TEXT DEFAULT 'new',
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accepted_at TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (manager_id) REFERENCES users(user_id)
            )
        ''')
        
        # Создаем таблицу для отслеживания доставок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                status TEXT,
                location TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        ''')
        
        # Создаем таблицу для платежей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                amount REAL,
                payment_method TEXT,
                status TEXT DEFAULT 'pending',
                transaction_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        ''')
        
        # Создаем таблицу для адресов пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                address_type TEXT,
                address TEXT,
                contact_name TEXT,
                contact_phone TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: Optional[str] = None, 
                 first_name: Optional[str] = None, last_name: Optional[str] = None,
                 role: str = UserRole.CLIENT) -> bool:
        """Добавляет или обновляет пользователя в базе данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Обновляем существующего пользователя
            cursor.execute('''
                UPDATE users 
                SET username = ?, first_name = ?, last_name = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (username, first_name, last_name, user_id))
        else:
            # Добавляем нового пользователя
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, role))
        
        conn.commit()
        conn.close()
        return True
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Получает информацию о пользователе"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        if row:
            return dict(row)
        return None
    
    def set_user_role(self, user_id: int, role: str) -> bool:
        """Устанавливает роль пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET role = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (role, user_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def get_all_users(self, role: Optional[str] = None) -> List[dict]:
        """Получает список всех пользователей, опционально фильтруя по роли"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if role:
            cursor.execute('SELECT * FROM users WHERE role = ? ORDER BY created_at DESC', (role,))
        else:
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def save_user_data(self, user_id: int, data_key: str, data_value: str) -> bool:
        """Сохраняет данные пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_data (user_id, data_key, data_value)
            VALUES (?, ?, ?)
        ''', (user_id, data_key, data_value))
        
        conn.commit()
        conn.close()
        return True
    
    def get_user_data(self, user_id: int, data_key: str) -> Optional[str]:
        """Получает данные пользователя по ключу"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data_value FROM user_data 
            WHERE user_id = ? AND data_key = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user_id, data_key))
        
        result = cursor.fetchone()
        conn.close()
        return result['data_value'] if result else None
    
    def create_order(self, client_id: int, description: str, from_address: str = None,
                     to_address: str = None, from_contact: str = None, to_contact: str = None,
                     weight: float = None, price: float = None, manager_id: Optional[int] = None) -> int:
        """Создает новый заказ"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Генерируем tracking number
        import random
        import string
        tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        cursor.execute('''
            INSERT INTO orders (client_id, manager_id, description, from_address, to_address,
                              from_contact, to_contact, weight, price, tracking_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (client_id, manager_id, description, from_address, to_address,
              from_contact, to_contact, weight, price, tracking_number))
        
        order_id = cursor.lastrowid
        
        # Создаем тикет для менеджера, если указан
        if manager_id:
            cursor.execute('''
                INSERT INTO tickets (order_id, manager_id, status)
                VALUES (?, ?, 'new')
            ''', (order_id, manager_id))
            ticket_id = cursor.lastrowid
            
            # Отправляем уведомление о новом тикете
            try:
                from utils.telegram_logger import send_log_sync, format_ticket_notification, init_log_group
                from config import LOG_GROUP_ID
                
                if LOG_GROUP_ID:
                    init_log_group(LOG_GROUP_ID)
                    ticket_data = {
                        'id': ticket_id,
                        'order_id': order_id,
                        'client_id': client_id,
                        'manager_id': manager_id,
                        'description': description,
                        'status': 'new'
                    }
                    message = format_ticket_notification(ticket_data)
                    send_log_sync(message, parse_mode='HTML')
            except Exception as e:
                import logging
                logging.error(f"Ошибка отправки уведомления о тикете: {e}")
        
        # Создаем начальную запись отслеживания
        cursor.execute('''
            INSERT INTO tracking (order_id, status, location, description)
            VALUES (?, 'pending', 'Создан', 'Заказ создан и ожидает обработки')
        ''', (order_id,))
        
        conn.commit()
        # order_id уже получен выше, не нужно получать снова
        
        # Отправляем уведомление о новом заказе
        try:
            from utils.telegram_logger import send_log_sync, format_order_notification, init_log_group
            from config import LOG_GROUP_ID
            
            if LOG_GROUP_ID:
                init_log_group(LOG_GROUP_ID)
                order_data = {
                    'id': order_id,
                    'client_id': client_id,
                    'from_address': from_address,
                    'to_address': to_address,
                    'price': price,
                    'status': 'pending'
                }
                message = format_order_notification(order_data)
                send_log_sync(message, parse_mode='HTML')
        except Exception as e:
            import logging
            logging.error(f"Ошибка отправки уведомления о заказе: {e}")
        
        conn.close()
        return order_id
    
    def get_order(self, order_id: int) -> Optional[dict]:
        """Получает информацию о заказе"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def update_order_status(self, order_id: int, status: str, manager_id: Optional[int] = None) -> bool:
        """Обновляет статус заказа"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if manager_id:
            cursor.execute('''
                UPDATE orders 
                SET status = ?, manager_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, manager_id, order_id))
        else:
            cursor.execute('''
                UPDATE orders 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, order_id))
        
        # Добавляем запись в отслеживание
        status_descriptions = {
            'pending': 'Ожидает обработки',
            'accepted': 'Принят в работу',
            'in_transit': 'В пути',
            'delivered': 'Доставлен',
            'cancelled': 'Отменен'
        }
        
        cursor.execute('''
            INSERT INTO tracking (order_id, status, description)
            VALUES (?, ?, ?)
        ''', (order_id, status, status_descriptions.get(status, status)))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def create_ticket(self, order_id: int, manager_id: int) -> int:
        """Создает тикет для менеджера"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets (order_id, manager_id, status)
            VALUES (?, ?, 'new')
        ''', (order_id, manager_id))
        
        ticket_id = cursor.lastrowid
        
        # Обновляем заказ, назначая менеджера
        cursor.execute('''
            UPDATE orders SET manager_id = ? WHERE id = ?
        ''', (manager_id, order_id))
        
        conn.commit()
        conn.close()
        return ticket_id
    
    def get_manager_tickets(self, manager_id: int, status: Optional[str] = None) -> List[dict]:
        """Получает тикеты менеджера"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT t.*, o.* FROM tickets t
                JOIN orders o ON t.order_id = o.id
                WHERE t.manager_id = ? AND t.status = ?
                ORDER BY t.assigned_at DESC
            ''', (manager_id, status))
        else:
            cursor.execute('''
                SELECT t.*, o.* FROM tickets t
                JOIN orders o ON t.order_id = o.id
                WHERE t.manager_id = ?
                ORDER BY t.assigned_at DESC
            ''', (manager_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def accept_ticket(self, ticket_id: int) -> bool:
        """Принимает тикет менеджером"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tickets 
            SET status = 'accepted', accepted_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (ticket_id,))
        
        # Обновляем статус заказа
        cursor.execute('''
            UPDATE orders SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT order_id FROM tickets WHERE id = ?)
        ''', (ticket_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def get_order_tracking(self, order_id: int) -> List[dict]:
        """Получает историю отслеживания заказа"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tracking 
            WHERE order_id = ?
            ORDER BY created_at ASC
        ''', (order_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_tracking_event(self, order_id: int, status: str, location: str = None, description: str = None) -> bool:
        """Добавляет событие отслеживания"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tracking (order_id, status, location, description)
            VALUES (?, ?, ?, ?)
        ''', (order_id, status, location, description))
        
        conn.commit()
        conn.close()
        return True
    
    def create_payment(self, order_id: int, amount: float, payment_method: str) -> int:
        """Создает запись о платеже"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        import uuid
        transaction_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO payments (order_id, amount, payment_method, status, transaction_id)
            VALUES (?, ?, ?, 'pending', ?)
        ''', (order_id, amount, payment_method, transaction_id))
        
        payment_id = cursor.lastrowid
        
        # Обновляем статус оплаты в заказе
        cursor.execute('''
            UPDATE orders SET payment_status = 'pending' WHERE id = ?
        ''', (order_id,))
        
        conn.commit()
        conn.close()
        return payment_id
    
    def complete_payment(self, payment_id: int) -> bool:
        """Завершает платеж"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE payments 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (payment_id,))
        
        # Обновляем статус оплаты в заказе
        cursor.execute('''
            UPDATE orders SET payment_status = 'paid' 
            WHERE id = (SELECT order_id FROM payments WHERE id = ?)
        ''', (payment_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def get_order_payments(self, order_id: int) -> List[dict]:
        """Получает платежи по заказу"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM payments 
            WHERE order_id = ?
            ORDER BY created_at DESC
        ''', (order_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def assign_order_to_manager(self, order_id: int, manager_id: int) -> bool:
        """Назначает заказ менеджеру (создает тикет)"""
        # Проверяем, нет ли уже тикета
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM tickets WHERE order_id = ?', (order_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Обновляем существующий тикет
            cursor.execute('''
                UPDATE tickets 
                SET manager_id = ?, status = 'new', assigned_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            ''', (manager_id, order_id))
        else:
            # Создаем новый тикет
            cursor.execute('''
                INSERT INTO tickets (order_id, manager_id, status)
                VALUES (?, ?, 'new')
            ''', (order_id, manager_id))
        
        # Обновляем заказ
        cursor.execute('''
            UPDATE orders SET manager_id = ? WHERE id = ?
        ''', (manager_id, order_id))
        
        conn.commit()
        conn.close()
        return True
    
    def get_user_orders(self, user_id: int, role: str) -> List[dict]:
        """Получает заказы пользователя в зависимости от роли"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if role == UserRole.CLIENT:
            cursor.execute('SELECT * FROM orders WHERE client_id = ? ORDER BY created_at DESC', (user_id,))
        elif role == UserRole.MANAGER:
            cursor.execute('SELECT * FROM orders WHERE manager_id = ? OR manager_id IS NULL ORDER BY created_at DESC', (user_id,))
        else:  # ADMIN
            cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
