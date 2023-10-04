import datetime
import sys

from typing import Any, Protocol

import requests

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
    def execute(self,
                data: dict[str, str],
                timestamp: str | None = None) -> str:
        if timestamp is None:
            timestamp = datetime.datetime.utcnow().isoformat()
        data['date_added'] = timestamp
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


class ImportGitHubStarsCommand:
    def _extract_bookmark_info(self, repo: dict[str, str]) -> dict[str, str]:
        return {
            'title': repo['name'],
            'url': repo['html_url'],
            'notes': repo['description'],
        }

    def execute(self, data):
        bookmarks_imported = 0

        github_username = data['github_username']
        next_page_of_results = f'https://api.github.com/users/{github_username}/starred'
        headers = {
                'Accept': 'application/vnd.github.v3.star+json'
            }

        while next_page_of_results:
            stars_response = requests.get(next_page_of_results,
                                          headers=headers)

            next_page = stars_response.links.get('next', {})
            next_page_of_results = next_page.get('url')

            for repo_info in stars_response.json():
                repo = repo_info['repo']
                if data['preserve_timestamp']:
                    timestamp = datetime.datetime.strptime(
                        repo_info['starred_at'],
                        '%Y-%m-%dT%H:%M:%SZ'
                        )
                else:
                    timestamp = None
                bookmarks_imported += 1

                AddBookmarksCommand().execute(
                    self._extract_bookmark_info(repo),
                    timestamp=timestamp
                    )
        return f'Импортировано {bookmarks_imported} закладок, '\
            'из помеченных звёздами репо'
