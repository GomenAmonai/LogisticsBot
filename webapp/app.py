#!/usr/bin/env python3
"""
Flask веб-приложение для логистической платформы
"""
import os
import sys
import hmac
import hashlib
import json
import logging
from datetime import datetime
from uuid import uuid4
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flasgger import Swagger
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import Database
from models.user import UserRole
import config
from utils.test_data import seed_demo_data, clear_demo_data

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)
swagger = Swagger(app)

_db = Database()


class DatabaseProxy:
    def __getattr__(self, item):
        target = app.config.get('DB_INSTANCE') or _db
        return getattr(target, item)


db = DatabaseProxy()

# Настройка логирования для Flask
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.WARNING)
app_logger = logging.getLogger(__name__)


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    stored_token = db.get_active_session_token(user_id)
    session_token = session.get('session_token')
    if not stored_token or stored_token != session_token:
        session.clear()
        return None
    return db.get_user(user_id)


def user_can_access_order(user: dict, order: dict) -> bool:
    """Проверяет, может ли пользователь получить доступ к заказу"""
    if not user or not order:
        return False
    role = user.get('role')
    user_id = user.get('user_id')
    if role == UserRole.ADMIN:
        return True
    if role == UserRole.CLIENT and order.get('client_id') == user_id:
        return True
    if role == UserRole.MANAGER and order.get('manager_id') == user_id:
        return True
    return False


def require_admin():
    user = get_current_user()
    if not user or user['role'] != UserRole.ADMIN:
        return None, jsonify({'error': 'Admin access required'}), 403
    return user, None, None


def has_test_token():
    auth_header = request.headers.get('Authorization', '')
    token_value = getattr(config, 'TEST_API_TOKEN', '')
    if not token_value:
        return False
    if not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ', 1)[1].strip()
    return token == token_value


def ensure_admin_or_token():
    if has_test_token():
        return True
    user = get_current_user()
    return bool(user and user['role'] == UserRole.ADMIN)


def verify_telegram_data(init_data: str) -> dict:
    """Проверяет данные от Telegram WebApp"""
    try:
        from urllib.parse import parse_qsl
        
        parsed_data = dict(parse_qsl(init_data))
        
        if 'hash' not in parsed_data:
            return None
        
        received_hash = parsed_data.pop('hash')
        
        # Создаем строку для проверки
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        # Создаем секретный ключ
        bot_token = getattr(config, 'BOT_TOKEN', '')
        if not bot_token:
            return None
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        if calculated_hash != received_hash:
            return None
        
        # Парсим user данные
        if 'user' in parsed_data:
            user_data = json.loads(parsed_data['user'])
            return user_data
        
        return None
    except Exception as e:
        print(f"Ошибка проверки Telegram данных: {e}")
        return None


@app.route('/')
def index():
    """Главная страница - React приложение"""
    # Проверяем, есть ли собранное React приложение
    react_build_path = Path(__file__).parent / 'static' / 'react' / 'index.html'
    if react_build_path.exists():
        # Используем собранный index.html от Vite
        with open(react_build_path, 'r', encoding='utf-8') as f:
            html = f.read()
        # Заменяем пути на статические файлы Flask
        # Сначала общая замена (чтобы избежать двойной замены)
        html = html.replace('href="/', 'href="/static/react/')
        html = html.replace('src="/', 'src="/static/react/')
        return html
    else:
        # Если React не собран, показываем сообщение
        return """
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Платформа доставки</title>
                <script src="https://telegram.org/js/telegram-web-app.js"></script>
            </head>
            <body style="font-family: Arial; padding: 40px; text-align: center; background: #0f172a; color: #f1f5f9;">
                <h1>🚚 Платформа доставки</h1>
                <p>React приложение не собрано.</p>
                <p>Запустите: <code style="background: #1e293b; padding: 10px; border-radius: 8px; display: block; margin: 20px auto; max-width: 500px;">cd webapp/react-app && npm install && npm run build</code></p>
                <p>Или используйте скрипт: <code style="background: #1e293b; padding: 10px; border-radius: 8px;">./build_react.sh</code></p>
            </body>
        </html>
        """


@app.route('/auth', methods=['POST'])
def auth():
    """Аутентификация через Telegram WebApp"""
    data = request.json
    init_data = data.get('initData', '')
    
    user_data = verify_telegram_data(init_data)
    
    if not user_data:
        return jsonify({'error': 'Invalid Telegram data'}), 401
    
    user_id = user_data.get('id')
    
    # Получаем или создаем пользователя
    user = db.get_user(user_id)
    if not user:
        db.add_user(
            user_id=user_id,
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name')
        )
        user = db.get_user(user_id)
    
    # Сохраняем в сессию
    session['user_id'] = user_id
    session['user_role'] = user['role']
    session['user_name'] = user['first_name']
    session_token = str(uuid4())
    session['session_token'] = session_token
    db.set_active_session(user_id, session_token)

    app_logger.info("Auth success: user_id=%s role=%s", user_id, user['role'])
    
    return jsonify({
        'success': True,
        'user': {
            'id': user['user_id'],
            'name': user['first_name'],
            'role': user['role']
        }
    })


@app.route('/auth/logout', methods=['POST'])
def logout():
    """Очищает серверную сессию
    ---
    responses:
      200:
        description: Session cleared
    """
    user_id = session.get('user_id')
    if user_id:
        db.clear_active_session(user_id)
    session.clear()
    return jsonify({'success': True})


@app.route('/api/user', methods=['GET', 'PUT'])
def user():
    """Получает или обновляет информацию о текущем пользователе"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if request.method == 'GET':
        user = db.get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Получаем дополнительные данные из user_data
        phone = db.get_user_data(user_id, 'phone') or ''
        email = db.get_user_data(user_id, 'email') or ''
        
        return jsonify({
            'id': user['user_id'],
            'user_id': user['user_id'],
            'username': user['username'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'role': user['role'],
            'phone': phone,
            'email': email,
            'notifications_enabled': user.get('notifications_enabled', False)
        })
    
    elif request.method == 'PUT':
        data = request.json
        user = db.get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Обновляем основные данные
        db.add_user(
            user_id=user_id,
            username=data.get('username', user.get('username')),
            first_name=data.get('first_name', user.get('first_name')),
            last_name=data.get('last_name', user.get('last_name')),
            role=user.get('role', 'client')
        )
        
        # Сохраняем дополнительные данные
        if 'phone' in data:
            db.save_user_data(user_id, 'phone', data['phone'])
        if 'email' in data:
            db.save_user_data(user_id, 'email', data['email'])
        
        # Обновляем настройки уведомлений
        if 'notifications_enabled' in data:
            db.set_notifications_enabled(user_id, data['notifications_enabled'])
        
        return jsonify({'success': True, 'message': 'Profile updated'})


@app.route('/api/orders', methods=['GET', 'POST'])
def orders():
    """Получает или создает заказы"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    role = user['role']
    order_type = request.args.get('type')
    
    if request.method == 'GET':
        # Получаем заказы в зависимости от роли
        if role == UserRole.CLIENT:
            orders_list = db.get_user_orders(user_id, role)
        elif role == UserRole.MANAGER:
            if order_type == 'incoming':
                orders_list = db.get_incoming_orders()
            elif order_type in ('assigned', 'my', 'mine'):
                orders_list = db.get_manager_assigned_orders(user_id)
            else:
                orders_list = db.get_manager_assigned_orders(user_id)
        else:  # ADMIN
            orders_list = db.get_user_orders(0, role)
        
        return jsonify({'orders': orders_list})
    
    elif request.method == 'POST':
        # Создание заказа (только для клиентов)
        if role != UserRole.CLIENT:
            return jsonify({'error': 'Only clients can create orders'}), 403
        
        data = request.json
        order_id = db.create_order(
            client_id=user_id,
            description=data.get('description'),
            from_address=data.get('from_address'),
            to_address=data.get('to_address'),
            from_contact=data.get('from_contact'),
            to_contact=data.get('to_contact'),
            weight=float(data.get('weight', 0)),
            price=float(data.get('price', 0))
        )
        
        # Автоматически создаем тикет для первого доступного менеджера
        managers = db.get_all_users(role=UserRole.MANAGER)
        if managers:
            # Назначаем первому менеджеру
            db.assign_order_to_manager(order_id, managers[0]['user_id'])
        
        order = db.get_order(order_id)
        
        # Уведомление о заказе уже отправлено в database.create_order
        
        return jsonify({'success': True, 'order': dict(order)}), 201


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Получает информацию о заказе"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    user = db.get_user(user_id)
    # Проверяем права доступа
    if user['role'] == UserRole.CLIENT and order['client_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Добавляем отслеживание
    tracking = db.get_order_tracking(order_id)
    order['tracking'] = tracking
    
    return jsonify({'order': dict(order)})


@app.route('/api/orders/<int:order_id>/assign', methods=['POST'])
def assign_order(order_id):
    """Назначает заказ менеджеру"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    if user['role'] != UserRole.MANAGER:
        return jsonify({'error': 'Only managers can assign orders'}), 403
    
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if order.get('manager_id') and order['manager_id'] != user_id:
        return jsonify({'error': 'Order already assigned'}), 400
    
    db.assign_order_to_manager(order_id, user_id)
    db.update_order_status(order_id, 'accepted', user_id)
    
    return jsonify({'success': True})


@app.route('/api/chat/<int:order_id>', methods=['GET'])
def get_chat(order_id):
    """Возвращает сообщения чата по заказу"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if not user_can_access_order(user, order):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        limit = min(int(request.args.get('limit', 100)), 200)
        offset = max(int(request.args.get('offset', 0)), 0)
    except ValueError:
        return jsonify({'error': 'Invalid pagination params'}), 400
    
    messages = db.get_chat_messages(order_id, limit=limit, offset=offset)
    return jsonify({'order': order, 'messages': messages})


@app.route('/api/chat/<int:order_id>/send', methods=['POST'])
def send_chat_message(order_id):
    """Отправляет сообщение в чат заказа"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if not user_can_access_order(user, order):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    if len(message) > 2000:
        return jsonify({'error': 'Message is too long'}), 400
    
    db.add_chat_message(order_id, user_id, user['role'], message)
    
    return jsonify({'success': True})


@app.route('/api/orders/<int:order_id>/offer', methods=['POST'])
def create_order_offer(order_id):
    """Создает или обновляет оферту для заказа"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    if user['role'] not in [UserRole.MANAGER, UserRole.ADMIN]:
        return jsonify({'error': 'Only managers can send offers'}), 403
    
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if user['role'] == UserRole.MANAGER and order.get('manager_id') not in (None, user_id):
        return jsonify({'error': 'Order assigned to another manager'}), 403
    
    data = request.json or {}
    try:
        price = float(data.get('offer_price') or data.get('price'))
        delivery_days = int(data.get('offer_delivery_days') or data.get('delivery_days'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Offer price and delivery days are required'}), 400
    
    currency = (data.get('offer_currency') or data.get('currency') or 'RUB').upper()
    comment = data.get('offer_comment') or data.get('comment') or ''
    
    if price <= 0 or delivery_days <= 0:
        return jsonify({'error': 'Offer values must be positive'}), 400
    
    success = db.set_order_offer(
        order_id=order_id,
        manager_id=user_id,
        price=price,
        currency=currency,
        delivery_days=delivery_days,
        comment=comment,
        status='sent'
    )
    
    if not success:
        return jsonify({'error': 'Order already assigned to another manager'}), 409
    
    updated_order = db.get_order(order_id)
    return jsonify({'success': True, 'order': updated_order})


@app.route('/api/orders/<int:order_id>/accept-offer', methods=['POST'])
def accept_order_offer(order_id):
    """Принимает или отклоняет оферту"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if user['role'] == UserRole.CLIENT and order.get('client_id') != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if user['role'] not in [UserRole.CLIENT, UserRole.ADMIN]:
        return jsonify({'error': 'Only clients can accept offers'}), 403
    
    data = request.json or {}
    decision = (data.get('decision') or 'accept').lower()
    status = 'accepted' if decision == 'accept' else 'rejected'
    
    success = db.update_offer_status(order_id, status)
    if not success:
        return jsonify({'error': 'Failed to update offer status'}), 500
    
    return jsonify({'success': True, 'offer_status': status})


@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Обновляет статус заказа"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    order = db.get_order(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Проверяем права (только менеджер или админ)
    if user['role'] not in [UserRole.MANAGER, UserRole.ADMIN]:
        return jsonify({'error': 'Access denied'}), 403
    
    if user['role'] == UserRole.MANAGER and order['manager_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    status = data.get('status')
    
    if db.update_order_status(order_id, status, user_id if user['role'] == UserRole.MANAGER else None):
        order = db.get_order(order_id)
        return jsonify({'success': True, 'order': dict(order)})
    
    return jsonify({'error': 'Failed to update status'}), 500


@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Получает тикеты менеджера"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    if user['role'] != UserRole.MANAGER:
        return jsonify({'error': 'Only managers can view tickets'}), 403
    
    status = request.args.get('status')
    tickets = db.get_manager_tickets(user_id, status)
    
    return jsonify({'tickets': tickets})


@app.route('/api/tickets/<int:ticket_id>/accept', methods=['POST'])
def accept_ticket(ticket_id):
    """Принимает тикет"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    if user['role'] != UserRole.MANAGER:
        return jsonify({'error': 'Only managers can accept tickets'}), 403
    
    if db.accept_ticket(ticket_id):
        return jsonify({'success': True})
    
    return jsonify({'error': 'Failed to accept ticket'}), 500


@app.route('/api/orders/<int:order_id>/tracking', methods=['GET'])
def get_tracking(order_id):
    """Получает историю отслеживания заказа"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    user = db.get_user(user_id)
    # Проверяем права доступа
    if user['role'] == UserRole.CLIENT and order['client_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    tracking = db.get_order_tracking(order_id)
    return jsonify({'tracking': tracking})


@app.route('/api/orders/<int:order_id>/contact-logist', methods=['POST'])
def contact_logist(order_id):
    """Создает тикет для связи клиента с менеджером"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    user = db.get_user(user_id)
    if user['role'] != UserRole.CLIENT or order['client_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Получаем менеджера заказа или первого доступного
    manager_id = order.get('manager_id')
    if not manager_id:
        managers = db.get_all_users(role=UserRole.MANAGER)
        if not managers:
            return jsonify({'error': 'No managers available'}), 404
        manager_id = managers[0]['user_id']
    
    # Создаем тикет для связи
    ticket_id = db.create_ticket(order_id, manager_id)
    
    # Отправляем уведомление в группу
    try:
        from utils.telegram_logger import send_log_sync, format_ticket_notification, init_log_group
        from config import LOG_GROUP_ID
        
        if LOG_GROUP_ID:
            init_log_group(LOG_GROUP_ID)
            ticket_data = {
                'id': ticket_id,
                'order_id': order_id,
                'client_id': user_id,
                'manager_id': manager_id,
                'description': f'Клиент запросил связь по заказу #{order_id}',
                'status': 'new'
            }
            message = format_ticket_notification(ticket_data)
            send_log_sync(message, parse_mode='HTML')
    except Exception as e:
        import logging
        logging.error(f"Ошибка отправки уведомления о тикете: {e}")
    
    return jsonify({
        'success': True,
        'ticket_id': ticket_id,
        'message': 'Ticket created. Manager will contact you soon.'
    })


@app.route('/api/admin/test/bootstrap', methods=['POST'])
def admin_bootstrap_data():
    """
    Создает демо-данные
    ---
    responses:
      200:
        description: OK
    """
    if not ensure_admin_or_token():
        return jsonify({'error': 'Admin access required'}), 403
    
    clear_demo_data(db)
    summary = seed_demo_data(db)
    return jsonify({'success': True, 'data': summary})


@app.route('/api/admin/test/clear', methods=['POST'])
def admin_clear_data():
    """
    Очищает демо-данные
    ---
    responses:
      200:
        description: OK
    """
    if not ensure_admin_or_token():
        return jsonify({'error': 'Admin access required'}), 403
    
    clear_demo_data(db)
    return jsonify({'success': True})


@app.route('/api/admin/test/create-user', methods=['POST'])
def admin_create_test_user():
    """
    Создает тестового пользователя
    ---
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            user_id:
              type: integer
            username:
              type: string
            first_name:
              type: string
            role:
              type: string
    responses:
      200:
        description: OK
    """
    if not ensure_admin_or_token():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json or {}
    role = data.get('role', UserRole.CLIENT)
    if role not in [UserRole.CLIENT, UserRole.MANAGER, UserRole.ADMIN]:
        return jsonify({'error': 'Invalid role'}), 400
    
    user_id_value = data.get('user_id')
    if user_id_value:
        try:
            user_id = int(user_id_value)
        except ValueError:
            return jsonify({'error': 'user_id must be numeric'}), 400
    else:
        user_id = int(str(uuid4().int)[-9:])
    
    db.add_user(
        user_id=user_id,
        username=data.get('username'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role=role
    )
    
    return jsonify({'success': True, 'user_id': user_id, 'role': role})


@app.route('/api/admin/test/user/<int:target_user_id>', methods=['GET'])
def admin_get_user(target_user_id):
    """
    Возвращает информацию о пользователе
    ---
    parameters:
      - name: target_user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: OK
    """
    if not ensure_admin_or_token():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = db.get_user(target_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user})


@app.route('/api/admin/test/set-role', methods=['POST'])
def admin_set_role():
    """
    Устанавливает роль пользователю
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
            role:
              type: string
              enum: ['client', 'manager', 'admin']
    responses:
      200:
        description: OK
    """
    if not ensure_admin_or_token():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json or {}
    try:
        target_user_id = int(data.get('user_id'))
    except (TypeError, ValueError):
        return jsonify({'error': 'user_id must be numeric'}), 400
    
    new_role = (data.get('role') or '').lower()
    if new_role not in [UserRole.CLIENT, UserRole.MANAGER, UserRole.ADMIN]:
        return jsonify({'error': 'Invalid role'}), 400
    
    target_user = db.get_user(target_user_id)
    if not target_user:
        db.add_user(
            user_id=target_user_id,
            role=new_role
        )
    else:
        db.set_user_role(target_user_id, new_role)
        # Очистим активную сессию, чтобы новое значение подхватилось
        db.clear_active_session(target_user_id)
    
    return jsonify({'success': True, 'user_id': target_user_id, 'role': new_role})


@app.route('/api/payments', methods=['POST'])
def create_payment():
    """Создает платеж"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    order_id = data.get('order_id')
    amount = float(data.get('amount', 0))
    payment_method = data.get('payment_method', 'card')
    
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    user = db.get_user(user_id)
    if user['role'] == UserRole.CLIENT and order['client_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    payment_id = db.create_payment(order_id, amount, payment_method)
    
    return jsonify({
        'success': True,
        'payment_id': payment_id,
        'message': 'Payment created. In production, redirect to payment gateway.'
    })


@app.route('/api/payments/<int:payment_id>/complete', methods=['POST'])
def complete_payment(payment_id):
    """Завершает платеж (для тестирования)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    if user['role'] not in [UserRole.ADMIN, UserRole.MANAGER]:
        return jsonify({'error': 'Access denied'}), 403
    
    if db.complete_payment(payment_id):
        return jsonify({'success': True})
    
    return jsonify({'error': 'Failed to complete payment'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получает статистику"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    
    if user['role'] == UserRole.CLIENT:
        orders = db.get_user_orders(user_id, user['role'])
        stats = {
            'total_orders': len(orders),
            'pending': len([o for o in orders if o['status'] == 'pending']),
            'in_transit': len([o for o in orders if o['status'] == 'in_transit']),
            'delivered': len([o for o in orders if o['status'] == 'delivered'])
        }
    elif user['role'] == UserRole.MANAGER:
        tickets = db.get_manager_tickets(user_id)
        orders = db.get_user_orders(user_id, user['role'])
        stats = {
            'total_tickets': len(tickets),
            'new_tickets': len([t for t in tickets if t['status'] == 'new']),
            'total_orders': len(orders),
            'in_progress': len([o for o in orders if o['status'] == 'in_transit'])
        }
    else:  # ADMIN
        all_orders = db.get_user_orders(0, user['role'])
        all_users = db.get_all_users()
        stats = {
            'total_orders': len(all_orders),
            'total_users': len(all_users),
            'pending_orders': len([o for o in all_orders if o['status'] == 'pending'])
        }
    
    return jsonify({'stats': stats})


# Обработчики ошибок Flask
@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибок"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибок"""
    app_logger.error(f'Server Error: {error}', exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Обработка всех необработанных исключений"""
    app_logger.error(f'Unhandled exception: {error}', exc_info=True)
    return jsonify({'error': 'An error occurred'}), 500


@app.before_request
def before_request():
    """Middleware перед каждым запросом"""
    import time
    request._start_time = time.time()  # Сохраняем время начала запроса
    app_logger.debug(f'Request: {request.method} {request.path}')


@app.after_request
def after_request(response):
    """Middleware после каждого запроса"""
    import time
    from utils.telegram_logger import send_log_sync, format_api_log, init_log_group
    from config import LOG_GROUP_ID
    
    # Инициализируем группу для логов если нужно
    if LOG_GROUP_ID and not hasattr(app, '_log_group_init'):
        init_log_group(LOG_GROUP_ID)
        app._log_group_init = True
    
    # Логируем API запросы в группу (только важные)
    if LOG_GROUP_ID:
        # Логируем только ошибки и важные запросы
        if response.status_code >= 400 or request.path.startswith('/api/'):
            duration = getattr(request, '_start_time', 0)
            if hasattr(request, '_start_time'):
                duration = (time.time() - request._start_time) * 1000
            else:
                duration = 0
            
            user_id = session.get('user_id') if hasattr(session, 'get') else None
            log_message = format_api_log(
                request.method,
                request.path,
                response.status_code,
                duration,
                user_id
            )
            send_log_sync(log_message, parse_mode='HTML')
    
    app_logger.debug(f'Response: {response.status_code} for {request.path}')
    return response


@app.route('/react')
def react_app():
    """Отдает React приложение"""
    return render_template('react_index.html')

if __name__ == '__main__':
    # Railway использует переменную PORT
    port = int(os.getenv('PORT', os.getenv('WEBAPP_PORT', 5000)))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    print(f"🚀 Запуск веб-приложения на {host}:{port}")
    app.run(host=host, port=port, debug=debug)

