import os
import youtube_dl
import asyncio
import discord
import random
import string
from discord.ext import commands

neko = open('neko.txt', 'r').read().split('\n')

class eve(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener(name='on_command_error')
    async def OCE(self, ctx, err):
        if isinstance(err, commands.CommandOnCooldown):
            retry_after_int = int(err.retry_after)
            retry_minute = retry_after_int // 60
            retry_second = retry_after_int % 60
            embed1 = discord.Embed(title="クールダウン中です。", description="慌てるのはよくないにゃん！！")
            embed1.add_field(name="詳細", value=f"`{retry_minute}分{retry_second}秒` 待つにゃん^^")
            await ctx.send(embed=embed1)
            return
        else:
            print(err)
            
    @commands.Cog.listener(name='on_message_edit')
    async def OME(self, before, after):
        #up通知
        if after.author.id == 761562078095867916:
            ch = after.channel
            if "をアップしたよ!" in after.embeds[0].fields[0].name:
                embed_done = discord.Embed(title="Upを検知したにゃん！", color=0xffffff, description="次にUpできる時間になったら教えるにゃん♡")
                await ch.send(embed=embed_done)
            else:
                return
            await asyncio.sleep(3610)
            embed_up = discord.Embed(title="Upできる時間にゃん^^", color=discord.Colour.orange(), description="`/dissoku up`しようにゃ！！")
            await ch.send(embed=embed_up)
            return            
        
    @commands.Cog.listener(name='on_message')
    async def OM(self, message):
        #bump通知
        if message.author.id == 302050872383242240:
            ch = message.channel
            if "表示順をアップしたよ" in message.embeds[0].description:
                embed_done = discord.Embed(title="Bumpを検知したにゃん！", color=0xffffff, description="次にBumpできる時間になったら教えるにゃん♡")
                await ch.send(embed=embed_done)
            else:
                return
            await asyncio.sleep(7210)
            embed_bump = discord.Embed(title="Bumpできる時間にゃん^^", color=discord.Colour.orange(), description="`/bump`しようにゃ！！")
            await ch.send(embed=embed_bump)
            return
                    
        #普通のOM
        if message.author.bot:
            return
        elif "にゃん" in message.content:
	        msg = random.choice(neko)
	        await message.reply(msg)
	        return
        elif "にゃむ" in message.content:
            await message.channel.send("にゃむにゃむ♡")
            return
        elif "にゃ～ん" in message.content:
	        msg = random.choice(neko)
	        await message.reply(msg)
	        return
        elif "にゃ〜ん" in message.content:
	        msg = random.choice(neko)
	        await message.reply(msg)
	        return
    

def setup(bot):
    bot.add_cog(eve(bot))