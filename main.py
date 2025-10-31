import datetime
import discord
from discord.ext import commands
from polymarket import get_2028_presidential_odds
from zoneinfo import ZoneInfo
from birthdays import get_nearest_birthday_str
from quotes import is_valid_quote
from random_list import RandomList, load_list
from time_to import get_time_to_str
from commands import Commands
from leafs import get_leafs_drought_str
from utils import get_main_file_path
from truth_social import TruthSocialWS
from server_context import ServerContext
from prefix import PREFIX

# TODO: This file is a disaster. So much stuff needs to be fixed I'm not
# even going to bother listing them here. Will do later.

with open(get_main_file_path().parent / 'version', 'r', encoding='utf-8') as vf:
    VERSION_STR = vf.readline().strip()

# Define intents
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(PREFIX, intents=intents)
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


def get_datetime_now() -> datetime.datetime:
    return datetime.datetime.now().astimezone(ZoneInfo("America/Toronto"))


command_info = Commands(PREFIX)
@client.command('help')
async def help(ctx: discord.ext.commands.Context, *args: str) -> None:
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
    if (birthday := get_nearest_birthday_str(server_contexts[ctx.guild.id].birthdays)) is None:
        await ctx.send('No birthdays found')
    else:
        await ctx.send(birthday)


charlie_kirk_vids: RandomList = load_list(get_main_file_path().parent / 'charlie_kirk_vids.txt')
@client.command('charlie_kirk')
async def charlie_kirk(ctx: discord.ext.commands.Context, *args: str) -> None:
    await ctx.send(charlie_kirk_vids.next())


@client.command('quote')
async def quote(ctx: discord.ext.commands.Context, *args: str) -> None:
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
async def on_command_error(ctx: discord.ext.commands.Context, error: Exception) -> None:
    for item in command_info.commands:
        if ctx.message.content.startswith(str(client.command_prefix) + item):
            output = 'Invalid argument for command: {0}. For help using this command, type "{1}help {0}"'.format(
                      item, client.command_prefix)
            await ctx.send(output)
            print(error)


client.run(get_bot_key())
