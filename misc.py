import discord
from discord.ext import commands, tasks

def is_me(**perms):
    async def predicate(ctx):
        return(ctx.message.author.id == 133811493778096128)
    return(commands.check(predicate))

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.tesxt = "sup loser. Beep. Boop. Assuming you actually have them, you can invite friends to this server.  Just click the server name in the top left and select \"Invite People\". Beep beep, bitch."


    @commands.command()
    @is_me()
    async def dm(self, ctx, user : discord.User):
        print(user.name)
        await user.send(self.tesxt)

    @commands.command(command_prefix="!")
    async def save(self, ctx):
        print("hi")

def setup(bot):
    bot.add_cog(Misc(bot))

tesxt = "sup loser. Beep. Boop. Assuming you actually have them, you can invite friends to this server.  Just click the server name in the top left and select \"Invite People\". Beep beep, bitch."

