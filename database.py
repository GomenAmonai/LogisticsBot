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
                privacy_accepted INTEGER DEFAULT 0,
                notifications_enabled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем колонку privacy_accepted если её нет (для существующих БД)
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN privacy_accepted INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
        # Добавляем колонку notifications_enabled если её нет
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN notifications_enabled INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
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
                offer_price REAL,
                offer_currency TEXT,
                offer_delivery_days INTEGER,
                offer_comment TEXT,
                offer_status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES users(user_id),
                FOREIGN KEY (manager_id) REFERENCES users(user_id)
            )
        ''')
        
        # Добавляем колонки оферты, если отсутствуют
        offer_columns = [
            ("offer_price", "REAL"),
            ("offer_currency", "TEXT"),
            ("offer_delivery_days", "INTEGER"),
            ("offer_comment", "TEXT"),
            ("offer_status", "TEXT DEFAULT 'draft'")
        ]
        for column_name, column_type in offer_columns:
            try:
                cursor.execute(f'ALTER TABLE orders ADD COLUMN {column_name} {column_type}')
            except sqlite3.OperationalError:
                pass
        
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
        
        # Таблица сообщений чата
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                sender_role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: Optional[str] = None, 
                 first_name: Optional[str] = None, last_name: Optional[str] = None,
                 role: str = UserRole.CLIENT, privacy_accepted: bool = False) -> bool:
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
                INSERT INTO users (user_id, username, first_name, last_name, role, privacy_accepted)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, role, 1 if privacy_accepted else 0))
        
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
            user_dict = dict(row)
            # Преобразуем privacy_accepted в boolean
            if 'privacy_accepted' in user_dict:
                user_dict['privacy_accepted'] = bool(user_dict['privacy_accepted'])
            # Преобразуем notifications_enabled в boolean
            if 'notifications_enabled' in user_dict:
                user_dict['notifications_enabled'] = bool(user_dict['notifications_enabled'])
            return user_dict
        return None
    
    def set_notifications_enabled(self, user_id: int, enabled: bool) -> bool:
        """Включает или выключает уведомления для пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET notifications_enabled = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (1 if enabled else 0, user_id))
        
        conn.commit()
        conn.close()
        return True
    
    def is_notifications_enabled(self, user_id: int) -> bool:
        """Проверяет, включены ли уведомления для пользователя"""
        user = self.get_user(user_id)
        if user and 'notifications_enabled' in user:
            return bool(user['notifications_enabled'])
        return False
    
    def accept_privacy(self, user_id: int) -> bool:
        """Отмечает, что пользователь принял политику конфиденциальности"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET privacy_accepted = 1, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def has_accepted_privacy(self, user_id: int) -> bool:
        """Проверяет, принял ли пользователь политику конфиденциальности"""
        user = self.get_user(user_id)
        if user:
            return user.get('privacy_accepted', False)
        return False
    
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
        
        # Отправляем уведомление клиенту, если уведомления включены
        try:
            if self.is_notifications_enabled(client_id):
                self._send_order_created_notification(client_id, order_id)
        except Exception as e:
            import logging
            logging.error(f"Ошибка отправки уведомления клиенту: {e}")
        
        conn.close()
        return order_id
    
    def _send_order_created_notification(self, client_id: int, order_id: int):
        """Отправляет уведомление клиенту о создании заказа"""
        try:
            from telegram import Bot
            from config import BOT_TOKEN
            import asyncio
            import threading
            
            if not BOT_TOKEN:
                return
            
            message = f"📦 <b>Заказ создан</b>\n\n"
            message += f"Ваш заказ #{order_id} успешно создан и ожидает обработки."
            
            def send_async():
                async def send():
                    bot = Bot(token=BOT_TOKEN)
                    try:
                        await bot.send_message(
                            chat_id=client_id,
                            text=message,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        import logging
                        logging.error(f"Ошибка отправки уведомления: {e}")
                
                asyncio.run(send())
            
            thread = threading.Thread(target=send_async)
            thread.start()
            
        except Exception as e:
            import logging
            logging.error(f"Ошибка создания уведомления: {e}")
    
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
        
        # Получаем информацию о заказе ДО обновления
        cursor.execute('SELECT client_id, status as old_status FROM orders WHERE id = ?', (order_id,))
        order_info = cursor.fetchone()
        old_status = order_info['old_status'] if order_info else None
        client_id = order_info['client_id'] if order_info else None
        
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
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        
        cursor.execute('''
            INSERT INTO tracking (order_id, status, description)
            VALUES (?, ?, ?)
        ''', (order_id, status, status_descriptions.get(status, status)))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        # Отправляем уведомление клиенту, если уведомления включены
        if client_id:
            try:
                if self.is_notifications_enabled(client_id):
                    self._send_order_notification(client_id, order_id, old_status, status)
            except Exception as e:
                import logging
                logging.error(f"Ошибка отправки уведомления клиенту: {e}")
        
        return success
    
    def _send_order_notification(self, client_id: int, order_id: int, old_status: str, new_status: str):
        """Отправляет уведомление клиенту об изменении статуса заказа"""
        try:
            from telegram import Bot
            from config import BOT_TOKEN
            import asyncio
            import threading
            
            if not BOT_TOKEN:
                return
            
            status_names = {
                'pending': 'Ожидает обработки',
                'accepted': 'Принят в работу',
                'in_transit': 'В пути',
                'delivered': 'Доставлен',
                'completed': 'Завершен',
                'cancelled': 'Отменен'
            }
            
            old_name = status_names.get(old_status, old_status) if old_status else 'новый'
            new_name = status_names.get(new_status, new_status)
            
            message = f"📦 <b>Изменение статуса заказа #{order_id}</b>\n\n"
            message += f"Статус изменен: {old_name} → {new_name}"
            
            def send_async():
                async def send():
                    bot = Bot(token=BOT_TOKEN)
                    try:
                        await bot.send_message(
                            chat_id=client_id,
                            text=message,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        import logging
                        logging.error(f"Ошибка отправки уведомления: {e}")
                
                asyncio.run(send())
            
            thread = threading.Thread(target=send_async)
            thread.start()
            
        except Exception as e:
            import logging
            logging.error(f"Ошибка создания уведомления: {e}")
    
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
        
        # Явно указываем колонки с алиасами, чтобы избежать конфликта имен
        if status:
            cursor.execute('''
                SELECT 
                    t.id AS ticket_id,
                    t.order_id,
                    t.manager_id,
                    t.status AS ticket_status,
                    t.assigned_at,
                    t.accepted_at,
                    o.id AS order_id_full,
                    o.client_id,
                    o.description,
                    o.from_address,
                    o.to_address,
                    o.price,
                    o.status AS order_status,
                    o.tracking_number,
                    o.created_at AS order_created_at
                FROM tickets t
                JOIN orders o ON t.order_id = o.id
                WHERE t.manager_id = ? AND t.status = ?
                ORDER BY t.assigned_at DESC
            ''', (manager_id, status))
        else:
            cursor.execute('''
                SELECT 
                    t.id AS ticket_id,
                    t.order_id,
                    t.manager_id,
                    t.status AS ticket_status,
                    t.assigned_at,
                    t.accepted_at,
                    o.id AS order_id_full,
                    o.client_id,
                    o.description,
                    o.from_address,
                    o.to_address,
                    o.price,
                    o.status AS order_status,
                    o.tracking_number,
                    o.created_at AS order_created_at
                FROM tickets t
                JOIN orders o ON t.order_id = o.id
                WHERE t.manager_id = ?
                ORDER BY t.assigned_at DESC
            ''', (manager_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Преобразуем результат в правильный формат
        result = []
        for row in rows:
            ticket_dict = dict(row)
            # Используем ticket_id как id для совместимости
            ticket_dict['id'] = ticket_dict['ticket_id']
            # Сохраняем order_id правильно
            ticket_dict['order_id'] = ticket_dict.get('order_id') or ticket_dict.get('order_id_full')
            # Используем ticket_status как status
            ticket_dict['status'] = ticket_dict['ticket_status']
            result.append(ticket_dict)
        
        return result
    
    def accept_ticket(self, ticket_id: int) -> bool:
        """Принимает тикет менеджером"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем информацию о заказе до обновления
        cursor.execute('''
            SELECT o.id as order_id, o.client_id, o.status as old_status
            FROM tickets t
            JOIN orders o ON t.order_id = o.id
            WHERE t.id = ?
        ''', (ticket_id,))
        order_info = cursor.fetchone()
        order_id = order_info['order_id'] if order_info else None
        client_id = order_info['client_id'] if order_info else None
        old_status = order_info['old_status'] if order_info else None
        
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
        
        # Отправляем уведомление клиенту, если уведомления включены
        if client_id and order_id:
            try:
                if self.is_notifications_enabled(client_id):
                    self._send_order_notification(client_id, order_id, old_status, 'accepted')
            except Exception as e:
                import logging
                logging.error(f"Ошибка отправки уведомления клиенту: {e}")
        
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

    def get_incoming_orders(self) -> List[dict]:
        """Возвращает заказы без назначенного менеджера"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE manager_id IS NULL ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_manager_assigned_orders(self, manager_id: int) -> List[dict]:
        """Возвращает заказы, назначенные конкретному менеджеру"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE manager_id = ? ORDER BY created_at DESC', (manager_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_chat_message(self, order_id: int, sender_id: int, sender_role: str, message: str) -> int:
        """Добавляет сообщение в чат заказа"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (order_id, sender_id, sender_role, message)
            VALUES (?, ?, ?, ?)
        ''', (order_id, sender_id, sender_role, message))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id
    
    def get_chat_messages(self, order_id: int, limit: int = 100, offset: int = 0) -> List[dict]:
        """Возвращает сообщения чата заказа"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM chat_messages
            WHERE order_id = ?
            ORDER BY created_at ASC
            LIMIT ? OFFSET ?
        ''', (order_id, limit, offset))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def set_order_offer(self, order_id: int, manager_id: int, price: float,
                        currency: str, delivery_days: int, comment: str,
                        status: str = 'sent') -> bool:
        """Устанавливает оферту по заказу"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE orders
            SET offer_price = ?, offer_currency = ?, offer_delivery_days = ?,
                offer_comment = ?, offer_status = ?, manager_id = COALESCE(manager_id, ?),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (price, currency, delivery_days, comment, status, manager_id, order_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def update_offer_status(self, order_id: int, status: str) -> bool:
        """Обновляет статус оферты"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE orders
            SET offer_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, order_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success