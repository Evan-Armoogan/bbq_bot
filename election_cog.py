import datetime
from discord.ext import commands, tasks

# this is when the days to election will send in UTC 24 hour (8:00am ET)
# hour = 13
# minute = 0
# second = 0
hour = 20
minute = 53
second = 30

utc = datetime.timezone.utc

# If no tzinfo is given then UTC is assumed.
daily_election_time = datetime.time(hour=9, minute=26, second=0, tzinfo=utc)


class DailyElectionCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.my_task.start()

  def cog_unload(self):
    self.my_task.cancel()

  @tasks.loop(time=daily_election_time)
  async def my_task(self):
    print("My task is running!")


async def setup(client):
  print("Cog added")
  client.add_cog(DailyElectionCog(client))
