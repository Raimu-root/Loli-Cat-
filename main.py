import os
import youtube_dl
import asyncio
import discord
import random
import string
import re
import datetime
import ast
from discord.ext import commands, tasks
#from discord_slash import SlashCommand, SlashContext


INITIAL_EXTENSIONS = {
    'data.arashi',
    'data.cmd',
    'data.event',
    'data.nsfw',
    'data.slash',
    'data.music'
}

#BOT構築
intents = discord.Intents.all()
intents.typing = False
intents.message_content = True

token = os.environ['TOKEN']

bot = commands.Bot(command_prefix="xp!", intents=intents, help_command=None)

for cog in INITIAL_EXTENSIONS:
    bot.load_extension(cog)

@bot.event
async def on_ready():
    print(f"ログイン成功:{bot.user}")
    while True:
        await bot.change_presence(
            status=discord.Status.dnd,
            activity=discord.Game(name=f"xp!help｜現在{len(bot.guilds)}サーバーに導入。",
                                  type=discord.ActivityType.playing))
        await asyncio.sleep(25)
        await bot.change_presence(
            status=discord.Status.dnd,
            activity=discord.Game(name="xp!help｜https://bit.ly/loli-cat",
                                  type=discord.ActivityType.playing))
        await asyncio.sleep(25)


@tasks.loop(seconds=55)
async def resetloop():
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
    now = datetime.datetime.now(JST).strftime('%H:%M')
    listchan = [
        "00:00",
        "01:00",
        "02:00",
        "03:00",
        "04:00",
        "05:00",
        "06:00",
        "12:00",
        "20:00",
        "18:00",
        "21:00",
        "22:00",
        "23:00"
    ]
    for rundate in listchan:
        if now == rundate:
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    try:
                        await resetch(channel)
                    except:
                        pass

async def resetch(channel):
    if channel.topic != None:
        if re.search("autoreset", channel.topic):
            msg = discord.Embed(title="通知", description="チャンネルの再生成が完了したにゃん♡")
            channel2 = await channel.clone()
            await channel2.edit(position=channel.position)
            await channel.delete()
            await channel2.send(embed=msg)
            if channel2.topic != None:
                if re.search("autosend=", channel2.topic):
                    s = channel2.topic
                    target = 'autosend="'
                    idx = s.find(target)
                    r = s[idx+len(target):]
                    s = r
                    target = '"'
                    idx = s.find(target)
                    r = s[:idx]
                    await channel2.send(r)
        return
    else:
        return


async def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


@bot.command(name="eval")
async def eval_fn(ctx, *, cmd):
    evaluser = [962953982618259476, 976420283965636668, 952815962262999120, 1019576845341040710]
    if ctx.author.id in evaluser:
        fn_name = "_eval_expr"
        
        cmd = cmd.strip("` ")
        
        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
    
        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"
        
        parsed = ast.parse(body)
        body = parsed.body[0].body
    
        await insert_returns(body)
        
        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
        await eval(f"{fn_name}()", env)
        #result = (await eval(f"{fn_name}()", env))
        #await ctx.send(result)
    else:
        await ctx.message.add_reaction("🤔")



@bot.command()
async def reload(ctx):
    if ctx.message.author.id == 962953982618259476 or ctx.message.author.id == 952815962262999120 or ctx.message.author.id == 1019576845341040710:
        msg = "✅ リロードします。"
        await ctx.send(msg)
        for cog in INITIAL_EXTENSIONS:
            bot.reload_extension(cog)
    else:
        await ctx.message.add_reaction("🤔")

try:
    resetloop.start()
    bot.run(token)
except discord.errors.HTTPException:
    os.system('kill 1')  