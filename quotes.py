from random_list import RandomList
from typing import Any

class PersonQuotes:
    @staticmethod
    def __name_in_str(name: str, quote: str) -> str:
        return (f'{name}:' in quote or
                f'-{name}' in quote or
                f'- {name}' in quote)

    def __init__(self, all_quotes: RandomList, people: list[str]) -> None:
        attr = [name.lower().replace(' ', '_') for name in people]
        for a in attr:
            name = ' '.join([a.capitalize() for a in a.split('_')])
            setattr(self, a, RandomList([quote for quote in all_quotes.items if self.__name_in_str(name, quote[0])]))

    def get_quote(self, person: str) -> Any | None:
        attr = person.lower().replace(' ', '_')
        if attr in self.__dict__:
            quote_list: RandomList = getattr(self, attr)
            return quote_list.next()
        return None

    def append(self, quote: Any) -> None:
        for attr in self.__dict__:
            if self.__name_in_str(attr.replace('_', ' ').title(), quote[0]):
                quote_list: RandomList = getattr(self, attr)
                quote_list.append(quote)
                setattr(self, attr, quote_list)
