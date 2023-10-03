import datetime
import sys

from typing import Any, Protocol

from database import DataBaseManager


db = DataBaseManager('bookmarks.db')


class Command(Protocol):
    def execute(self) -> None:
        ...


class CreateBookmarksTableCommand:
    def execute(self) -> None:
        db.create_table('bookmarks',
                        {
                            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                            'title': 'TEXT NOT NULL',
                            'url': 'TEXT NOT NULL',
                            'notes': 'TEXT',
                            'date_added': 'TEXT NOT NULL',
                        })


class AddBookmarksCommand:
    def execute(self, data: dict[str, str]) -> str:
        data['date_added'] = datetime.datetime.utcnow().isoformat()
        db.add('bookmarks', data)
        return 'Закладка добавлена!'


class ListBookmarksCommand:
    def __init__(self, order_by='date_added') -> None:
        self.order_by = order_by

    def execute(self) -> list[Any]:
        select = db.select('bookmarks', order_by=self.order_by)
        return select.fetchall()


class DeleteBookmarkCommand:
    def execute(self, data: dict[str, str]) -> str:
        db.delete('bookmarks', {'id': data})
        return 'Закладка удалена!'


class QuitCommand:
    def execute(self) -> None:
        sys.exit()
