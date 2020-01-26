import discord
from discord.ext import commands
import keys


client = commands.Bot(command_prefix='.', case_insensitive=True)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    #game = discord.Game("bonk")
    #await client.change_presence(activity=game)

##load worst mmr
try:
    client.load_extension("playerTracker")
except Exception as e:
    print("FAILED to load PlayerTracker:\n{0}".format(e))
else:
    print("Loaded PlayerTracker")

##load stream tracking
try:
    client.load_extension("stream")
except Exception as e:
    print("FAILED to load Stream:\n{0}".format(e))
else:
    print("Loaded Stream")

client.run(keys.CLIENT_SECRET)
