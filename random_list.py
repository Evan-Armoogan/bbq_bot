import random

from typing import Any

class RandomList:
    def __init__(self, items: list[str] = []):
        self.items = items
        self.items_used = []
        self.SEQUENCE_LENGTH = max(1, len(items) // 2)
    
    def next(self) -> Any | None:
        if len(self.items) == 0:
            return None

        while True:
            rand_val = random.randint(0, len(self.items) - 1)
            if self.items[rand_val] not in self.items_used:
                if len(self.items_used) >= self.SEQUENCE_LENGTH:
                    self.items_used.pop(0)
                if len(self.items) > 1:
                    self.items_used.append(self.items[rand_val])
                return self.items[rand_val]

    def append(self, item: Any) -> None:
        self.items.append(item)
        self.SEQUENCE_LENGTH = max(1, len(self.items) // 2)

    items: list[Any]
    items_used: list[Any]
    SEQUENCE_LENGTH: int


def load_list(filename: str) -> RandomList:
    with open(filename, 'r', encoding='utf-8') as f:
        items = [line.strip() for line in f.readlines() if line.strip() != '']
    return RandomList(items=items)
