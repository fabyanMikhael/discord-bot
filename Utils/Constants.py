# ITEM/TRADING
CURRENCY_SYMBOL = "💰"
PAGE_ITEM_LIMIT = 10
ITEMS_PER_TRADE_LIMIT = 10
STARTING_AMOUNT_OF_LOOTBOXES = 5

#SAVING CONFIG
PLAYER_DATA_FILEPATH = './Data/PlayerData.json'

#SHOP
from GameLogic.shop import Shop
GLOBAL_SHOP = Shop()

#SEED GROWTH DURATION
class SEED_DURATION:
    X_SEED = 60 * 15

#BEE GROWTH DURATION
class BEE_DURATION:
    NORMAL_BEE = 60 * 10

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