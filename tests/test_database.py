from models.user import UserRole


def prepare_users(db):
    db.add_user(1, username='client', first_name='Client', role=UserRole.CLIENT)
    db.add_user(2, username='manager1', first_name='Manager1', role=UserRole.MANAGER)
    db.add_user(3, username='manager2', first_name='Manager2', role=UserRole.MANAGER)


def test_offer_conflict_locked_after_assignment(test_db):
    db = test_db
    prepare_users(db)

    order_id = db.create_order(
        client_id=1,
        description='Тестовый заказ',
        from_address='A',
        to_address='B',
        price=1000
    )

    assert db.set_order_offer(order_id, 2, 1200, 'RUB', 3, 'Комментарий')

    # Второй менеджер пытается отправить оферту в то же время
    assert not db.set_order_offer(order_id, 3, 1300, 'RUB', 2, 'Другая цена')

    order = db.get_order(order_id)
    assert order['manager_id'] == 2
    assert order['offer_price'] == 1200
    assert order['offer_delivery_days'] == 3


def test_chat_messages_roundtrip(test_db):
    db = test_db
    prepare_users(db)
    order_id = db.create_order(client_id=1, description='Чат', from_address='A', to_address='B')
    db.assign_order_to_manager(order_id, 2)

    db.add_chat_message(order_id, 1, UserRole.CLIENT.value, 'Привет!')
    db.add_chat_message(order_id, 2, UserRole.MANAGER.value, 'Здравствуйте!')

    messages = db.get_chat_messages(order_id)
    assert len(messages) == 2
    assert messages[0]['sender_role'] == UserRole.CLIENT.value
    assert messages[1]['sender_role'] == UserRole.MANAGER.value
    assert messages[0]['message'] == 'Привет!'

