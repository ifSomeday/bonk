import discord
from discord.ext import commands

##TODO: convert to psql or something
import pickle

class PlayerTracker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(PlayerTracker(bot))