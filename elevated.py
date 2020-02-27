import discord
from discord.ext import commands, tasks

import keys

import os
import asyncio
import pickle
import aiohttp
import traceback
import datetime

from steam import SteamID

class Elevated(commands.Cog):


    def __init__(self, bot):
        self.bot = bot

        self.postChannel = 389504390177751054

        self.steamIds = [31646409]

        self.fileLock = asyncio.Lock()
        self.filePath = "{0}/elevatedLastMatch.pickle".format(os.getcwd())

        self.lastMatch = {}
        self.loadHistory()

        self.dotaHistoryUrl = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1"
        self.dotaDetailsUrl = "http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1"
        self.steamProfileUrl = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002"

        for uId in self.steamIds:
            if not uId in self.lastMatch:
                ## self.lastMatch[uId] = -1
                self.lastMatch[uId] = 5263207971

        self.checkHistory.start()


    @tasks.loop(seconds=60.0)
    async def checkHistory(self):
        try:
            for uId, lastMatch in self.lastMatch.items():

                steamId = SteamID(uId).as_32

                history = await self.__getMatchHistory(steamId)
                
                ## Started from the bottom now we here
                history = history[::-1]

                for match in history:
                    if match['match_id'] > lastMatch:

                        details = await self.__getMatchDetails(match['match_id'])
                        profile = await self.__getSteamProfile(steamId)

                        slot = -1
                        for player in match['players']:
                            if(SteamID(player['account_id']).as_32 == steamId):
                                slot = player['player_slot']
                        if slot == -1:
                            continue
                        
                        won = bool(1 << 7 & slot) != details['radiant_win']

                        embed = await self.__buildEmbed(match, details, profile, won, steamId)

                        ch = self.bot.get_channel(self.postChannel)
                        await ch.send("New match found!", embed=embed)

                        self.lastMatch[uId] = match['match_id']
                
            await self.saveHistory()

        except Exception as e:
            print(e)
            traceback.print_exc()


    async def __getMatchHistory(self, uid):
        async with aiohttp.ClientSession() as session:
            params = {  "key" : keys.STEAM_WEBAPI, 
                        "account_id" : uid  }
            async with session.get(self.dotaHistoryUrl, params = params) as r:
                if r.status == 200:
                    js = await r.json()
                    if(js['result']['status'] == 1):
                        return(js['result']['matches'])


    async def __getMatchDetails(self, uid):
        async with aiohttp.ClientSession() as session:
            params = {  "key" : keys.STEAM_WEBAPI, 
                        "match_id" : uid  }
            async with session.get(self.dotaDetailsUrl, params = params) as r:
                if r.status == 200:
                    js = await r.json()
                    return(js['result'])
                    
    async def __getSteamProfile(self, uid):
        async with aiohttp.ClientSession() as session:
            params = {  "key" : keys.STEAM_WEBAPI, 
                        "steamids" : SteamID(uid).as_64  }
            async with session.get(self.steamProfileUrl, params = params) as r:
                if r.status == 200:
                    js = await r.json()
                    return(js['response']['players'][0])


    def utc2tz(self, timestamp):
        return(datetime.datetime.fromtimestamp(timestamp).replace(tzinfo=datetime.timezone.utc).astimezone(tz=None))


    async def __buildEmbed(self, match, details, profile, won, uId):
        embed = discord.Embed()
        embed.title = "{0}!".format("Victory" if won else "Defeat")
        embed.url = "https://www.dotabuff.com/matches/{0}".format(match['match_id'])
        embed.set_author(name=profile['personaname'], url=profile['profileurl'], icon_url=profile['avatarfull'])
        
        await self.__addStats(embed, details, uId)
        
        t = self.utc2tz(details['start_time'] + details['pre_game_duration'] + details['duration'])
        embed.set_footer(text="Finished at {0}".format(t.strftime("%H:%M %m/%d/%Y MST")))
        embed.color = discord.Colour.dark_red()
        return(embed)

    async def __addStats(self, embed, details, steamId):
        player = {}
        for player in details['players']:
            if player['account_id'] == steamId:
                player = player
                break
        
        embed.add_field(name="Hero", value="TODO lol")
        embed.add_field(name="Items", value="TODO lol")
        embed.add_field(name="K/D/A", value="{kills}/{deaths}/{assists}".format(**player))
        embed.add_field(name="GPM", value=player['gold_per_min'])
        embed.add_field(name="XPM", value=player['xp_per_min'])
        embed.add_field(name="LH", value=player['last_hits'])


    ## Load the stream database
    def loadHistory(self):
        if(os.path.isfile(self.filePath)):
            with open(self.filePath, "rb") as f:
                self.database = pickle.load(f)


    ## Save the stream database
    async def saveHistory(self):
        async with self.fileLock:
            with open(self.filePath, "wb") as f:
                pickle.dump(self.lastMatch, f)


def setup(bot):
    bot.add_cog(Elevated(bot))