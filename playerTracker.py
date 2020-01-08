import discord
from discord.ext import commands

##TODO: convert to psql or something
import pickle
import asyncio
import os

class PlayerTracker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.fileLock = asyncio.Lock()
        self.filePath = "{0}/trackerDB.pickle".format(os.getcwd())
        self.loadDatabase()

    @commands.command()
    async def add(self, ctx, name : str, *, description : str):
        print("adding {0} as {1}".format(name, description))
        self.database.setdefault(name.lower(), {"name" : name, "description" : []})
        self.database[name.lower()]["description"].append(description)
        await self.saveDatabase()
        await ctx.message.add_reaction('✅')
        

    @commands.command()
    async def search(self, ctx, *, name : str):
        nameL = name.lower()
        print(self.database)
        out = []
        async with self.fileLock:
            for k in self.database:
                if nameL in k:
                    out.append(self.database[k]["name"])
        await ctx.send("\n".join(out))
            


    @commands.command()
    async def display(self, ctx, *, name : str):
        async with self.fileLock:
            if name.lower() in self.database:
                desc = " **-** {0}".format("\n **-** ".join(self.database[name.lower()]["description"]))
                embed = discord.Embed()
                embed.color = discord.Colour.purple()
                embed.title = self.database[name.lower()]["name"]
                embed.description = desc
                await ctx.send(embed=embed)
            else:
                await ctx.send("`{0}` not found".format(name))


    def loadDatabase(self):
        self.database = {}
        if(os.path.isfile(self.filePath)):
            with open(self.filePath, "rb") as f:
                self.database = pickle.load(f)

    async def saveDatabase(self):
        async with self.fileLock:
            with open(self.filePath, "wb") as f:
                pickle.dump(self.database, f)


def setup(bot):
    bot.add_cog(PlayerTracker(bot))