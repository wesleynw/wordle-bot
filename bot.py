import discord
from discord.ext import commands
import os, asyncio, logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
from re import match

logging.basicConfig(level=logging.INFO)
intents = discord.Intents().default()

db_client = MongoClient("mongodb://database:27017")
db = db_client["discord_wordle_bot_db"]
bot = commands.Bot(command_prefix='^', intents=intents, help_command=None)




### EVENTS
@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} has conneced to Discord!')

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    if message.channel.name.lower() == "wordle" and bool(match(r"Wordle \d{3,} [\dX]/6", message.content)):
        coll = db[str(message.guild.id)]
        raw = message.content.split(' ')[2][0]
        day = raw[1]

        q = coll.find_one({"_id" : message.author.id})
        if q is not None: 
            if q.get("updated") == day:
                return


        if raw_score == 'X':
            score = 0
        else:
            score = 7 - int(raw_score)
        
        coll.update_one({"_id" : message.author.id}, {"$inc" : {"score" : score}}, upsert=True)
        coll.update_one({"_id" : message.author.id}, {"$set" : {"updated" : day}}, upsert=True)

        await message.add_reaction("✅")        




### COMMANDS
@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! **{round(bot.latency * 1000)}ms**.')

@bot.command()
async def leaderboard(ctx):
    coll = db[str(ctx.guild.id)]
    sorted_ranks = sorted(list(coll.find({})), key=lambda x: x.get('score'), reverse=True)
    logging.info(sorted_ranks)

    embed = discord.Embed(color=0x3498db)
    embed.add_field(name=f'Wordle Leaderboard', value='___', inline=False)

    for i in range(min(len(sorted_ranks), 4)):
        member = await ctx.guild.fetch_member(int(sorted_ranks[i]['_id']))
        embed.add_field(name=f"***{i+1}*** - {member.display_name}", value=f"{sorted_ranks[i]['score']} points", inline=False)
    
    await ctx.send(embed=embed)



### RUN
load_dotenv()
token = os.environ.get('TOKEN')
bot.run(token)