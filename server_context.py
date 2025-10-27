from pathlib import Path
from utils import get_main_file_path, read_all_quotes
from enum import IntEnum
from random_list import RandomList
from quotes import PersonQuotes
from discord.ext import commands
from datetime import datetime


SERVER_CONTEXT_PATH: Path = get_main_file_path().parent / 'server_contexts'


class Contexts(IntEnum):
    TRUTH_SOCIAL_CHANNEL_ID = 1
    QUOTES_CHANNEL_ID = 2
    QUOTES_PEOPLE = 3
    BIRTHDAYS = 4


class ServerContext:
    @staticmethod
    def __get_server_context_path(server_id: int, context: Contexts) -> Path:
        match context:
            case Contexts.TRUTH_SOCIAL_CHANNEL_ID:
                return SERVER_CONTEXT_PATH / str(server_id) / 'truth_social_channel_id'
            case Contexts.QUOTES_CHANNEL_ID:
                return SERVER_CONTEXT_PATH / str(server_id) / 'quotes_channel_id'
            case Contexts.QUOTES_PEOPLE:
                return SERVER_CONTEXT_PATH / str(server_id) / 'quotes_people'
            case Contexts.BIRTHDAYS:
                return SERVER_CONTEXT_PATH / str(server_id) / 'birthdays'
            case _:
                raise ValueError('Invalid context type')
            
    @staticmethod
    def __read_context_file(server_id: int, context: Contexts) -> str:
        path = ServerContext.__get_server_context_path(server_id, context)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            return ''  # Simulate empty file if it doesn't exist
        
    @staticmethod
    def __parse_birthdays(birthdays_str: str) -> dict[str, str]:
        birthdays = {}
        for line in birthdays_str.splitlines():
            if line.strip() == '':
                continue
            try:
                name, date_str = line.split(':', 1)
                dt = datetime.fromisoformat(date_str.strip())
                birthdays[name.strip()] = dt
            except ValueError:
                continue  # Skip malformed lines
        return birthdays

    def __init__(self, server_id: int, quotes: list[str]) -> None:
        self.server_id = server_id
        self.prefix = '>'  # TODO: make this configurable per-server

        try:
            self.truth_social_channel_id = int(
                ServerContext.__read_context_file(self.server_id, Contexts.TRUTH_SOCIAL_CHANNEL_ID)
            )
        except ValueError:
            self.truth_social_channel_id = None

        try:
            self.quotes_channel_id = int(
                ServerContext.__read_context_file(self.server_id, Contexts.QUOTES_CHANNEL_ID)
            )
        except ValueError:
            self.quotes_channel_id = None

        self.quotes_people = [
            line.strip()
            for line in ServerContext.__read_context_file(
                self.server_id, Contexts.QUOTES_PEOPLE
            ).splitlines()
            if line.strip() != ''
        ]
        self.quotes_list = RandomList(quotes)
        self.person_quotes = PersonQuotes(self.quotes_list, self.quotes_people)

        self.birthdays = ServerContext.__parse_birthdays(
            ServerContext.__read_context_file(self.server_id, Contexts.BIRTHDAYS)
        )

    @classmethod
    async def create(cls, server_id: int, client: commands.Bot) -> 'ServerContext':
        try:
            quotes_channel_id = int(cls.__read_context_file(server_id, Contexts.QUOTES_CHANNEL_ID))
            quotes = await read_all_quotes(client, server_id, quotes_channel_id)
        except ValueError:
            quotes = []

        return cls(server_id, quotes)

    server_id: int
    prefix: str
    truth_social_channel_id: int | None
    quotes_channel_id: int | None
    quotes_people: list[str] = []
    person_quotes: PersonQuotes
    quotes_list: RandomList
    birthdays: dict[str, str]
