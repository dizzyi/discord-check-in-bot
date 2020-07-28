#discord
import discord
from discord.ext import commands
from discord.utils import get
#get .env
import os
from dotenv import load_dotenv
#text to speech
import pyttsx3
#database
import sqlite3
#gif
from tenor import fetch_tenor
##################
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

TENOR_API_KEY = os.getenv("TENOR_API_KEY")

PREFIX = '>'

client = commands.Bot(command_prefix = PREFIX)

VOLUME = 2
##############################################
# init of text to speech
engine = pyttsx3.init()
evoices = engine.getProperty('voices')
for evoice in evoices:
    if 'Hong' in evoice.name:
        engine.setProperty('voice', evoice.id)
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-40)

###################################################
conn = sqlite3.connect('check-in.db')
c = conn.cursor()

#c.execute("DROP TABLE names")
#c.execute("""
#    CREATE TABLE names(
#        AL text
#   )
#""")
conn.commit()

conn.close()

###################################################
@client.event
async def on_connect():
    print("The bot is connected to discord")

@client.event 
async def on_ready():
    print('the Check-in bot is ready.')
    for guild in client.guilds:
        for channel in guild.channels:
            try:
                for text_C in channel.text_channels:
                    await text_C.send(f"***Hi i am the check-in bot, enter {PREFIX}h(or {PREFIX}hp) for more info***")
                    await text_C.send( fetch_tenor('excited', TENOR_API_KEY) )
            except AttributeError:
                return


@client.command(pass_context=True, aliases=['p'])
async def ping(ctx):
    global voice

    try:
        channel = ctx.message.author.voice.channel
    except AttributeError:
        await ctx.send(f"{ctx.message.author.mention}, you haven't joined any voice channel yet")
        return

    voice = get( client.voice_clients, guild=ctx.guild )

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    #await voice.disconnect()

    await ctx.send(f"The check in bot has connected to {channel}")

    await ctx.send(f"Pong! delay:{round(client.latency * 1000)}ms")

@client.command(pass_context=True, aliases=['q'])
async def quit(ctx):
    channel = ctx.message.author.voice.channel
    voice = get( client.voice_clients , guild=ctx.guild )

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f'Left {channel}')
    else:
        print('Bot has no channel')
        await ctx.send(f"The bot didn't join any voice channel")

@client.command(pass_context=True, aliases=['h'])
async def hp(ctx):
    await ctx.send(f"""{ctx.message.author.mention}, Hi this is Check-in bot  
    I will help you see who join and leave the voice chat room and tell you!!!
    enter ***({PREFIX}join)      {PREFIX}p***  to tell me to join to your voice channel
    enter ***({PREFIX}quit)     {PREFIX}q***  to tell me to leave the voice channel
    enter ***({PREFIX}callme){PREFIX}cm*** to tell me how you wanted to be call
    enter ***({PREFIX}say)      {PREFIX}s***  to tell me what to say
    enter ***({PREFIX}gif)       {PREFIX}g***  to search a gif and post it here
    """)

@client.command(pass_context=True, aliases=['g'])
async def gif(ctx):
    keywords = '-'.join( ctx.message.content.split(' ')[1:] )
    if(keywords == None): 
        keywords = 'random'
    gifurl = fetch_tenor( keywords, TENOR_API_KEY)
    await ctx.send( gifurl )


@client.command(pass_context=True, aliases=['s'])
async def say(ctx):  
    sentence = ' '.join( ctx.message.content.split(' ')[1:] )
    
    if len(sentence) == 0:
        await ctx.send(f"{ctx.message.author.mention}, please specifiy what you want me to say")
        return

    try:
        channel = ctx.message.author.voice.channel
    except AttributeError:
        await ctx.send(f"{ctx.message.author.mention}, you haven't joined any voice channel yet")
        return

    voice = get( client.voice_clients, guild=ctx.guild )

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    output_voice = os.path.isfile('temp.mp3')
    try:
        if output_voice:
            os.remove('temp.mp3')
    except PermissionError:
        ctx.send('I was saying thing, pls try again')
        return
    
    engine.save_to_file(sentence,'temp.mp3')
    engine.runAndWait()

    voice.play(discord.FFmpegPCMAudio('./temp.mp3'), after= lambda e: print(f"Said {sentence}"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = VOLUME

@client.command(pass_context=True, aliases=['cm'])
async def callme(ctx, *, AL):
    ID = ctx.message.author.id
    conn = sqlite3.connect('check-in.db')
    c = conn.cursor()
    c.execute("SELECT * FROM names WHERE id=?", (ID,) )    
    namedb = c.fetchone()
    print(namedb)
    if(namedb):
        c.execute("UPDATE names SET AL=? WHERE ID=?",(AL,ID,))
        conn.commit()
    else:
        c.execute("INSERT INTO names VALUES (?,?)", ( ID, AL, ) )
        conn.commit()
    conn.close()
    await ctx.send(f"I'll call you {AL} from now on")

@client.event
async def on_voice_state_update(member, before, after):
    if(member.name == 'Check-in'):
        return
    
    output_voice = os.path.isfile('temp.mp3')
    try:
        if output_voice:
            os.remove('temp.mp3')
    except PermissionError:
        print('using')
        return
    print(f"member: {member.name}")
    print(f"id: {member.id}")
    print(f"before: {before.channel}")
    print(f"after: {after.channel}")

    ################################################################
    conn = sqlite3.connect('check-in.db')
    c = conn.cursor()
    c.execute("SELECT * FROM names WHERE id=?", (member.id,) )    
    namedb = c.fetchone()
    print(namedb)
    if(namedb):
        sayname = namedb[1]
    else:
        c.execute("INSERT INTO names VALUES (?,?)", ( member.id, member.name, ) )
        conn.commit()
        sayname = member.name
    conn.close()
    ################################################################
    output = '成員' + sayname + '已經'

    if(before.channel and not after.channel):
        output += '離開'
        print('leaving')
        voice = get( client.voice_clients , guild=before.channel.guild )

    if(after.channel and not before.channel):
        output += '加入'
        print('joining')
        voice = get( client.voice_clients , guild=after.channel.guild )
    
    if(not voice): 
        return

    output += '了聊天室'

    print(output)

    engine.save_to_file(output,'temp.mp3')
    engine.runAndWait()

    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = VOLUME
    voice.play(discord.FFmpegPCMAudio('./temp.mp3'), after= lambda e: print(f"Said {output}"))
    
        


client.run(TOKEN)   