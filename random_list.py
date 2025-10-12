import random

from typing import Any

class RandomList:
    SEQUENCE_LENGTH = 10

    def __init__(self, items: list = []):
        self.items = items
        self.items_used = []
    
    def next(self) -> Any:
        while True:
            rand_val = random.randint(0, len(self.items) - 1)
            if self.items[rand_val] not in self.items_used:
                if len(self.items_used) >= RandomList.SEQUENCE_LENGTH:
                    self.items_used.pop(0)
                self.items_used.append(self.items[rand_val])
                return self.items[rand_val]

    items: list[Any]
    items_used: list[Any]


def load_list(filename: str) -> RandomList:
    with open(filename, 'r', encoding='utf-8') as f:
        items = [line.strip() for line in f.readlines() if line.strip() != '']
    return RandomList(items=items)
