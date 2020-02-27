import discord
from discord.ext import commands
import keys

import os

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


##load stream tracking
try:
    client.load_extension("elevated")
except Exception as e:
    print("FAILED to load Elevated:\n{0}".format(e))
else:
    print("Loaded Elevated")


##load dev plugin if it exists (not for prod)
if(os.path.isfile("{0}/dev.py".format(os.getcwd()))):
    client.load_extension("dev")

client.run(keys.CLIENT_SECRET)
