import discord
from discord.ext import commands, tasks

import keys

import twitch
import os
import asyncio
import pickle

class Stream(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.helix = twitch.Helix(keys.TWITCH_CLIENT_ID)
        self.filePath = "{0}/streams.pickle".format(os.getcwd())
        self.alertPath = "{0}/alerts.pickle".format(os.getcwd())
        self.fileLock = asyncio.Lock()
        self.fileLock2 = asyncio.Lock()

        self.database = {}
        self.loadDatabase()

        self.alertChannels = []
        self.loadAlerts()
        
        self.checkStream.start()


    @tasks.loop(seconds=60.0)
    async def checkStream(self):
        try:
            async with self.fileLock:
                for user in self.database:
                    channel = self.helix.user(user)
                    if(channel is None):
                        return
                    if(not self.database[user]["online"] == channel.is_live):
                        if(channel.is_live):
                            embed = await self.buildEmbed(channel)
                            messageIds = await self.doAlert(embed)
                            self.database[user]["messageIds"] = messageIds
                    elif(channel.is_live):
                        await self.doUpdate(channel, self.database[user]["messageIds"])
                    self.database[user]["online"] = channel.is_live
            await self.saveDatabase()
        except Exception as e:
            print("Fucky Wucky:\n{0}".format(e))


    async def buildEmbed(self, channel):
        stream = channel.stream
        embed = discord.Embed()
        embed.title = stream.title
        embed.set_thumbnail(url=stream.thumbnail_url.format(height=720, width=1280))
        embed.set_author(name=channel.display_name, url="https://www.twitch.tv/{0}".format(stream.user), icon_url=channel.profile_image_url)
        embed.url = "https://www.twitch.tv/{0}".format(stream.user)
        embed.color = discord.Colour.purple()
        embed.set_footer(text="{0} Viewers".format(stream.viewer_count))
        return(embed)


    async def doAlert(self, embed):
        messageIds = []
        async with self.fileLock2:
            for chId in self.alertChannels:
                ch = self.bot.get_channel(chId)
                message = await ch.send("Stream!", embed=embed)
                messageIds.append(message.id)
        return(messageIds)

    
    async def doUpdate(self, channel, messageIds):
        # for messageId in messageIds:
        #     message = await ch.fetch_message(messageId)
        #     embed = message.embeds[0]
        #     embed.set_footer(text="{0} Viewers".format(channel.stream.viewer_count))
        #     await message.edit(embed=embed)
        pass

    @checkStream.before_loop
    async def beforeCheckStream(self):
        await self.bot.wait_until_ready()


    @commands.command()
    async def addStream(self, ctx, *, streamId : str):
        streamId = streamId.lower()
        if(not streamId in self.database):
            if(not self.helix.user(streamId) == None):
                self.database.setdefault(streamId, {"online" : False, "messageIds" : []})
                await self.saveDatabase()
                await ctx.message.add_reaction('✅')
            else:
                await ctx.send("Invalid user specified.")
        else:
            await ctx.send("User already being tracked.")
        
    
    @commands.command()
    async def removeStream(self, ctx, *, streamId : str):
        streamId = streamId.lower()
        if(streamId in self.database):
            del(self.database[streamId])
            await self.saveDatabase()
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send("User was not being tracked.")


    @commands.command()
    async def addAlertChannel(self, ctx):
        if(not ctx.channel.id in self.alertChannels):
            self.alertChannels.append(ctx.channel.id)
            await self.saveAlerts()
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send("Channel already added.")


    @commands.command()
    async def removeAlertChannel(self, ctx):
        if(ctx.channel.id in self.alertChannels):
            self.alertChannels.remove(ctx.channel.id)
            await self.saveDatabase()
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send("Channel was not added.")


    @commands.command()
    async def listStreams(self, ctx):
        await ctx.send("Currently Tracking:\n{0}".format("\n".join(self.database.keys())))


    @commands.command()
    async def listChannels(self, ctx):
        await ctx.send("Currently Alerting:\n{0}".format("\n".join(self.alertChannels)))


    ## Load the stream database
    def loadDatabase(self):
        self.database = {}
        if(os.path.isfile(self.filePath)):
            with open(self.filePath, "rb") as f:
                self.database = pickle.load(f)


    ## Save the stream database
    async def saveDatabase(self):
        async with self.fileLock:
            with open(self.filePath, "wb") as f:
                pickle.dump(self.database, f)


    ## Load the alert database
    def loadAlerts(self):
        self.alertChannels = []
        if(os.path.isfile(self.alertPath)):
            with open(self.alertPath, "rb") as f:
                self.alertChannels = pickle.load(f)


    ## Save the alert database
    async def saveAlerts(self):
        async with self.fileLock2:
            with open(self.alertPath, "wb") as f:
                pickle.dump(self.alertChannels, f)


def setup(bot):
    bot.add_cog(Stream(bot))
