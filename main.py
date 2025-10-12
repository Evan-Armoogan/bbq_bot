#V1.0 of development

import datetime
import os

import discord
from discord.ext import commands, tasks
from rcp import get_rcp_avgs
from polymarket import get_2028_presidential_odds
from zoneinfo import ZoneInfo
from birthdays import get_nearest_birthday_str
from random_list import RandomList, load_list

# Define intents
intents = discord.Intents.default()
intents.message_content = True

PREFIX = '>'

client = commands.Bot(PREFIX, intents=intents)
target_channel_id = 1294386878249963710  # should be set to #countdown-to-election-night

# valid_commands = '''
# {0}programming: returns a random response that might be somewhat related to programming class. Type "{0}help programming" for more info
# {0}election: returns the time until first polls close in the 2024 US Presidential Election. Type "{0}help election" for more info
# {0}help: returns a list of commands for use on the BBQ Bot. Type "{0}help help" for more info
# '''.format(client.command_prefix)

valid_commands = '''
**{0}election:** returns the time until first polls close in the 2024 US Presidential Election. Type "{0}help election" for more info
**{0}polls:** returns the current RCP polling averages in the US Presidential Election. Type "{0}help polls" for more info
**{0}polymarket:** returns the current Polymarket bettings averages in the US PResidential Election. Type "{0}help polymarket" for more info
**{0}help:** returns a list of commands for use on the BBQ Bot. Type "{0}help help" for more info
'''.format(client.command_prefix)

programming_help = '''
The **{0}programming** command returns a random response that might be somewhat related to programming class. This is entirely useless except to be funny but it really isn't. 

Valid Programming Command Arguments:
  1) {0}programming - returns a random response message
  2) {0}programming [number] - returns the response message that corresponds to the user's input index
  3) {0}programming loop - returns a loop of 10 random response messages
'''.format(client.command_prefix)

election_help = '''
The **{0}election** command returns the time until the first polls close. This command takes no arguments.
'''.format(client.command_prefix)

polls_help = '''
The **{0}polls** command returns the current polling averages in the RCP aggregate in all 7 swing states as well as the popular vote. This command takes no arguments.
'''

polymarket_help = '''
The **{0}polymarket** command returns the current polymarket bettings averages for the 2024 US Presidential Election. This command takes no arguments.
'''

help_help = '''
The **{0}help** command returns a list of valid commands that the BBQ Bot can handle. Below are a list of commands that can be used with this bot.
{1}
'''.format(client.command_prefix, valid_commands)

# help_dict = {
#     "programming": programming_help,
#     "election": election_help,
#     "help": help_help
# }

help_dict = {"election": election_help, "polls": polls_help, "polymarket": polymarket_help, "help": help_help}

#commands = ['programming', 'election', 'help']
commands_list = ['election', 'help']

marks_pogchamp_rant = r'''
WHY, what am i supposed to take from the meaningless word "POGCHAMP". IT'S AS IF YOU COMBINED THE WORD PIG AND HOG AND THEN PRETENDED IT WAS A CHAMPION. or maybe there is a competition between a pig and a hog and there will be a champion but you never specify who the champ is. but what does this champion have to do with dnd and wether or not you are excited, the the champ decide whether or not you are excited, in which case how are you communicating with a fricking pig or does the loser get eaten because thats all its good for and depending on how tasty the pogchamp is you are excited or not excited. or maybe you eat them both and decide which one is tastier and it is the pogchamp. and where are you getting the pogs, if you are mentioning them so much do you need help finding some? in which case i know several places that you might be able to buy some. or maybe its a different word combo like penis and frog and the frog penis has to be a certain size for you to be excited or maybe if you find a penis shaped frog you become excited. POGCHAMP IS STUPID, however very complex.\ -Mark D, many moons ago
'''

random_responses = {
    1:
    "IT'S PROGRAMMING SEASON",
    2:
    "LETS GOOOOOOOOO BEST CLASSSS",
    3:
    "PROGRAMMING IS POGGERS",
    4:
    "SUB TO EVAN_BBQ ON TWITCH",
    5:
    "IT'S A SCAMMMMMMMMM",
    6:
    "Watch the BBQ Podcast at tinyurl.com/evanbbq-yt",
    7:
    "WHAT SEASON?? PROGRAMMING SEASON!!",
    8:
    "PROGRAMMING IS MY FAVOURITE EPICEST CLASS",
    9:
    "This comes from a dictionary which returns random responses or responses that correspond to the index in the dictionary from user arguments"
}

client.remove_command('help')

def get_bot_key():
  with open("bot_key.secret", "r") as f:
    return str(f.readline())


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


def get_datetime_now():
  return datetime.datetime.now().astimezone(ZoneInfo("America/Toronto"))


# @client.command('programming')
# async def programming(ctx, *args):
#   args = ''.join(args)
#   if args == 'loop':
#     for i in range(10):
#       random_num = random.randint(1, len(random_responses))
#       await ctx.send(random_responses[random_num])
#     print("Sent loop of 10 random responses")
#   elif len(args) == 1:
#     for index in range(len(random_responses) + 1):
#       if int(args) == index:
#         await ctx.send(random_responses[index])
#         print("Sent user requested response to programming command")
#         return
#   else:
#     random_num = random.randint(1, len(random_responses))
#     await ctx.send(random_responses[random_num])
#     print("Random response for programming command sent")


@client.command('help')
async def help(ctx, *args):
  argument = ''.join(args)
  if len(argument) == 0:
    output = "Below is a list of the valid commands for this bot. {0}".format(
        valid_commands)
    await ctx.send(output)
    print("Help dialogue sent")
    return
  else:
    for item in commands_list:
      if item == argument:
        await ctx.send(help_dict[argument])
        print("Help {0} sent".format(argument))
        return
      elif item == commands_list[len(commands_list) - 1]:
        raise Exception


POLL_CLOSE_TIME_EPOCH = datetime.datetime(2026, 11, 3, 18, 0, 0, tzinfo=ZoneInfo("America/Toronto")).timestamp()

def get_time_to_election_str():
  time_to_closure = POLL_CLOSE_TIME_EPOCH - get_datetime_now().timestamp()
  days, remainder = divmod(time_to_closure, 3600 * 24)
  hours, remainder = divmod(remainder, 3600)
  minutes, seconds = divmod(remainder, 60)
  days = int(days)
  hours = int(hours)
  minutes = int(minutes)
  seconds = int(seconds)

  duration_str = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds until the first poll closure in the 2026 US Midterm Election"
  return duration_str

INAUGURATION_2029_TIME_EPOCH = datetime.datetime(2029, 1, 20, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto")).timestamp()

def get_time_to_inauguration_str():
  time_to_inauguration = INAUGURATION_2029_TIME_EPOCH - get_datetime_now().timestamp()
  days, remainder = divmod(time_to_inauguration, 3600 * 24)
  hours, remainder = divmod(remainder, 3600)
  minutes, seconds = divmod(remainder, 60)
  days = int(days)
  hours = int(hours)
  minutes = int(minutes)
  seconds = int(seconds)

  duration_str = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds until the 2029 Inauguration of President JD Vance"
  return duration_str

CHRISTMAS_2025_TIME_EPOCH = 1735102800 + 31540000

def get_time_to_christmas_str():
  time_to_christmas = CHRISTMAS_2025_TIME_EPOCH - get_datetime_now().timestamp()
  days, remainder = divmod(time_to_christmas, 3600 * 24)
  hours, remainder = divmod(remainder, 3600)
  minutes, seconds = divmod(remainder, 60)
  days = int(days)
  hours = int(hours)
  minutes = int(minutes)
  seconds = int(seconds)

  duration_str = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds until Christmas!"
  return duration_str

JAGMEET_PENSION_TIME_EPOCH = 1740459600

def get_time_to_jagmeet_pension_str():
  time_to_christmas = JAGMEET_PENSION_TIME_EPOCH - get_datetime_now().timestamp()
  days, remainder = divmod(time_to_christmas, 3600 * 24)
  hours, remainder = divmod(remainder, 3600)
  minutes, seconds = divmod(remainder, 60)
  days = int(days)
  hours = int(hours)
  minutes = int(minutes)
  seconds = int(seconds)

  duration_str = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds until Jagmeet Singh gets his pension and can call a federal election"
  return duration_str

UWATERLOO_FREEDOM_TIME_EPOCH = 1808452800

def get_time_to_uwaterloo_freedom_str():
  time_to_freedom = UWATERLOO_FREEDOM_TIME_EPOCH - get_datetime_now().timestamp()
  days, remainder = divmod(time_to_freedom, 3600 * 24)
  hours, remainder = divmod(remainder, 3600)
  minutes, seconds = divmod(remainder, 60)
  days = int(days)
  hours = int(hours)
  minutes = int(minutes)
  seconds = int(seconds)

  duration_str = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds until the end of our University of Waterloo prison sentence"
  return duration_str

@client.command('election')
async def election(ctx, *args):
  await ctx.send(get_time_to_election_str())
  return

@client.command('inauguration')
async def inauguration(ctx, *args):
  await ctx.send(get_time_to_inauguration_str())
  return

@client.command('christmas')
async def christmas(ctx, *args):
  await ctx.send(get_time_to_christmas_str())
  return

@client.command('feliz_navidad')
async def feliz_navidad(ctx, *args):
  await ctx.send(f'{get_time_to_christmas_str()}\nhttps://www.youtube.com/watch?v=5oyd5mR6cCY')
  return

@client.command('illegals')
async def illegals(ctx, *args):
  await ctx.send(f'{get_time_to_christmas_str()}\nhttps://www.youtube.com/watch?v=ZblXxiPA7d8')
  return

@client.command('freedom')
async def freedom(ctx, *args):
  await ctx.send(get_time_to_uwaterloo_freedom_str())
  return

# @client.command('jagmeet')
# async def jagmeet(ctx, *args):
#   await ctx.send(get_time_to_jagmeet_pension_str())
#   return

# @client.command('polls')
# async def polls(ctx, *args):
#   date_str = get_datetime_now().strftime("%B %d, %Y %I:%M%p")
#   string = f"2024 US Presidential Election RCP Aggregates as of {date_str}\n\n" + get_rcp_avgs()
#   await ctx.send(string)

@client.command('polymarket')
async def polymarket(ctx, *args):
  line = ""
  for name, percentage in get_2028_presidential_odds():
    line += f"{name}: {percentage}%\n"

  date_str = get_datetime_now().strftime("%B %d, %Y %I:%M%p")
  string = f"2028 US Presidential Election Polymarket Bettings Odds as of {date_str}\n" + line
  await ctx.send(string)

@client.command('penis')
async def penis(ctx, *args):
  await ctx.send("Bruh. That's a Joseph moment.")
  return

@client.command('joseph')
async def joseph(ctx, *args):
  await ctx.send('''```"Kamala Harris crashed into me"
-Joseph [9/13/24]```''')
  return

@client.command('birthday')
async def birthday(ctx, *args):
  await ctx.send(get_nearest_birthday_str())
  return

charlie_kirk_vids: RandomList = load_list("charlie_kirk_vids.txt")
@client.command('charlie_kirk')
async def charlie_kirk(ctx, *args):
  await ctx.send(charlie_kirk_vids.next())
  return

@client.event
async def on_command_error(ctx, error):
  for item in commands_list:
    if ctx.message.content.startswith(str(client.command_prefix) + item):
      output = 'Invalid argument for command: {0}. For help using this command, type "{1}help {0}"'.format(
          item, client.command_prefix)
      await ctx.send(output)
      print("Exception raised -- " + str(error))
      return


client.load_extension("election_cog")
client.run(get_bot_key())

# end of script
