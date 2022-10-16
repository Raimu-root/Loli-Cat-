import os
import asyncio
import discord
import random
import string
import requests
from discord.ext import commands

HHHH = open('HHHH.txt', 'r').read().split('\n')

class NSFWcmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
		
    @commands.command()
    @commands.cooldown(5, 5, type=commands.cooldowns.BucketType.user)
    async def hentai(self, ctx):
        if ctx.channel.is_nsfw():
            for i in range(2):
                msg = random.choice(HHHH)
                await ctx.send(msg)
        else:
            embed = discord.Embed(title="⚠️ NSFWチャンネル以外では実行できないにゃ… ⚠️")
            await ctx.send(embed=embed, delete_after=5)

    @commands.command()
    async def neko(self, ctx):
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.0.0 Safari/537.36",
            "accept-encoding": "gzip, deflate",
            "content-type": "application/json"
        }
        session = requests.session()
        session.get("https://nekobot.xyz/api/")
        if ctx.channel.is_nsfw():
            data = session.get("https://nekobot.xyz/api/image?type=hneko", headers=headers).json()
            embed = discord.Embed(title="にゃん！")
            embed.set_image(url=data["message"])
            await ctx.send(embed=embed)
        else:
            data = session.get("https://nekobot.xyz/api/image?type=neko", headers=headers).json()
            embed = discord.Embed(title="にゃん！")
            embed.set_image(url=data["message"])
            await ctx.send(embed=embed)

 

def setup(bot):
    bot.add_cog(NSFWcmd(bot))