import discord
from discord.ext import commands, tasks

import io
import aiohttp

def is_me(**perms):
    async def predicate(ctx):
        return(ctx.message.author.id == 133811493778096128)
    return(commands.check(predicate))

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.tesxt = "sup loser. Beep. Boop. Assuming you actually have them, you can invite friends to this server.  Just click the server name in the top left and select \"Invite People\". Beep beep, bitch."

        self.hamHamUrl = "https://cdn.discordapp.com/attachments/427380139186323459/568038125927137280/hamham.png"

    @commands.command()
    @is_me()
    async def dm(self, ctx, user : discord.User):
        print(user.name)
        await user.send(self.tesxt)

    ##blank command so it shows up in help, the on_message listener below handles the actual processing
    @commands.command(help="hamham")
    async def save(self, ctx):
        #await self.sendHamHam(ctx)
        pass

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if(any(x in ctx.clean_content for x in [".save", "!save"])):
            await self.sendHamHam(ctx, ctx.channel)
        if(ctx.guild.id == 427380139186323457 and ctx.author.id == 98114500615487488):
            e = self.bot.get_emoji(729799500838862961)
            await ctx.add_reaction(e)


    async def sendHamHam(self, ctx, destination):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.hamHamUrl) as r:
                if r.status != 200:
                    await ctx.send("Error retrieving hamham :(")
                else:
                    data = io.BytesIO(await r.read())
                    await destination.send(file=discord.File(data, "hamham.png"))
        

def setup(bot):
    bot.add_cog(Misc(bot))

tesxt = "sup loser. Beep. Boop. Assuming you actually have them, you can invite friends to this server.  Just click the server name in the top left and select \"Invite People\". Beep beep, bitch."

