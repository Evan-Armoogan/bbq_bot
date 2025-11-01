from datetime import datetime, timedelta
import discord
from discord.ext import commands
from polymarket import get_2028_presidential_odds
from zoneinfo import ZoneInfo
from birthdays import get_nearest_birthday_str, get_specific_birthday_str
from quotes import is_valid_quote
from random_list import RandomList, load_list
from time_to import get_time_to_str
from commands import Commands
from leafs import get_leafs_drought_str
from utils import get_main_file_path, get_pretty_name
from truth_social import TruthSocialWS
from server_context import ServerContext
from prefix import PREFIX
from typing import Callable

# TODO: This file is a disaster. So much stuff needs to be fixed I'm not
# even going to bother listing them here. Will do later.

with open(get_main_file_path().parent / 'version', 'r', encoding='utf-8') as vf:
    VERSION_STR = vf.readline().strip()

# Define intents
intents = discord.Intents.default()
intents.message_content = True

async def get_prefix(_: commands.Bot, message: discord.Message) -> str:
    if not message.guild:
        return 

    return server_contexts[message.guild.id].prefix

client = commands.Bot(command_prefix=get_prefix, intents=intents)
# Remove the default help command to create a custom one
client.remove_command('help')


def get_bot_key() -> str:
    with open(get_main_file_path().parent / 'bot_key.secret', 'r', encoding='utf-8') as f:
        return str(f.readline())


server_contexts: dict[int, ServerContext] = {}
truth_social_ws: TruthSocialWS | None = None
initializing = True
@client.event
async def on_ready() -> None:
    print('We have logged in as {0.user}'.format(client))
    # Set the bot version to be publicly visible
    await client.change_presence(activity=discord.Game(name=VERSION_STR))
    server_ids = [guild.id for guild in client.guilds]

    # TODO: this is really bad. Ideally, the whole file should be refactored into a class
    global server_contexts
    for server_id in server_ids:
        server_contexts[server_id] = await ServerContext.create(server_id, client)

    global truth_social_ws
    truth_social_ws = TruthSocialWS(client, server_contexts)

    global initializing
    initializing = False


@client.event
async def on_guild_join(guild: discord.Guild) -> None:
    server_contexts[guild.id] = await ServerContext.add_server(guild.id, client)
    print(f'Joined new server: {guild.name} (ID: {guild.id})')


@client.event
async def on_guild_remove(guild: discord.Guild) -> None:
    if guild.id in server_contexts:
        await ServerContext.remove_server(guild.id)
        del server_contexts[guild.id]
    print(f'Removed from server: {guild.name} (ID: {guild.id})')


def get_datetime_now() -> datetime:
    return datetime.now().astimezone(ZoneInfo("America/Toronto"))


command_info = Commands(PREFIX)
@client.command('help')
async def help(ctx: commands.Context, *args: str) -> None:
    argument = ''.join(args)

    if len(argument) == 0:
        output = "**User Commands:**\n"
        output += command_info.help()

        if ctx.author.guild_permissions.administrator:
            output += "\n\n**Admin Commands:**\n"
            output += command_info.help_admin()

        await ctx.send(output)
        print("Help dialogue sent")
        return
    elif argument in command_info.commands or argument in command_info.commands_admin:
        if command_info.is_admin_command(argument) and not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have permission to view help for this command.")
            print(f"Help {argument} denied due to insufficient permissions")
            return

        await ctx.send(f"**{PREFIX}{argument}:** {command_info.help_arg(argument)}")
        print(f"Help {argument} sent")
    else:
        raise RuntimeError("Invalid argument for help command")


def get_time_to_christmas() -> str:
    """
    Return a datetime object for the next Christmas (December 25)
    based on the current date. Always returns a future Christmas.
    Optional: specify a timezone (e.g., "America/Toronto").
    """
    tz = "America/Toronto"
    now = datetime.now(ZoneInfo(tz)) if tz else datetime.now()
    year = now.year

    # This year's Christmas
    christmas_dt = datetime(year, 12, 25, tzinfo=ZoneInfo(tz) if tz else None)

    # If it's already Christmas or after, move to next year
    if now >= christmas_dt:
        christmas_dt = datetime(year + 1, 12, 25, tzinfo=ZoneInfo(tz) if tz else None)

    return christmas_dt


def get_time_to_uwaterloo_freedom() -> datetime:
    return datetime(2027, 4, 23, 0, 0, 0, tzinfo=ZoneInfo("America/Toronto"))


def get_time_to_inauguration() -> datetime:
    """
    Return a timezone-aware datetime for the next U.S. presidential inauguration.
    Inaugurations occur every 4 years on January 20th, starting in 1937.
    """
    tz = "America/New_York"
    now = datetime.now(ZoneInfo(tz)) if tz else datetime.now()
    year = now.year

    # Find the most recent inauguration year (multiple of 4 since 1937)
    # Inauguration years are 1937, 1941, 1945, ..., 2021, 2025, 2029, ...
    offset = (year - 1937) % 4
    last_inauguration_year = year - offset
    next_inauguration_year = last_inauguration_year + 4

    inauguration = datetime(next_inauguration_year, 1, 20, 12, 0,  # Noon ET
                            tzinfo=ZoneInfo(tz) if tz else None)

    # If we’re still before the inauguration this year, use it
    if now < inauguration and now.year == inauguration.year:
        inauguration = datetime(year, 1, 20, 12, 0,
                                tzinfo=ZoneInfo(tz) if tz else None)

    return inauguration


def get_time_to_election() -> datetime:
    """
    Return a timezone-aware datetime for the next U.S. federal election.
    Federal elections are held on the first Tuesday after the first Monday in November.
    """
    tz = "America/New_York"
    now = datetime.now(ZoneInfo(tz)) if tz else datetime.now()
    year = now.year

    if (year % 2 != 0):
        year += 1

    while True:
        # November 1st
        nov1 = datetime(year, 11, 1, tzinfo=ZoneInfo(tz) if tz else None)
        # Find the first Monday
        first_monday_offset = (0 - nov1.weekday()) % 7  # Monday = 0
        first_monday = nov1 + timedelta(days=first_monday_offset)
        # Election is the next day (Tuesday)
        election_day = first_monday + timedelta(days=1)

        if now < election_day:
            return election_day

        # Otherwise, check the next year
        year += 2


def get_time_to_dt_str(dt: Callable[[], datetime]) -> str:
    time_to_event = dt() - get_datetime_now()
    duration_str = get_time_to_str(time_to_event.total_seconds())
    return duration_str


@client.command('election')
async def election(ctx: commands.Context, *args: str) -> None:
    await ctx.send(get_time_to_dt_str(get_time_to_election))


@client.command('inauguration')
async def inauguration(ctx: commands.Context, *args: str) -> None:
    await ctx.send(get_time_to_dt_str(get_time_to_inauguration))


@client.command('christmas')
async def christmas(ctx: commands.Context, *args: str) -> None:
    await ctx.send(get_time_to_dt_str(get_time_to_christmas))


@client.command('feliz_navidad')
async def feliz_navidad(ctx: commands.Context, *args: str) -> None:
    await ctx.send(f'{get_time_to_dt_str(get_time_to_christmas)}\nhttps://www.youtube.com/watch?v=5oyd5mR6cCY')


@client.command('illegals')
async def illegals(ctx: commands.Context, *args: str) -> None:
    await ctx.send(f'{get_time_to_dt_str(get_time_to_christmas)}\nhttps://www.youtube.com/watch?v=ZblXxiPA7d8')


@client.command('freedom')
async def freedom(ctx: commands.Context, *args: str) -> None:
    await ctx.send(get_time_to_dt_str(get_time_to_uwaterloo_freedom))


@client.command('polymarket')
async def polymarket(ctx: commands.Context, *args: str) -> None:
    line = ""
    for name, percentage in get_2028_presidential_odds():
        line += f"{name}: {percentage}%\n"

    date_str = get_datetime_now().strftime("%B %d, %Y %I:%M%p")
    string = f"2028 US Presidential Election Polymarket Betting Odds as of {date_str}\n" + line
    await ctx.send(string)


@client.command('penis')
async def penis(ctx: commands.Context, *args: str) -> None:
    await ctx.send("Bruh. That's a Joseph moment.")


@client.command('joseph')
async def joseph(ctx: commands.Context, *args: str) -> None:
    await ctx.send('```Kamala Harris crashed into me\n-Joseph [9/13/24]```')


@client.command('birthday')
async def birthday(ctx: commands.Context, *args: str) -> None:
    if len(args) > 0:
        name = get_pretty_name(args[0])
        if (birthday := get_specific_birthday_str(name, server_contexts[ctx.guild.id].birthdays)) is not None:
            await ctx.send(birthday)
        else:
            await ctx.send(f'Birthday for {name} not found')
    else:
        if (birthday := get_nearest_birthday_str(server_contexts[ctx.guild.id].birthdays)) is None:
            await ctx.send('No birthdays found')
        else:
            await ctx.send(birthday)


charlie_kirk_vids: RandomList = load_list(get_main_file_path().parent / 'charlie_kirk_vids.txt')
@client.command('charlie_kirk')
async def charlie_kirk(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(charlie_kirk_vids.next())


@client.command('quote')
async def quote(ctx: commands.Context, *args: str) -> None:
    person_quotes = server_contexts[ctx.guild.id].person_quotes
    quotes_list = server_contexts[ctx.guild.id].quotes_list

    if len(args) > 0:
        person = args[0]
        if (quote := person_quotes.get_quote(person)) is not None:
            content, files, embeds = quote
            await ctx.send(content=content, files=files, embeds=embeds)
        else:
            await ctx.send(f'No quotes found for "{person}". Make sure to use the correct spelling and formatting.')
    else:
        next = quotes_list.next()
        if next is None:
            await ctx.send("No quotes available.")
        else:
            content, files, embeds = next
            await ctx.send(content=content, files=files, embeds=embeds)


@client.command(name='leafs')
async def leafs_cmd(ctx: commands.Context) -> None:
    await ctx.send(get_leafs_drought_str())


@client.command(name='settings')
async def settings(ctx: commands.Context, *args: str) -> None:
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command.")
        return

    if len(args) == 0:
        await ctx.send("Missing required arguments. Usage: >settings <setting_type> <value1> ... <valueN>")
        return

    await server_contexts[ctx.guild.id].update_settings(ctx, *args)


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    
    if message.guild is None:
        return

    if initializing:
        if message.content.startswith(PREFIX):
            await message.channel.send("Bot still initializing...")
        return

    server_context = server_contexts[message.guild.id]
    if is_valid_quote(client, message, server_context.quotes_channel_id):
        quote = (message.content, message.attachments, message.embeds)
        server_context.quotes_list.append(quote)
        server_context.person_quotes.append(quote)

    await client.process_commands(message)


@client.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    for item in command_info.commands:
        if ctx.message.content.startswith(str(client.command_prefix) + item):
            output = 'Invalid argument for command: {0}. For help using this command, type "{1}help {0}"'.format(
                      item, client.command_prefix)
            await ctx.send(output)
            print(error)


client.run(get_bot_key())
