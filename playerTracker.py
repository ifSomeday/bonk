import discord
from discord.ext import commands

import steam
from steam import WebAPI, SteamID

import keys

##TODO: convert to psql or something
import pickle
import asyncio
import os
import re

## Used to track the worst players in MM
class PlayerTracker(commands.Cog):

    ## Init
    def __init__(self, bot):
        self.bot = bot
        self.fileLock = asyncio.Lock()
        self.filePath = "{0}/trackerDB.pickle".format(os.getcwd())
        self.loadDatabase()
        self.urlRegex = r"\.com/players/(\d+)"
        self.api = WebAPI(keys.STEAM_WEBAPI)

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
                embed.add_field(name="Comments", value=desc)
                embed.set_footer(text="Added {0} times".format(len(user["description"])))
                if("id" in user and not user["id"] is None):
                    await self.steamEmbed(embed, user["id"])
                await ctx.send(embed=embed)
            else:
                await ctx.send("`{0}` not found".format(name))


    async def steamEmbed(self, embed, steamId):
        profile = await self.getProfile(steamId)
        embed.set_thumbnail(url=profile["avatarfull"])
        embed.url = profile["profileurl"]
        embed.description = embed.title
        embed.title = profile["personaname"]
        ##75419738


    ## associate an actual steam profile
    @commands.command(help="Associate a steam profile with a given MM Tracker profile.\n <identifier> can be a Steam ID 32/64, Steam Profile url, or DotaBuff/Opendota link.")
    async def addProfile(self, ctx, name : str, identifier : str):
        if name.lower() in self.database:
            user = self.database[name.lower()]
            identifier = self.resolveIdentifier(identifier)

            try:
                self.api.ISteamUser.GetPlayerSummaries(steamids=identifier)
            except:
                await ctx.send("Error retrieving Steam profile.")
                return

            user["id"] = SteamID(identifier).as_64
            await self.saveDatabase()
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send("`{0}` not found".format(name)) 


    def resolveIdentifier(self, identifier):
        m = re.search(self.urlRegex, identifier)
        if(m):
            return(int(m.group(1)))
        
        ident = steam.steamid.steam64_from_url(identifier)
        if(ident):
            return(ident)
        
        try:
            int(identifier)
            return(identifier)
        except Exception as e:
            pass

        return


    async def getProfile(self, steamId):
        return(self.api.ISteamUser.GetPlayerSummaries(steamids=SteamID(steamId).as_64)["response"]["players"][0])


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