###############################
'''this loads the "DISCORD_TOKEN" string from the .env file'''

import time
from discord.reaction import Reaction
from dotenv import load_dotenv
import os, random

load_dotenv()

TOKEN = os.environ["DISCORD_TOKEN"]

###############################

################ IMPORTS ################
import discord
from Utils.ErrorHandling import command_error
from Utils.Constants import BOT_MAX_ITEMS_SELLING, GLOBAL_SHOP, MSG_EVENTS, RefreshShop, SHOP_CONSTANTS
from discord.ext import commands
from GameLogic.Player import Player
from GameLogic.Trading import CancelAllTrades
from GameLogic.plants import Plant, PlantStorage
from GameLogic.Bees import Bee, BeeStorage
from discord.ext import tasks
#########################################


intents = discord.Intents.all()

bot : commands.Bot = commands.Bot(
                    command_prefix="$",
                    case_insensitive=True,
                    intents=intents,
                    help_command=None
                    )


def LoadCogs():
    if not os.path.isdir("cogs"): 
        print("no cogs folder found!")
        return
    
    cogs = []
    for cog in os.listdir("./cogs"):
        if cog.endswith(".py"):
            cogs.append(cog)
    
    print(f"cogs folder found! attempting to load: \u001b[35m{len(cogs)}\u001b[0m cogs")
    for cog in cogs:
        try:
            cog = f"cogs.{cog.replace('.py', '')}"
            bot.load_extension(cog)
            print(f"\u001b[32m{cog} Loaded! \u001b[0m")
        except Exception as e:
            print(f"\u001b[31m{cog} cannot be loaded: {e} \u001b[0m")
            #raise e

    print("\u001b[36mdone loading cogs \u001b[0m")

@bot.event
async def on_message(message : discord.Message):
    if message.author == bot.user: 
        return
    await bot.fetch_user(message.author.id)
    await bot.process_commands(message=message)

@bot.command()
async def ping(ctx):
    await ctx.send(f'My ping is {bot.latency * 1000 : .0f}!')

@bot.event
async def on_reaction_add(reaction : Reaction, user):
    if user == bot.user:
        return
    if reaction.message.id in MSG_EVENTS:
        for callback in MSG_EVENTS[reaction.message.id]:
            await callback(reaction,user)
    

bot.on_command_error = command_error


@tasks.loop(seconds=(60 * 5))
async def SaveLoop():
    Player.Save()
    PlantStorage.Save()
    BeeStorage.Save()


@tasks.loop(seconds=30)
async def BotSellItem():
    from GameLogic.Items import Item
    from GameLogic.shop import Sale
    # get the items the bot is currently selling in the shop
    bot_user = Player.GetPlayer(bot.user.id)
    items = GLOBAL_SHOP.GetAllSalesFor(user = bot_user)
    if len(items) < BOT_MAX_ITEMS_SELLING:
        sale = Sale(item= Item.GetRandomItem(), amount=1, price=random.randint(3, 11), seller=bot_user)
        GLOBAL_SHOP.AddSale(sale=sale)
        items.append(sale)

@tasks.loop(minutes=30)
async def BotRefreshSales():
    await RefreshShop()

@bot.event 
async def on_ready():
    Player.BOT = bot
    SaveLoop.start()
    BotSellItem.start()
    GLOBAL_SHOP.LoadAll()
    BotRefreshSales.start()
    SHOP_CONSTANTS.next_refresh_at = time.time() + (60 * 30)
    print(f"{bot.user.name} has connected to Discord!")
    LoadCogs()

bot.run(TOKEN)

########### ATTEMPT AT SAVING RIGHT AS THE BOT IS TURNING OFF ###########
#GLOBAL_SHOP.CancelAllSales() not neccessary anymore, since mongodb is used
CancelAllTrades()
Player.Save()
PlantStorage.Save()
BeeStorage.Save()
#########################################################################