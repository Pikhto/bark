import os

from typing import Callable

import commands


class Option:
    def __init__(self, menu_option: str,
                 command: commands.Command,
                 prep_call: Callable | None = None) -> None:
        self.menu_option = menu_option
        self.command = command
        self.prep_call = prep_call

    def choose(self) -> None:
        data = self.prep_call() if self.prep_call else None
        message = self.command.execute(data) if data \
            else self.command.execute()
        print(message)

    def __str__(self) -> str:
        return self.menu_option


def print_option(option: dict[str, Option]) -> None:
    for shotcut, option in option.items():
        print(f'({shotcut}) {option}')
    print()


def option_choice_is_valid(choice: str, options: dict[str, Option]) -> bool:
    return choice in options or choice.upper() in options


def get_option_choice(options: dict[str, Option]) -> Option:
    user_input = input('Введите вариант действия: ')
    while not option_choice_is_valid(user_input, options):
        print('Такого варианта не существует!\n\nВведите команду из меню!\n')
        print_option(options)
        user_input = input('Введите вариант действия: ')
    return options[user_input.upper()]


def get_user_input(label: str, required: bool = True) -> str:
    value = input(f'{label}: ') or None
    while required and not value:
        value = input(f'{label}: ') or None
    return value


def get_new_bookmark_data() -> dict[str, Callable]:
    return {
        'title': get_user_input('Название'),
        'url': get_user_input('URL'),
        'notes': get_user_input('Примечания', required=False)
    }


def get_bookmarks_id_for_deletion():
    return get_user_input('Ввести идентификатор закладки для удаления')


def clear_screen() -> None:
    clear = 'cls' if os.name == 'nt' else 'clear'
    os.system(clear)


def loop() -> None:
    options = {
        'A': Option('Добавить закладку.',
                    commands.AddBookmarksCommand(),
                    prep_call=get_new_bookmark_data),
        'B': Option('Показать список закладок по дате.',
                    commands.ListBookmarksCommand()),
        'T': Option('Показать список закладок по заголовку.',
                    commands.ListBookmarksCommand(order_by='title')),
        'D': Option('Удалить закладку.',
                    commands.DeleteBookmarkCommand(),
                    prep_call=get_bookmarks_id_for_deletion),
        'Q': Option('Выйти.', commands.QuitCommand()),

        }

    clear_screen()
    print_option(options)

    chosen_option = get_option_choice(options)
    clear_screen()
    chosen_option.choose()

    _ = input('Нажмите ENTER для возврата в меню.')


if __name__ == '__main__':
    # print('Добро пожаловать в Bark!')
    # commands.CreateBookmarksTableCommand().execute()

    while True:
        loop()
