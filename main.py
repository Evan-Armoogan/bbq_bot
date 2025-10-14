import datetime
from random import random
import re
from typing import Any
import discord
from discord.ext import commands, tasks
from polymarket import get_2028_presidential_odds
from zoneinfo import ZoneInfo
from birthdays import get_nearest_birthday_str
from random_list import RandomList, load_list
from time_to import get_time_to_str
from commands import Commands
from leafs import get_leafs_drought_str

PREFIX = '>'

# Define intents
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(PREFIX, intents=intents)
# Remove the default help command to create a custom one
client.remove_command('help')


def get_bot_key() -> str:
    with open("bot_key.secret", "r") as f:
        return str(f.readline()) 


class PersonQuotes:
    @staticmethod
    def __name_in_str(name: str, quote: str) -> str:
        return (f'{name}:' in quote or
                f'-{name}' in quote or
                f'- {name}' in quote)

    def __init__(self, all_quotes: RandomList) -> None:
        self.evan: RandomList | None = None
        self.joseph: RandomList | None = None
        self.jason: RandomList | None = None
        self.lian_cheng: RandomList | None = None
        self.matthew: RandomList | None = None
        self.lucas: RandomList | None = None
        self.aryan: RandomList | None = None
        self.eric: RandomList | None = None
        self.sharan: RandomList | None = None

        attr = [a for a in self.__dict__.keys() if not a.startswith('__')]
        for a in attr:
            name = ' '.join([a.capitalize() for a in a.split('_')])
            setattr(self, a, RandomList([quote for quote in all_quotes.items if self.__name_in_str(name, quote[0])]))

    def get_quote(self, person: str) -> Any | None:
        attr = person.lower().replace(' ', '_')
        if attr in self.__dict__:
            quote_list: RandomList = getattr(self, attr)
            return quote_list.next()
        return None


async def read_all_quotes(client: commands.Bot) -> list[str]:
    channel_id = 1195468205867667456  # Quotes channel
    channel = client.get_channel(channel_id)
    if not channel:
        print("Channel not found. Make sure the bot can see it.")
        return []

    messages = []
    async for message in channel.history(limit=None):
        # Send text content
        content = message.content or ""

        # Handle attachments (images, files, etc.)
        files = []
        for attachment in message.attachments:
            fp = await attachment.to_file()
            files.append(fp)

        # Handle embeds if you want (Discord limits re-sending foreign embeds)
        embeds = message.embeds if message.embeds else []

        messages.append((content, files, embeds))

    print(f'Found {len(messages)} messages in the quotes channel.')
    return messages

    # # Regex: exactly three backticks, then non-backtick chars, then [int/int/int], then three backticks
    # pattern = re.compile(r"^```[^`\[\]]+\[\d+/\d+/\d+\]```$", re.MULTILINE)

    # filtered = []
    # for msg in messages:
    #     content = msg.content.strip()  # remove stray whitespace/newlines
    #     if pattern.match(content):
    #         filtered.append(msg)

    # with open('test.txt', 'w', encoding='utf-8') as f:
    #     for item in filtered:
    #         f.write(f"{item.content}\n")

    # print(f"Found {len(filtered)} matching messages.")
    # return filtered


quotes_list: RandomList | None = None
person_quotes: PersonQuotes | None = None
@client.event
async def on_ready() -> None:
    print('We have logged in as {0.user}'.format(client))
    # TODO: this is really bad. Ideally, the whole file should be refactored into a class
    global quotes_list
    global person_quotes
    quotes_list = RandomList(await read_all_quotes(client))
    person_quotes = PersonQuotes(quotes_list)


def get_datetime_now() -> datetime.datetime:
    return datetime.datetime.now().astimezone(ZoneInfo("America/Toronto"))


command_info = Commands(PREFIX)
@client.command('help')
async def help(ctx: discord.ext.commands.Context, *args: str) -> None:
    argument = ''.join(args)

    if len(argument) == 0:
        output = "Below is a list of the valid commands for this bot.\n"
        output += command_info.help()
        await ctx.send(output)
        print("Help dialogue sent")
        return
    elif argument in command_info.commands:
        await ctx.send(f"**{PREFIX}{argument}:** {command_info.help_arg(argument)}")
        print(f"Help {argument} sent")
    else:
        raise RuntimeError("Invalid argument for help command")


POLL_CLOSE_TIME_EPOCH = datetime.datetime(2026, 11, 3, 18, 0, 0, tzinfo=ZoneInfo("America/Toronto")).timestamp()

def get_time_to_election_str() -> str:
    time_to_closure = int(POLL_CLOSE_TIME_EPOCH - get_datetime_now().timestamp())
    duration_str = f"{get_time_to_str(time_to_closure)} until the first poll closure in the 2026 US Midterm Election"
    return duration_str


INAUGURATION_2029_TIME_EPOCH = datetime.datetime(2029, 1, 20, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto")).timestamp()

def get_time_to_inauguration_str() -> str:
    time_to_inauguration = INAUGURATION_2029_TIME_EPOCH - get_datetime_now().timestamp()
    duration_str = f"{get_time_to_str(time_to_inauguration)} until the 2029 Inauguration of President JD Vance"
    duration_str = f"{duration_str} until the 2029 Inauguration of President JD Vance"
    return duration_str


CHRISTMAS_2025_TIME_EPOCH = datetime.datetime(2025, 12, 25, 0, 0, 0, tzinfo=ZoneInfo("America/Toronto")).timestamp()

def get_time_to_christmas_str() -> str:
    time_to_christmas = CHRISTMAS_2025_TIME_EPOCH - get_datetime_now().timestamp()
    duration_str = get_time_to_str(time_to_christmas)
    duration_str = f"{duration_str} until Christmas!"
    return duration_str


UWATERLOO_FREEDOM_TIME_EPOCH = 1808452800

def get_time_to_uwaterloo_freedom_str() -> str:
    time_to_freedom = UWATERLOO_FREEDOM_TIME_EPOCH - get_datetime_now().timestamp()
    duration_str = get_time_to_str(time_to_freedom)
    duration_str = f"{duration_str} until the end of our University of Waterloo prison sentence"
    return duration_str


@client.command('election')
async def election(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(get_time_to_election_str())


@client.command('inauguration')
async def inauguration(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(get_time_to_inauguration_str())


@client.command('christmas')
async def christmas(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(get_time_to_christmas_str())


@client.command('feliz_navidad')
async def feliz_navidad(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(f'{get_time_to_christmas_str()}\nhttps://www.youtube.com/watch?v=5oyd5mR6cCY')


@client.command('illegals')
async def illegals(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(f'{get_time_to_christmas_str()}\nhttps://www.youtube.com/watch?v=ZblXxiPA7d8')


@client.command('freedom')
async def freedom(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(get_time_to_uwaterloo_freedom_str())


@client.command('polymarket')
async def polymarket(ctx: discord.ext.commands.Context, *args: str) -> None:
    line = ""
    for name, percentage in get_2028_presidential_odds():
        line += f"{name}: {percentage}%\n"

    date_str = get_datetime_now().strftime("%B %d, %Y %I:%M%p")
    string = f"2028 US Presidential Election Polymarket Betting Odds as of {date_str}\n" + line
    await ctx.send(string)


@client.command('penis')
async def penis(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send("Bruh. That's a Joseph moment.")


@client.command('joseph')
async def joseph(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send('```Kamala Harris crashed into me\n-Joseph [9/13/24]```')


@client.command('birthday')
async def birthday(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(get_nearest_birthday_str())


charlie_kirk_vids: RandomList = load_list("charlie_kirk_vids.txt")
@client.command('charlie_kirk')
async def charlie_kirk(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(charlie_kirk_vids.next())


@client.command('quote')
async def quote(ctx: discord.ext.commands.Context, *args: str) -> None:
    if len(args) > 0:
        person = args[0]
        if person_quotes is None:
            await ctx.send("Bot still initializing...")
            return
        if (quote := person_quotes.get_quote(person)) is not None:
            content, files, embeds = quote
            await ctx.send(content=content, files=files, embeds=embeds)
        else:
            await ctx.send(f'No quotes found for "{person}". Make sure to use the correct spelling and formatting.')
    else:
        if quotes_list is None:
            await ctx.send("Bot still initializing...")
            return
        content, files, embeds = quotes_list.next()
        await ctx.send(content=content, files=files, embeds=embeds)


@client.command(name='leafs')
async def leafs_cmd(ctx: commands.Context) -> None:
    await ctx.send(get_leafs_drought_str())


@client.event
async def on_command_error(ctx: discord.ext.commands.Context, error: Exception) -> None:
    for item in command_info.commands:
        if ctx.message.content.startswith(str(client.command_prefix) + item):
            output = 'Invalid argument for command: {0}. For help using this command, type "{1}help {0}"'.format(
                      item, client.command_prefix)
            await ctx.send(output)
            print(error)


client.run(get_bot_key())
