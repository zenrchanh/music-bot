#Importing Discord modules for bot to work.
import os
import shutil
from os import system
import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get

TOKEN = 'NjczNzg3MjUxMjg0NzcwODE3.XjfHXg.6wTuyiGUnMq29XivD9BNi7HYheE' #Insert discord token.
client = commands.Bot(command_prefix = '!') #Uses exclamation mark as prefix for commands in discord can modify to be something else.

players = {}

#If running will notify when running if the is online. Use @bot.event to create own events.
@client.event
async def on_ready(): #Can modify this to change status of bots 'game' can put any text you want.
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('hell yeah peget'))
    print('Discord bot online.')

@client.command(pass_context=True) #HELP
async def guide(ctx):
    await ctx.send(f'Commands = !play - plays song, !queue - queues song, !skip - skip song, !pause - pause song, !resume - resume song, !stop - stop')

@client.command(pass_context=True) #joining voice channel
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)
    
    await channel.connect()

    await ctx.send(f"Joined {channel}")

@client.command(pass_context=True) #leaving and not in voice channel.
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f'PGF has left channel {channel}')
        await ctx.send(f'Left {channel}')
    else:
        print('PGF not in voice channel')
        await ctx.send("Not in voice channel.")
    
@client.command(pass_context=True)
async def play(ctx, *url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")



    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("Error: Music playing")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.send("Initializing")

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,
        'outtmpl': "./song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    song_search = " ".join(url)

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -ff song -f " + '"' + c_path + '"' + " -s " + song_search)

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

@client.command(pass_context=True)
async def pause(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print('Music paused.')
        voice.pause()
        await ctx.send('Music paused.')
    else:
        print('Music currently not playing failed pause')
        await ctx.send('Not playing anything.')

@client.command(pass_context=True)
async def resume(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print('Resuming music')
        voice.resume()
        await ctx.send('Resuming music')
    else:
        print('Music is not paused')
        await ctx.send('Music currently playing.')

@client.command(pass_context=True)
async def stop(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)
    queues.clear()

    if voice and voice.is_playing():
        print('Music stopped.')
        voice.stop()
        await ctx.send('Music stopped')
    else:
        print('No music playing, failed to stop')
        await ctx.send('No music playing failed to stop')

queues = {} #dict to store que

@client.command(pass_context=True)
async def queue(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url)

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
        q_path = os.path.abspath(os.path.realpath("Queue"))
        system(f"spotdl -ff song{q_num} -f " + '"' + q_path + '"' + " -s " + song_search)


    await ctx.send("Adding song " + str(q_num) + " to the queue")

    print("Song added to queue\n")

@client.command(pass_context=True)
async def skip(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Playing Next Song")
        voice.stop()
        await ctx.send("Skipping current song.")
    else:
        print("No music playing")
        await ctx.send("No music playing failed")


@client.command(pass_context=True)
async def volume(ctx, volume: int):

    if ctx.voice_client is None:
        return await ctx.send("Not connected to voice channel")

    print(volume/100)

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Changed volume to {volume}%")   



#Insert Discord bot token here generated from discord bot. 
client.run(TOKEN)

