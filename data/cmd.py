import asyncio
import discord
import random
import aiohttp
import string
import io
from discord.ext import commands

taikoS = open('taiko.txt', 'r').read().split('\n')

class botcmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        rawping = self.bot.latency
        ping = round(rawping * 1000)
        embed = discord.Embed(title="Pong!^^", description=f"Botの速度は{ping}msだにゃん♡")
        await ctx.reply(embed=embed)
        
    @commands.command()
    @commands.cooldown(1, 50, type=commands.cooldowns.BucketType.guild)
    async def help(self, ctx):
        page1 = discord.Embed(title="ヘルプを表示してます。(1/5)",
                              color=0xff8c01,
                              description="⏹で終了します。")
        page1.add_field(name="ヘルプコマンドを実行しています。",
                        value="◀で前ページ、▶で次ページに行きます。",
                        inline=False)
        page1.add_field(name="`xp!`の後にコマンド一覧のコマンドを入力してください",
                        value="コマンドはあまりないけど許してにゃ～",
                        inline=False)
        page1.add_field(name="コマンド一覧(ゲーム・遊び関連)",
                        value="↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓",
                        inline=False)
        page1.add_field(name="taiko",
                        value="太鼓の達人で曲選びに迷った時にランダムに曲を選んでくれます。",
                        inline=False)
        page1.add_field(name="hentai", value="みんなも変態になろう！！", inline=False)
        page1.add_field(name="cat",
                        value="ランダムに猫の画像を送信します。",
                        inline=False)
        page1.add_field(name="fox",
                        value="ランダムに狐の画像を送信します。",
                        inline=False)
        page1.add_field(name="pimon",
                        value="ランダムにピクセルな画像を送信します。",
                        inline=False)
        page1.add_field(name="cqrc (内容)", 
                        value="内容に指定したコンテンツまたはURLをQRコードにして送信します。",
                        inline=False)
        page1.add_field(name="insult", 
                        value="Mな方におすすめ！たくさん痛めつけてくれます！！",
                        inline=False)
    
        page2 = discord.Embed(title="ヘルプを表示してます。(2/5)",
                              color=0xff8c01,
                              description="⏹で終了します。")
        page2.add_field(name="`xp!`の後にコマンド一覧のコマンドを入力してください",
                        value="コマンドはあまりないけど許してにゃ～",
                        inline=False)
        page2.add_field(name="コマンド一覧(Discord関連)",
                        value="↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓",
                        inline=False)
        page2.add_field(name="nitro (送信回数)", value="ニトロジェネレータ。送信回数に指定した回数分（最大10回）DMにギフトを送信します。\n回数を指定しなかった場合はコマンドを実行したチャンネルに一つギフトを送信します。", inline=False)
        page2.add_field(name="avatar (ユーザーID)",
                        value="(ユーザーID)に指定したユーザーID人のアバターを表示します。\nユーザーIDを指定しなかった場合はコマンドの実行者のアバターを送信します。",
                        inline=False)
    
        page3 = discord.Embed(title="ヘルプを表示してます。(3/5)",
                              color=0xff8c01,
                              description="⏹で終了します。")
        page3.add_field(name="`xp!`の後にコマンド一覧のコマンドを入力してください",
                        value="コマンドはあまりないけど許してにゃ～",
                        inline=False)
        page3.add_field(name="コマンド一覧(サーバー関連)",
                        value="↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓",
                        inline=False)
        page3.add_field(name="Sinfo", value="サーバーの情報を表示します。", inline=False)
        page3.add_field(name="Binfo", value="このボットの情報を表示します。", inline=False)
        page3.add_field(name="clear (値)",
                        value="(値)に指定した分のメッセージを削除します。（管理者以外不可）",
                        inline=False)
        page3.add_field(name="なし（代わりにチャンネルトピックを使用します。）", value="チャンネルのトピックに「autoreset」が含まれていた場合は定期的にチャンネル削除をします。それに加えて「autosend=\"送りたい文字\"」が含まれていた場合はリセット後にその文字を送信します。", inline=False)
    
        page4 = discord.Embed(title="ヘルプを表示してます。(4/5)",
                              color=0xff8c01,
                              description="⏹で終了します。")
        page4.add_field(name="コマンド一覧のスラッシュコマンドを使うことができます。",
                        value="スラッシュコマンド一覧を表示してるにゃ～",
                        inline=False)
        page4.add_field(name="スラッシュコマンド一覧",
                        value="↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓",
                        inline=False)
        page4.add_field(name="play (YT動画・URL)",
                        value="VCに接続し、(YT動画・URL)に指定したURL・タイトルのYoutube動画の音声を再生します。",
                        inline=False)
        page4.add_field(name="vol (値)", value="(値)に指定した音量に設定します。", inline=False)
        page4.add_field(name="stop", value="再生を停止します。\nコマンド実行者がVCにいない状態でストップすると、ボットがVCを離れます。", inline=False)
        page4.add_field(name="skip", value="再生中の音楽をスキップします。", inline=False)
        page4.add_field(name="playing", value="再生中の音楽の情報を表示します。", inline=False)
        page4.add_field(name="queue", value="キューの中身を一覧表示します。", inline=False)
        page4.add_field(name="remove", value="キューから指定した番号の音楽を削除します。", inline=False)
        page4.add_field(name="shuffle", value="キューをシャッフルします。", inline=False)
        page4.add_field(name="verify-setup", value="サーバーのアンチレイド機能としてお使いください。\n追加ルールを送信しロールを指定して、/verifyを使用して認証出来る様になります。", inline=False)
        page4.add_field(name="verify", value="サーバーIDを入力し、そのサーバーのルールに同意してサーバーのメンバーロールを入手しましょう！", inline=False)
        page4.add_field(name="neko", value="使ったらわかるｗ", inline=False)
        
        page5 = discord.Embed(title="ヘルプを表示してます。(5/5)",
                              color=0xff8c01,
                              description="⏹で終了します。")
        page5.add_field(name="このボットについて…",
                        value="このボットはろりねこ#7733が遊びで作成・運営しています。"
                        "\nこのボットが勝手にオフラインになることもあるかもしれませんがご了承ください。\n",
                        inline=False)
        page5.add_field(name="BOT作成者のいる雑談鯖",
                            value="https://discord.gg/ZrCTbkcff5",
                            inline=False)
        page5.add_field(
            name="BOT導入用URL",
            value="https://discord.com/oauth2/authorize?client_id=919046852089905192&permissions=1391870733566&scope=bot%20applications.commands",
            inline=False)
        
        pages = 5
        cur_page = 1
        contents = [page1, page2, page3, page4, page5]
        message = await ctx.reply(embed=page1)
        await message.add_reaction("💞")
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        await message.add_reaction("⏹️")
        await message.add_reaction("💕")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️", "⏹️"]
            
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add",
                                                    timeout=60,
                                                    check=check)
                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    await message.edit(embed=contents[cur_page - 1])
                    await message.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    await message.edit(embed=contents[cur_page - 1])
                    await message.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "⏹️":
                    await message.delete()
                    break
                else:
                    await message.remove_reaction(reaction, user)
        
            except asyncio.TimeoutError:
                await message.delete()
                break

    
    @commands.command()
    async def taiko(self, ctx):
	    msg = random.choice(taikoS) + "をやるといいにゃ～！"
	    await ctx.reply(msg)
	
    @commands.command()
    async def nitro(self, ctx, *, amount = None):
        def nnitro(n):
            return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
        if amount == None:
            msg = "https://discord.gift/" + str(nnitro(16))
            await ctx.send(msg)
        elif int(amount) < 11:
            for i in range(int(amount)):
                msg = "https://discord.gift/" + str(nnitro(16))
                await ctx.message.author.send(msg)

    @commands.command()
    async def avatar(self, ctx, *, userid = None):
        if userid == None:
            author = ctx.message.author
            user = "{}#{}".format(author.name, author.discriminator)
            url = author.avatar.url
            embed = discord.Embed(title=f"{user}さんのアバター", url=url, color=0xff00cc)
            embed.set_image(url=url)
            await ctx.reply(embed=embed)
        else:
            user = await self.bot.fetch_user(userid)
            url = user.avatar.url
            user = "{}#{}".format(user.name, user.discriminator)
            embed = discord.Embed(title=f"{user}さんのアバター", url=url, color=0xff00cc)
            embed.set_image(url=url)
            await ctx.reply(embed=embed)

    @commands.command()
    async def Sinfo(self, ctx):
        guild = ctx.guild
        ico = guild.icon.url
        total = guild.member_count
        online = sum(
            1 for member in guild.members
            if member.status != discord.Status.offline and member.bot == False)
        user = sum(1 for member in guild.members if not member.bot)
        botk = sum(1 for member in guild.members if member.bot)
        gname = guild.name
        gid = guild.id
        embed = discord.Embed(title="サーバー情報！！", color=0xff8c01)
        embed.set_thumbnail(url=ico)
        embed.add_field(name="サーバー名：ID",
                        value=f"```「{gname}」:「{gid}」```",
                        inline=False)
        embed.add_field(name="現在オンラインのユーザー数", value=f"`{online}人`")
        embed.add_field(name="ユーザー数", value=f"`{user}人`")
        embed.add_field(name="BOTの数", value=f"`{botk}台`")
        embed.add_field(name="合計メンバー数", value=f"`{total}人`")
    
        await ctx.send(embed=embed)
        
    '''                
    @commands.command()
    async def Binfo(self, ctx):
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
    
        shard_id = ctx.guild.shard_id
        shard = self.bot.get_shard(shard_id)
        shardPING1 = shard.latency
        shardPING2 = round(shardPING1 * 1000)
        shard_servers = len([guild for guild in self.bot.guilds if guild.shard_id == shard_id])
    
        embed = discord.Embed(title=f'{self.bot.user.name}の情報にゃん♡')
        embed.add_field(name='Discord.Pyのバージョン:', value=f"`{dpyVersion}`")
        embed.add_field(name='導入サーバー数:', value=f"`{shard_servers}`")
        embed.add_field(name='シャードID:', value=f"`{shard_id}`")
        embed.add_field(name='Ping:', value=f"`{shardPING2}`")
        
        await ctx.send(embed=embed)
    '''          
    @commands.command()
    async def Binfo(self, ctx):
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        usercount = 0
        for guild in self.bot.guilds:
            usercount += guild.member_count - 1
        rawping = self.bot.latency
        ping = round(rawping * 1000)
    
        embed = discord.Embed(title=f'{self.bot.user.name}の情報にゃん♡')
        embed.add_field(name='Discord.Pyのバージョン:', value=f"`{dpyVersion}`")
        embed.add_field(name='導入サーバー数:', value=f"`{serverCount}`サーバー")
        embed.add_field(name='Ping:', value=f"`{ping}`ms")
        embed.add_field(name="監視ユーザー数:", value=f"`{usercount}`ユーザー")
        embed.add_field(name="最近の更新情報", value=f"１．遊び系のコマンドをいくつか追加\n" \
        "最終更新日：2022年10月4日"
        )
        
        await ctx.send(embed=embed)


    @commands.command()
    async def pimon(self, ctx):
        sentmsg = await ctx.send("loading...")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://app.pixelencounter.com/api/basic/monsters/random/png") as res:
                if res.status == 200:
                    data = io.BytesIO(await res.read())
                else:
                    return
        file = discord.File(data, 'image.png')
        await sentmsg.edit(content="ぴくせるもんすた〜！", file=file)

    @commands.command()
    async def insult(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://evilinsult.com/generate_insult.php?lang=ja&type=json") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await ctx.send(data["insult"])
                else:
                    return

    @commands.command()
    async def cqrc(self, ctx, *, url="https://discord.com/"):
        sentmsg = await ctx.send("loading...")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.qrserver.com/v1/create-qr-code/?data={url}&format=png") as res:
                if res.status == 200:
                    data = io.BytesIO(await res.read())
                else:
                    return
        file = discord.File(data, "image.png")
        await sentmsg.edit(content="", file=file)

    @commands.command()
    async def cat(self, ctx):
        sentmsg = await ctx.send("loading...")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://aws.random.cat/meow") as res:
                if res.status == 200:
                    data = await res.json()
                    url = data["file"]
                else:
                    return
        embed = discord.Embed(title="猫^^")
        embed.set_image(url=url)
        await sentmsg.edit(content="", embed=embed)

    @commands.command()
    async def fox(self, ctx):
        sentmsg = await ctx.send("loading...")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://randomfox.ca/floof/") as res:
                if res.status == 200:
                    data = await res.json()
                    url = data["image"]
                else:
                    return
        embed = discord.Embed(title="狐^^")
        embed.set_image(url=url)
        await sentmsg.edit(content="", embed=embed)

        
def setup(bot):
    bot.add_cog(botcmd(bot))