import os
import sys
from importlib import reload

import pytest


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """
    Создает временную БД для каждого теста.
    Перезагружает модули config/database, чтобы они увидели новый путь.
    """
    db_path = tmp_path / 'test.db'
    monkeypatch.setenv('DATABASE_PATH', str(db_path))
    monkeypatch.setenv('SKIP_DOTENV', '1')
    monkeypatch.delenv('BOT_TOKEN', raising=False)
    monkeypatch.delenv('LOG_GROUP_ID', raising=False)

    # Перезагружаем config/database, чтобы они прочитали новые переменные
    if 'config' in sys.modules:
        reload(sys.modules['config'])
    else:
        import config  # noqa
    config = sys.modules['config']

    if 'database' in sys.modules:
        reload(sys.modules['database'])
    else:
        import database  # noqa
    database = sys.modules['database']

    db = database.Database()
    yield db

