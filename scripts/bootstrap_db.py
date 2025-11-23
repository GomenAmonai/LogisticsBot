#!/usr/bin/env python3
"""
Скрипт для подготовки тестовой/продовой базы данных.

Примеры:
    python scripts/bootstrap_db.py --reset --seed
    DATABASE_PATH=data/prod.db python scripts/bootstrap_db.py --seed
"""
import argparse
import os
from pathlib import Path

from config import DATABASE_PATH
from database import Database
from utils.test_data import seed_demo_data, clear_demo_data


def main():
    parser = argparse.ArgumentParser(description='Утилита подготовки базы данных')
    parser.add_argument('--reset', action='store_true', help='Удалить текущий файл БД перед созданием')
    parser.add_argument('--seed', action='store_true', help='Заполнить базу тестовыми данными')
    args = parser.parse_args()

    db_path = Path(DATABASE_PATH)
    if args.reset and db_path.exists():
        db_path.unlink()
        print(f'🗑️  Удален файл БД {db_path}')

    os.makedirs(db_path.parent, exist_ok=True)
    db = Database()

    if args.seed:
        clear_demo_data(db)
        summary = seed_demo_data(db)
        print(f"✅ Создано демо-данных: {summary}")

    print(f'✅ База данных готова: {db_path.resolve()}')


if __name__ == '__main__':
    main()

