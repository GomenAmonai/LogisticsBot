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
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import Database
from models.user import UserRole
from config import BOT_TOKEN

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)

db = Database()

# Настройка логирования для Flask
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.WARNING)
app_logger = logging.getLogger(__name__)


def verify_telegram_data(init_data: str) -> dict:
    """Проверяет данные от Telegram WebApp"""
    try:
        from urllib.parse import parse_qsl
        from config import BOT_TOKEN
        
        parsed_data = dict(parse_qsl(init_data))
        
        if 'hash' not in parsed_data:
            return None
        
        received_hash = parsed_data.pop('hash')
        
        # Создаем строку для проверки
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        # Создаем секретный ключ
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=BOT_TOKEN.encode(),
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
                <title>Логистическая платформа</title>
                <script src="https://telegram.org/js/telegram-web-app.js"></script>
            </head>
            <body style="font-family: Arial; padding: 40px; text-align: center; background: #0f172a; color: #f1f5f9;">
                <h1>🚚 Логистическая платформа</h1>
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
    
    return jsonify({
        'success': True,
        'user': {
            'id': user['user_id'],
            'name': user['first_name'],
            'role': user['role']
        }
    })


@app.route('/api/user', methods=['GET'])
def get_user():
    """Получает информацию о текущем пользователе"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user['user_id'],
        'username': user['username'],
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'role': user['role']
    })


@app.route('/api/orders', methods=['GET', 'POST'])
def orders():
    """Получает или создает заказы"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user(user_id)
    role = user['role']
    
    if request.method == 'GET':
        # Получаем заказы в зависимости от роли
        if role == UserRole.CLIENT:
            orders_list = db.get_user_orders(user_id, role)
        elif role == UserRole.MANAGER:
            orders_list = db.get_user_orders(user_id, role)
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
    app_logger.debug(f'Request: {request.method} {request.path}')


@app.after_request
def after_request(response):
    """Middleware после каждого запроса"""
    app_logger.debug(f'Response: {response.status_code} for {request.path}')
    return response


@app.route('/react')
def react_app():
    """Отдает React приложение"""
    return render_template('react_index.html')

if __name__ == '__main__':
    port = int(os.getenv('WEBAPP_PORT', os.getenv('PORT', 5000)))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    print(f"🚀 Запуск веб-приложения на {host}:{port}")
    app.run(host=host, port=port, debug=debug)

