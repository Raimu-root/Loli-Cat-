import os
import youtube_dl
import asyncio
import discord
import random
import functools
import itertools
import math
from async_timeout import timeout
from discord.ext import commands


errorembed = discord.Embed(title="エラーが発生したにゃ…", description="もう一度実行し、ダメだった場合はサポートサーバーに報告してください。", color=0xff0000)

class VoiceError(Exception):
    pass

class YTDLError(Exception):
    pass

youtube_dl.utils.bug_reports_message = lambda: ''
    
class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -af dynaudnorm -ab 192k'
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '`{0.title}` '.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} 日'.format(days))
        if hours > 0:
            duration.append('{} 時間'.format(hours))
        if minutes > 0:
            duration.append('{} 分'.format(minutes))
        if seconds > 0:
            duration.append('{} 秒'.format(seconds))

        return ', '.join(duration)
        
class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester
    	
    def create_embed(self):
        embed = (discord.Embed(title='再生中の音楽の情報にゃん♡',
                               color=0xff8c01)
                 .add_field(name="タイトル", value='```{0.source.title}\n```'.format(self), inline=False)
                 .add_field(name='演奏時間', value=self.source.duration)
                 .add_field(name='再生を実行した人', value=self.requester.mention)
                 .add_field(name='この動画のうｐ主', value='[{0.source.uploader} さん]({0.source.uploader_url})'.format(self))
                 .add_field(name='動画へのリンク', value='[クリックしてにゃ。]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed(), delete_after=5)

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        errorembed.add_field(name="エラー内容：", value=f"```{error}```")
        await ctx.send(embed=errorembed)

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @discord.slash_command(name="leave", description="ボットをVCから切断します。")
    async def _leave(self, ctx: discord.ApplicationContext):
        """Clears the queue and leaves the voice channel."""

        guild = ctx.guild
        if guild.voice_client is None:
            embed = discord.Embed(title="⚠️ 失敗・・・",
                                  description="私はボイスチャンネルにいにゃいよ…",
                                  color=0xff8c01)
            await ctx.respond(embed=embed, delete_after=5)
            return

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]
        embed = discord.Embed(title="✅ 成功！",
                                  color=0xff8c01,
                                  description=f"ボイスチャンネルから退出したにゃん！")
        await ctx.respond(embed=embed, delete_after=5)

    @discord.slash_command(name="vol", description="現在再生中の音楽の音量を変更します。")
    async def _volume(self, ctx: discord.ApplicationContext, *, volume: discord.Option(int, "設定したい音量", min_value=1, max_value=100, required=True)):
        """Sets the volume of the player."""

        if not ctx.voice_state.is_playing:
            embed = discord.Embed(title="⚠️ 失敗・・・",
    	                          description="既に再生は停止しているにゃ…",
    	                          color=0xff8c01)
            await ctx.respond(embed=embed, delete_after=5)
            return

        ctx.voice_state.volume = volume / 100
        embed = discord.Embed(title="✅ 成功！",
                              color=0xff8c01,
                              description=f"ボリュームを{volume}に変更したにゃん！")
        await ctx.respond(embed=embed, delete_after=5)

    @discord.slash_command(name="playing", description="現在再生中の音楽の情報を送信します。")
    async def _now(self, ctx: discord.ApplicationContext):
        """Displays the currently playing song."""
        if len(ctx.voice_state.songs) == 0:
            embed = discord.Embed(title="⚠️ 失敗・・・",
                                  description="キューには何も入ってないにゃ…",
                                  color=0xff8c01)
            await ctx.respond(embed=embed, delete_after=5)
            return

        await ctx.respond(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @discord.slash_command(name="stop", description="現在再生中の音楽を停止します。")
    async def _stop(self, ctx: discord.ApplicationContext):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            embed = discord.Embed(title="✅ 成功！",
        	                      color=0xff8c01,
        	                      description=f"再生を停止し、キューを削除したにゃん！")
            await ctx.respond(embed=embed, delete_after=5)
                
        elif not ctx.voice_state.is_playing:
            embed = discord.Embed(title="⚠️ 失敗・・・",
    	                          description="既に再生は停止しているにゃ…",
    	                          color=0xff8c01)
            await ctx.respond(embed=embed, delete_after=5)
            return
            

    @discord.slash_command(name="skip", description="現在再生中の音楽をスキップします。")
    async def _skip(self, ctx: discord.ApplicationContext):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if not ctx.voice_state.is_playing:
            embed = discord.Embed(title="⚠️ 失敗・・・",
    	                          description="既に再生は停止しているにゃ…",
    	                          color=0xff8c01)
            await ctx.respond(embed=embed, delete_after=5)
            return

        voter = ctx.author
        if voter == ctx.voice_state.current.requester:
            await ctx.respond('再生中の音楽をスキップしたにゃん！', delete_after=5)
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.respond('再生中の音楽をスキップしたにゃん！', delete_after=5)
                ctx.voice_state.skip()
            else:
                await ctx.respond('**{}/3**人がスキップに賛成してるにゃん。賛成する人はスキップコマンドを実行してにゃん♡'.format(total_votes))

        else:
            await ctx.respond('あなたは既にスキップに賛成してるにゃん😰', ephemeral=True)

    @discord.slash_command(name="queue", description="キューの情報を送信します。")
    async def _queue(self, ctx: discord.ApplicationContext, *, page: discord.Option(int, "見たいページ", min_value=1, max_value=5, required=True)):
        """Shows the player's queue.

        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            embed = discord.Embed(title="⚠️ 失敗・・・",
                                  description="キューには何も入ってないにゃ…",
                                  color=0xff8c01)
            await ctx.respond(embed=embed, delete_after=5)
            return

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '{0}． [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = discord.Embed(title='{} 個の音楽：'.format(len(ctx.voice_state.songs)), description='{}'.format(queue))
        embed.set_footer(text='表示中のページ： {}/{}'.format(page, pages))
        await ctx.respond(embed=embed, delete_after=15)

    @discord.slash_command(name="shuffle", description="キューをシャッフルします。")
    async def _shuffle(self, ctx: discord.ApplicationContext):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            embed = discord.Embed(title="⚠️ 失敗・・・",
                                  description="キューには何も入ってないにゃ…",
                                  color=0xff8c01)
            await ctx.respond(embed=embed, delete_after=5)
            return

        ctx.voice_state.songs.shuffle()
        embed = discord.Embed(title="✅ 成功！",
                              color=0xff8c01,
                              description=f"キューをシャッフルしたにゃん！")
        await ctx.respond(embed=embed, delete_after=5)
        

    @discord.slash_command(name="remove", description="指定した番号の音楽をキューから削除します。")
    async def _remove(self, ctx: discord.ApplicationContext, 
                      index: discord.Option(int, "キューから削除したい曲のインデックス", min_value=1, max_value=10, required=True)):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            embed = discord.Embed(title="⚠️ 失敗・・・",
                                  description="キューには何も入ってないにゃ…",
                                  color=0xff8c01)
            await ctx.respond(embed=embed, delete_after=5)
            return

        ctx.voice_state.songs.remove(index - 1)
        embed = discord.Embed(title="✅ 成功！",
                              color=0xff8c01,
                              description=f"{index}番目の音楽をキューから削除したにゃん！")
        await ctx.respond(embed=embed, delete_after=5)

    @discord.slash_command(name="play", description="YouTube動画の音声をボイスチャンネルに流します。")
    async def _play(
                   self, 
                   ctx: discord.ApplicationContext,
                   song: discord.Option(str, "再生したいYoutube動画", required=True)
                  ):
        """Plays a song.

        If there are songs in the queue, this will be queued until the
        other songs finished playing.

        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed1 = discord.Embed(title="まずはボイスチャンネルに行くにゃん！^^", color=0xff8c01)
            await ctx.respond(embed=embed1, delete_after=5)
            return
            
        await ctx.defer()
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        
        try:
            
            source = await YTDLSource.create_source(ctx, song, loop=self.bot.loop)
            song = Song(source)
            await ctx.voice_state.songs.put(song)
            await ctx.followup.send('{} がキューに追加されたにゃん♡'.format(str(source)), delete_after=5)
        except YTDLError as e:
            errorembed.add_field(name="エラー内容：", value=f"```{e}```")
            await ctx.followup.send(embed=errorembed)
        
        
    

def setup(bot):
    bot.add_cog(Music(bot))