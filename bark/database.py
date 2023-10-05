import sqlite3
from sqlite3 import Cursor
from typing import Any


class DataBaseManager:
    def __init__(self, db_file: str) -> None:
        self.connect = sqlite3.connect(db_file)

    def __del__(self) -> None:
        self.connect.close()

    def _execute(self, statement: str, values: Any = None) -> Cursor:
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute(statement, values or [])
            return cursor

    def create_table(self, table_name: str, columns: dict[str, str]) -> None:
        columns_with_types = [
            f'{column_name} {data_type}'
            for column_name, data_type in columns.items()
        ]

        stm = f'''
              CREATE TABLE IF NOT EXISTS {table_name}
              ({', '.join(columns_with_types)});
              '''

        self._execute(stm)

    def add(self, table_name: str, data: dict[str, str]) -> None:
        placeholders: str = ', '.join(('?' * len(data)))
        column: str = ', '.join(data.keys())
        column_values: tuple[str] = tuple(data.values())

        stm = f'''
              INSERT INTO {table_name}
              ({column})
              VALUES ({placeholders});
              '''

        self._execute(stm, column_values)

    def delete(self, table_name: str, criteria: dict[str, str]) -> None:
        placeholders = [f'{column} = ?' for column in criteria.keys()]
        delete_criteria = ' AND '.join(placeholders)
        crt = tuple(criteria.values())

        stm = f'''
              DELETE FROM {table_name}
              WHERE {delete_criteria};
              '''

        self._execute(stm, crt)

    def select(self, table_name: str,
               criteria: dict[str, str] | None = None,
               order_by: str | None = None) -> Cursor:
        criteria = criteria or {}
        query = f'SELECT * FROM {table_name}'

        if criteria:
            placeholders: str = [f'{column} = ?' for column in criteria.keys()]
            select_criteria = ' AND '.join(placeholders)
            query += f' WHERE {select_criteria}'

        order = order_by or 'id'
        query += f' ORDER BY {order};'

        return self._execute(query, tuple(criteria.values()))

    def update(self, table_name: str,
               fields: dict[str, str],
               criteria: dict[str, str]) -> None:
        placeholders = ', '.join([f'{col} = ?' for col in fields.keys()])
        update_criteria = ', '.join([f'{col} = ?' for col in criteria.keys()])
        stm = f'''
        UPDATE {table_name}
        SET {placeholders}
        WHERE {update_criteria};'''

        self._execute(stm, tuple(fields.values()) + tuple(criteria.values()))
