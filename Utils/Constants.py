# ITEM/TRADING
CURRENCY_SYMBOL = "💰"
PAGE_ITEM_LIMIT = 10
ITEMS_PER_TRADE_LIMIT = 10
STARTING_AMOUNT_OF_LOOTBOXES = 5
BOT_MAX_ITEMS_SELLING = 10

#SAVING CONFIG
PLAYER_DATA_FILEPATH = './Data/PlayerData.json'

#SHOP
import time
from GameLogic.Items import Item
import asyncio
from GameLogic.Player import Player
import discord
from GameLogic.shop import Shop
GLOBAL_SHOP = Shop()

# NEXT SHOP REFRESH
class SHOP_CONSTANTS:
    next_refresh_at : int = 0

#SEED GROWTH DURATION
MINUTE = 60 # will be changed when debugging so plants can grow quickly
class SEED_DURATION:
    x_seed =            MINUTE * 15
    wooden_seed =       MINUTE * 15
    arctic_parasite =   MINUTE * 20

#BEE GROWTH DURATION
class BEE_DURATION:
    normal_bee = MINUTE * 10

HOUR = 60 * 60
#Time it takes for a pet to grow up
PET_GROWTH_DURATION = HOUR * 18

#GLOBAL DICTIONARY OF EVENTS
MSG_EVENTS : dict[int, list] = {}

def __add_listener__(msg_id, listener):
    if msg_id not in MSG_EVENTS:
        MSG_EVENTS[msg_id] = [listener]
    else :
        MSG_EVENTS[msg_id].append(listener)

def OnReaction(msg):
    def decorator(func):
        __add_listener__(msg.id, func)
    return decorator

def OnReactionOnce(msg):
    def decorator(func):
        async def wrapper(reaction,user):
            await func(reaction,user)
            MSG_EVENTS[msg.id].remove(wrapper)
        __add_listener__(msg.id, wrapper)
    return decorator

def OnReactionOnly(msg, accepted_reactions: list[str], accepted_users = []):
    def decorator(func):
        async def wrapper(reaction,user):
            if str(reaction) in accepted_reactions and (len(accepted_users) == 0 or user in accepted_users):
                await func(reaction,user)
        __add_listener__(msg.id, wrapper)
    return decorator

def OnReactionOnlyOnce(msg, accepted_reactions: list[str], accepted_users = []):
    def decorator(func):
        async def wrapper(reaction,user):
            if str(reaction) in accepted_reactions and (len(accepted_users) == 0 or user in accepted_users):
                await func(reaction,user)
                MSG_EVENTS[msg.id].remove(wrapper)
        __add_listener__(msg.id, wrapper)
    return decorator

def pretty_time_delta(seconds):
    s = seconds
    seconds = round(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        p = "%d days, %d hours, %d minutes, %d seconds" % (
            days,
            hours,
            minutes,
            seconds,
        )
    elif hours > 0:
        p = "%d hours, %d minutes, %d seconds" % (hours, minutes, seconds)
    elif minutes > 0:
        p = "%d minutes, %d seconds" % (minutes, seconds)
    else:
        p = "%d seconds" % (seconds,)

    if s < 0:
        p = "-" + p
    return p

def ConvertItemList(items : list) -> list:
    result = []
    if len(items) == 0: return result
    tmp = []
    for item in items:
        try :
            possible_num = int(item)
            result.append( " ".join(tmp) )
            result.append(possible_num)
            tmp = []
        except:
            tmp.append(item)
    if len(tmp) > 0 : result.append( " ".join(tmp) ) 
    if isinstance(result[-1], str): result.append(1)
    #################### TEMPORARY ####################
    if "" in result: result.remove("")
    ###################################################
    return result
 
async def RewardUI( ctx, user : Player, title : str , items_to_give : list[Item]):
        hidden_content = ["**->** <a:loading:794672829202300939>" for _ in range(len(items_to_give))]
        embed = discord.Embed(
        title=title,
        description= "\n\n".join(hidden_content),
        color=discord.Color.dark_teal(),
        )
        msg = await ctx.reply(embed=embed)
        for i in range(len(items_to_give)):
            hidden_content[i] = f"**->** {items_to_give[i]}"
            embed.description = "\n\n".join(hidden_content)
            Player.GetPlayer(user.id).inventory.AddItem(items_to_give[i])
            await asyncio.sleep(1.5)
            await msg.edit(embed=embed)

async def RefreshShop():
    SHOP_CONSTANTS.next_refresh_at = time.time() + (60 * 30)
    bot_user = Player.GetPlayer(Player.BOT.user.id)
    for sale in GLOBAL_SHOP.GetAllSalesFor(user = bot_user):
        sale.Cancel()