from pathlib import Path
from utils import get_main_file_path
from quotes import read_all_quotes
from enum import IntEnum
from random_list import RandomList
from quotes import PersonQuotes
from discord.ext import commands
from datetime import datetime
from prefix import PREFIX, VALID_PREFIXES


SERVER_CONTEXT_PATH: Path = get_main_file_path().parent / 'server_contexts'


class Contexts(IntEnum):
    TRUTH_SOCIAL_CHANNEL_ID = 1
    QUOTES_CHANNEL_ID = 2
    QUOTES_PEOPLE = 3
    BIRTHDAYS = 4
    PREFIX = 5


class UpdateSettings(IntEnum):
    BIRTHDAY_ADD = 1
    BIRTHDAY_REMOVE = 2
    QUOTE_PERSON_ADD = 3
    QUOTE_PERSON_REMOVE = 4
    QUOTE_CHANNEL_SET = 5
    TRUTH_CHANNEL_SET = 6
    QUOTE_CHANNEL_REMOVE = 7
    TRUTH_CHANNEL_REMOVE = 8
    PREFIX_UPDATE = 9


class ServerContext:
    @staticmethod
    def __get_server_context_path(server_id: int, context: Contexts) -> Path:
        path = None
        match context:
            case Contexts.TRUTH_SOCIAL_CHANNEL_ID:
                path = SERVER_CONTEXT_PATH / str(server_id) / 'truth_social_channel_id'
            case Contexts.QUOTES_CHANNEL_ID:
                path = SERVER_CONTEXT_PATH / str(server_id) / 'quotes_channel_id'
            case Contexts.QUOTES_PEOPLE:
                path = SERVER_CONTEXT_PATH / str(server_id) / 'quotes_people'
            case Contexts.BIRTHDAYS:
                path = SERVER_CONTEXT_PATH / str(server_id) / 'birthdays'
            case Contexts.PREFIX:
                path = SERVER_CONTEXT_PATH / str(server_id) / 'prefix'
            case _:
                raise ValueError('Invalid context type')
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
            
    @staticmethod
    def __read_context_file(server_id: int, context: Contexts) -> str:
        path = ServerContext.__get_server_context_path(server_id, context)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            return ''  # Simulate empty file if it doesn't exist
        
    @staticmethod
    def __parse_birthdays(birthdays_str: str) -> dict[str, datetime]:
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

        prefix_file = ServerContext.__read_context_file(self.server_id, Contexts.PREFIX)
        if len(prefix_file) != 1:
            self.prefix = PREFIX
        else:
            self.prefix = prefix_file

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
    
    def rewrite_date_file(self) -> None:
        path = ServerContext.__get_server_context_path(self.server_id, Contexts.BIRTHDAYS)
        with open(path, 'w', encoding='utf-8') as f:
            for person, date in self.birthdays.items():
                f.write(f'{person}: {date.date().isoformat()}\n')
    
    def update_birthday(self, name: str, dt: datetime) -> None:
        self.birthdays[name] = dt
        self.rewrite_date_file()

    def remove_birthday(self, name: str) -> None:
        if name in self.birthdays:
            del self.birthdays[name]
            self.rewrite_date_file()

    def rewrite_quotes_file(self) -> None:
        path = ServerContext.__get_server_context_path(self.server_id, Contexts.QUOTES_PEOPLE)
        with open(path, 'w', encoding='utf-8') as f:
            for person in self.quotes_people:
                f.write(f'{person}\n')

    def update_quotes_people(self, name: str) -> None:
        if name not in self.quotes_people:
            self.quotes_people.append(name)
            self.rewrite_quotes_file()
            self.person_quotes.insert_person(name, self.quotes_list)

    def remove_quotes_people(self, name: str) -> None:
        if name in self.quotes_people:
            self.quotes_people.remove(name)
            self.rewrite_quotes_file()
            attr = name.lower().replace(' ', '_')
            if attr in self.person_quotes.__dict__:
                delattr(self.person_quotes, attr)

    def update_prefix(self, new_prefix: str) -> None:
        self.prefix = new_prefix
        path = ServerContext.__get_server_context_path(self.server_id, Contexts.PREFIX)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_prefix)

    async def update_settings(self, ctx: commands.Context, *args: str) -> None:
        try:
            setting = UpdateSettings[args[0].strip().upper()]
        except KeyError:
            valid_settings = ', '.join([s.name.lower() for s in UpdateSettings])
            await ctx.send(f'Error: Invalid setting name "{args[0]}". Valid settings are: {valid_settings}')
            return
        match setting:
            case UpdateSettings.BIRTHDAY_ADD:
                if len(args) < 5:
                    await ctx.send('Usage: >settings birthday_add <name> <year> <month> <day>')
                    return
                name = args[1]
                try:
                    year = int(args[2])
                    month = int(args[3])
                    day = int(args[4])
                    dt = datetime(year, month, day)
                except ValueError:
                    await ctx.send('Error: Invalid date format. Please provide valid integers for year, month, and day.')
                    return
                
                self.update_birthday(name, dt)
                await ctx.send(f'Birthday for {name} added/updated to {dt.date().isoformat()}.')

            case UpdateSettings.BIRTHDAY_REMOVE:
                if len(args) < 2:
                    await ctx.send('Usage: >settings birthday_remove <name>')
                    return
                name = args[1]
                self.remove_birthday(name)
                await ctx.send(f'Birthday for {name} removed.')

            case UpdateSettings.QUOTE_PERSON_ADD:
                if len(args) < 2:
                    await ctx.send('Usage: >settings quote_person_add <name>')
                    return
                name = args[1]
                self.update_quotes_people(name)
                await ctx.send(f'Quote person "{name}" added.')

            case UpdateSettings.QUOTE_PERSON_REMOVE:
                if len(args) < 2:
                    await ctx.send('Usage: >settings quote_person_remove <name>')
                    return
                name = args[1]
                self.remove_quotes_people(name)
                await ctx.send(f'Quote person "{name}" removed.')

            case UpdateSettings.QUOTE_CHANNEL_SET:
                if self.quotes_channel_id == ctx.channel.id:
                    await ctx.send(f'Quotes channel is already set to #{ctx.channel.name}')
                    return

                self.quotes_channel_id = ctx.channel.id
                path = ServerContext.__get_server_context_path(self.server_id, Contexts.QUOTES_CHANNEL_ID)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(str(self.quotes_channel_id))
                await ctx.send('Loading quotes from the new channel, please wait...')
                self.quotes_list = RandomList(await read_all_quotes(ctx.bot, self.server_id, self.quotes_channel_id))
                print(f'Server {self.server_id} - Loaded {len(self.quotes_list.items)} quotes from channel ID {self.quotes_channel_id}')
                self.person_quotes = PersonQuotes(self.quotes_list, self.quotes_people)
                await ctx.send(f'Quotes channel set to #{ctx.channel.name}')

            case UpdateSettings.TRUTH_CHANNEL_SET:
                if self.truth_social_channel_id == ctx.channel.id:
                    await ctx.send(f'Truth Social channel is already set to #{ctx.channel.name}')
                    return

                self.truth_social_channel_id = ctx.channel.id
                path = ServerContext.__get_server_context_path(self.server_id, Contexts.TRUTH_SOCIAL_CHANNEL_ID)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(str(self.truth_social_channel_id))
                await ctx.send(f'Truth Social channel set to #{ctx.channel.name}')

            case UpdateSettings.QUOTE_CHANNEL_REMOVE:
                self.quotes_channel_id = None
                path = ServerContext.__get_server_context_path(self.server_id, Contexts.QUOTES_CHANNEL_ID)
                if path.exists():
                    path.unlink()
                self.quotes_list = RandomList([])
                self.person_quotes = PersonQuotes(self.quotes_list, [])
                await ctx.send('Quotes channel and all associated quotes removed.')

            case UpdateSettings.TRUTH_CHANNEL_REMOVE:
                self.truth_social_channel_id = None
                path = ServerContext.__get_server_context_path(self.server_id, Contexts.TRUTH_SOCIAL_CHANNEL_ID)
                if path.exists():
                    path.unlink()
                await ctx.send('Truth Social channel removed.')
            
            case UpdateSettings.PREFIX_UPDATE:
                if len(args) != 2:
                    await ctx.send('Usage: >settings prefix_update <new_prefix>')
                    return
                prefix = args[1]
                if prefix not in VALID_PREFIXES:
                    await ctx.send(f'Error: Invalid prefix "{prefix}". Valid prefixes are: {", ".join(VALID_PREFIXES)}')
                    return

                self.update_prefix(prefix)
                await ctx.send(f'Prefix updated to: {prefix}')

    server_id: int
    prefix: str
    truth_social_channel_id: int | None
    quotes_channel_id: int | None
    quotes_people: list[str] = []
    person_quotes: PersonQuotes
    quotes_list: RandomList
    birthdays: dict[str, datetime]
