import json

import pytest

from webapp.app import app
from utils.test_data import seed_demo_data, clear_demo_data, TEST_CLIENT_ID
import config


@pytest.fixture
def client(test_db):
    clear_demo_data(test_db)
    seed_demo_data(test_db)
    app.config['DB_INSTANCE'] = test_db
    with app.test_client() as client_ctx:
        yield client_ctx
    app.config.pop('DB_INSTANCE', None)


def test_admin_set_role_with_token(client, monkeypatch):
    monkeypatch.setenv('TEST_API_TOKEN', 'secret')
    config.TEST_API_TOKEN = 'secret'

    response = client.post(
        '/api/admin/test/set-role',
        data=json.dumps({'user_id': TEST_CLIENT_ID, 'role': 'admin'}),
        content_type='application/json',
        headers={'Authorization': 'Bearer secret'}
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['role'] == 'admin'

