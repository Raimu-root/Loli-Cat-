import os
import youtube_dl
import asyncio
import discord
import random
import string
import json
from discord.ext import commands


class Arashicmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, target: int):
        deleted = await ctx.channel.purge(limit=target)
        embed = discord.Embed(title=f"{len(deleted)}件のメッセージを削除したにゃ！")
        await ctx.send(embed=embed, delete_after=3)

    @discord.slash_command(name="verify-setup", description="参加時役職付与機能を設定します。")
    @discord.default_permissions(administrator=True)
    async def verifysetup(
        self, ctx: discord.ApplicationContext,
        ROOO: discord.Option(discord.Role,
                             name="ロール",
                             description="認証成功時に付与する””このボットより順序の低いロール””を選択してください（メンバーロールなど）",
                             required=True),
        rulech: discord.Option(discord.TextChannel,
                               name="rule-ch",
                               description="このボットによる追加ルールを表示するチャンネルを選択してください",
                               required=True)):
        with open('data/verify.json', 'r+') as f:
            jsondata = json.load(f)
            guilddata = [ctx.guild.name, ROOO.id]
            jsondata[str(ctx.guild_id)] = guilddata
        with open('data/verify.json', 'w') as fx:
            json.dump(jsondata, fx, indent=4, ensure_ascii=False)
        syembed = discord.Embed(title="このサーバーでのおしゃべりを始めるには…", color=0xff8c01)
        syembed.add_field(name="1.このサーバーのルールに同意してください。",
                          value="```しっかりと読みましょう。```",
                          inline=False)
        syembed.add_field(
            name="2.このボットとのDM若しくはこのボットが居るサーバーにて`/verify` を使用して認証します。",
            value=
            f"```このサーバーのサーバーID({ctx.guild_id})をコピーしておいてください。\n分からない方⇒https://ja.macspots.com/how-find-server-id-discord-pc-2403733```",
            inline=False)
        syembed.add_field(name="3.このサーバーを存分に楽しみましょう！",
                          value="```^^```",
                          inline=False)
        await rulech.send(embed=syembed)
        embed = discord.Embed(title="設定が完了しました。")
        embed.add_field(name="詳細：",
                        value=f"`{str(jsondata[str(ctx.guild_id)])}`")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    @discord.slash_command(name="verify",
                           description="サーバーのメンバーロールを取得します（認証機能）")
    async def verify(self, ctx: discord.ApplicationContext,
                     verifyguildid: discord.Option(
                         str,
                         name="サーバー",
                         description="メンバーロールが欲しいサーバーのIDを入力してください。",
                         required=True)):
        if ctx.guild:
            await ctx.respond("このボットとのDMで実行してください。", ephemeral=True)
            await ctx.author.send("こちらで`/verify` を実行してください。")
        else:
            nam1 = random.randint(0, 15)
            nam2 = random.randint(0, 10)
            nam3 = nam1 + nam2
            await ctx.respond(f"三十秒以内に{nam1}+{nam2}の答えを半角数字で入力してにゃ…")
    
            def check(m):
                return m.content == str(nam3) and m.author == ctx.author
    
            try:
                await self.bot.wait_for("message", timeout=30, check=check)
                with open('data/verify.json', 'r') as fxx:
                    fxxx = json.load(fxx)
                    if verifyguildid in fxxx:
                        roleid = fxxx[verifyguildid][1]
                        guild = self.bot.get_guild(int(verifyguildid))
                        member = guild.get_member(ctx.author.id)
                        role = guild.get_role(roleid)
                        await member.add_roles(role)
                        await ctx.respond(f"{guild.name}でロールを付与したにゃん！")
                    else:
                        await ctx.respond(f"指定したサーバーでは認証機能のセットアップが行われてないにゃん…")
            except asyncio.TimeoutError:
                await ctx.respond(f"一定時間答えが入力されなかったためこの後は反応しないにゃん…",
                                  ephemeral=True)
            return


def setup(bot):
    bot.add_cog(Arashicmd(bot))