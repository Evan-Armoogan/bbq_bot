from random_list import RandomList
from typing import Any
from discord.ext import commands
import discord
from prefix import PREFIX


def is_valid_quote(client: commands.Bot, message: discord.Message, channel_id: int | None) -> bool:
    if channel_id is None:
        return False

    return (
        len(message.content.strip()) > 0 and
        not message.content.strip().startswith(PREFIX) and
        not message.author.id == client.user.id and
        message.channel.id == channel_id
    )


async def read_all_quotes(client: commands.Bot, server_id: int, channel_id: int) -> list[str]:
    channel = client.get_channel(channel_id)
    if not channel:
        print(f"Error: {server_id} - Quotes channel with ID {channel_id} not found.")
        return []

    messages = []
    async for message in channel.history(limit=None):
        # Send text content
        content = message.content or ""

        if not is_valid_quote(client, message, channel_id):
            continue

        # Handle attachments (images, files, etc.)
        files = []
        for attachment in message.attachments:
            fp = await attachment.to_file()
            files.append(fp)

        # Handle embeds if you want (Discord limits re-sending foreign embeds)
        embeds = message.embeds if message.embeds else []

        messages.append((content, files, embeds))

    print(f'{server_id} - Found {len(messages)} messages in the quotes channel.')
    return messages


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

    def insert_person(self, person: str, quotes_list: RandomList) -> None:
        attr = person.lower().replace(' ', '_')
        name = ' '.join([a.capitalize() for a in person.split('_')])
        if attr not in self.__dict__:
            quote_list = RandomList([
                quote for quote in quotes_list.items
                if self.__name_in_str(name, quote[0])
            ])
            setattr(self, attr, quote_list)
