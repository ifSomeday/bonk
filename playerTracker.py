import discord
from discord.ext import commands

##TODO: convert to psql or something
import pickle
import asyncio
import os

## Used to track the worst players in MM
class PlayerTracker(commands.Cog):

    ## Init
    def __init__(self, bot):
        self.bot = bot
        self.fileLock = asyncio.Lock()
        self.filePath = "{0}/trackerDB.pickle".format(os.getcwd())
        self.loadDatabase()

    ## Adds name and comments to the tracker
    @commands.command(help="Add a player to the MM Tracker")
    async def add(self, ctx, name : str, *, description : str):
        print("adding {0} as {1}".format(name, description))
        self.database.setdefault(name.lower(), {"name" : name, "description" : []})
        self.database[name.lower()]["description"].append(description)
        await self.saveDatabase()
        await ctx.message.add_reaction('✅')
        
    ## searches the tracker for player matches based on query
    ## this is a rudimentary case insensitive substring search 
    @commands.command(help="Search the MM Tracker for players")
    async def search(self, ctx, *, name : str):
        nameL = name.lower()
        out = []
        async with self.fileLock:
            for k in self.database:
                if nameL in k:
                    out.append(self.database[k]["name"])
        await ctx.send("\n".join(out))
            

    ## display a player and their comments
    @commands.command(help="Display information about a specific player in the MM Tracker")
    async def display(self, ctx, *, name : str):
        async with self.fileLock:
            if name.lower() in self.database:
                user = self.database[name.lower()]
                desc = " **-** {0}".format("\n **-** ".join(user["description"]))
                embed = discord.Embed()
                embed.color = discord.Colour.purple()
                embed.title = user["name"]
                embed.description = desc
                await ctx.send(embed=embed)
            else:
                await ctx.send("`{0}` not found".format(name))

    ## Load the tracker database (TODO: convert to psql)
    def loadDatabase(self):
        self.database = {}
        if(os.path.isfile(self.filePath)):
            with open(self.filePath, "rb") as f:
                self.database = pickle.load(f)

    ## Save the tracker database (TODO: convert to psql)
    async def saveDatabase(self):
        async with self.fileLock:
            with open(self.filePath, "wb") as f:
                pickle.dump(self.database, f)


def setup(bot):
    bot.add_cog(PlayerTracker(bot))