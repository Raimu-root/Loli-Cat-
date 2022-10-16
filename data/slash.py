import os
import asyncio
import discord
import random
from discord.ext import commands



nekochan = open('nekochan.txt', 'r').read().split('\n')

class slcmd(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="neko", description="ボット作者がNekobotから厳選した「ねこ画像」を送信します。")
    async def nekobotsl(self, ctx: discord.ApplicationContext):
        if ctx.channel.is_nsfw():
            embed = discord.Embed(title="ねこ！", description="ボット作者はあまり男性視点でのセンスないかもだけど許してにゃ…；；", color=0xff00cc)
            embed.set_image(url=random.choice(nekochan))
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="⚠️ NSFWチャンネル以外では実行できないにゃ… ⚠️")
            await ctx.respond(embed=embed, delete_after=5)
        return
    

def setup(bot):
    bot.add_cog(slcmd(bot))