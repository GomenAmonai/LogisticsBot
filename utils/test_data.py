"""
Вспомогательные функции для подготовки/очистки тестовых данных.
"""
from models.user import UserRole

TEST_ADMIN_ID = 91001
TEST_MANAGER_ID = 92001
TEST_CLIENT_ID = 93001


def clear_demo_data(db):
    """Удаляет заказы, тикеты, чаты и связанные сущности (без затрагивания существующих пользователей)."""
    conn = db.get_connection()
    cursor = conn.cursor()
    tables = [
        'chat_messages',
        'tracking',
        'tickets',
        'payments',
        'orders',
        'user_data'
    ]
    for table in tables:
        cursor.execute(f'DELETE FROM {table}')
    conn.commit()
    conn.close()


def seed_demo_data(db):
    """Создает базовый набор данных (админ, менеджер, клиент, заказ)."""
    db.add_user(TEST_ADMIN_ID, username='demo_admin', first_name='DemoAdmin', role=UserRole.ADMIN)
    db.add_user(TEST_MANAGER_ID, username='demo_manager', first_name='DemoManager', role=UserRole.MANAGER)
    db.add_user(TEST_CLIENT_ID, username='demo_client', first_name='DemoClient', role=UserRole.CLIENT)

    order_id = db.create_order(
        client_id=TEST_CLIENT_ID,
        description='Демо-заказ для тестов',
        from_address='Москва, Тестовая 1',
        to_address='Санкт-Петербург, Проверочная 2',
        from_contact='Демо Клиент',
        to_contact='Получатель',
        weight=3.5,
        price=7500
    )

    db.assign_order_to_manager(order_id, TEST_MANAGER_ID)
    db.add_chat_message(order_id, TEST_CLIENT_ID, UserRole.CLIENT.value, 'Когда заберете?')
    db.add_chat_message(order_id, TEST_MANAGER_ID, UserRole.MANAGER.value, 'Сегодня вечером.')

    db.set_order_offer(order_id, TEST_MANAGER_ID, price=7800, currency='RUB', delivery_days=4, comment='Хрупкий груз')

    return {
        'admin_id': TEST_ADMIN_ID,
        'manager_id': TEST_MANAGER_ID,
        'client_id': TEST_CLIENT_ID,
        'order_id': order_id
    }

