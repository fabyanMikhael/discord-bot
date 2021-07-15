################Imports##############################
import asyncio
import random
import discord

from discord.ext import commands
from Utils.ErrorHandling import ErrorMessage 

from GameLogic.shop import Sale, CURRENCY_SYMBOL
from GameLogic.Player import Player
from GameLogic.Items import Inventory, Item
from GameLogic.Trading import PendingTrade, Trade, IsTrading, GetAnyTradeInvolving
from Utils.Constants import ITEMS_PER_TRADE_LIMIT

from Utils.Constants import GLOBAL_SHOP, pretty_time_delta

#####################################################

################Helper functions#######################
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

#####################################################

class PlayerCommands(commands.Cog):
    '''General Commands'''
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command(aliases=["inv"])
    @ErrorMessage("\n👋 **Use this:**  \n\n**$Inventory** `optional: page number`")
    async def Inventory(self, ctx: commands.Context, page : int = 1):
        player: Player = Player.GetPlayer(ctx.author.id)
        pages = player.inventory.ToPages()
        page = max(1, page)
        page = min(page, len(pages))
        page -= 1
        embed = discord.Embed(
        title="💼 Inventory 💼",
        description= pages[page],
        color=discord.Color.dark_teal(),
        )
        embed.add_field(name="\u200b", value=f"**Balance:**`{CURRENCY_SYMBOL} {player.balance}`")
        embed.set_footer(text=f"({page + 1}/{len(pages)}) pages")
        await ctx.send(embed=embed)

    @commands.command()
    @ErrorMessage("\n👋 **Use this:**  \n\n**$Shop** `optional: page number`")
    async def Shop(self, ctx: commands.Context, page : int = 1):
        """opens up the global shop."""
        pages = GLOBAL_SHOP.ToPages()
        page = max(1, page)
        page = min(page, len(pages))
        page -= 1
        embed = discord.Embed(
        title="💷 Shop 💷",
        description=pages[page],
        color=discord.Color.dark_teal(),
        )
        embed.set_footer(text=f"({page + 1}/{len(pages)}) pages")
        await ctx.send(embed=embed)

    @commands.command()
    @ErrorMessage("\n👋 **Use this:**  \n\n**$Sell** `id | name of item` `amount` `price`")
    async def Sell(self, ctx: commands.Context, *args : str):
        """puts up the given item on auction in the $shop"""
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="💷 Selling 💷",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(embed=embed)

        args : list = ConvertItemList(args)
        if len(args) == 2:
            if isinstance(args[1], int):
                args.append(1)

        if len(args) != 3:
            await ReplyWith("\nError: **Use this:**  \n\n**$Sell** `id | name of item` `amount` `price`")
            return
        
        id, price, amount = args

        if amount <= 0:
            await ReplyWith(f"Cannot sell `x{amount}` amount!")
            return
        if price < 0:
            await ReplyWith(f"Cannot sell `{CURRENCY_SYMBOL}{price}` price!")
            return

        player = Player.GetPlayer(id = ctx.author.id)
        item = Item.GetItem(id)
        itemCount = player.inventory.GetItemCount(item=item)

        if itemCount == 0 or itemCount < amount: 
            await ReplyWith(f"Cannot sell [{item}] because you do not have `x{amount}`!")
            return
            
        sale = Sale(item=item, amount=amount, price=price, seller=player)
        GLOBAL_SHOP.AddSale(sale=sale)
        player.inventory.RemoveItem(item=item, amount=amount)
        await ReplyWith(f"{sale.item} `x{sale.amount}` **for** `{CURRENCY_SYMBOL}{sale.price}` is now in the shop `🎉`! ")

    @commands.command()
    @ErrorMessage("\n👋 **Use this:**  \n\n**$CancelSale** `sale id`")
    async def CancelSale(self, ctx: commands.Context, sale_id : int):
        """cancels a sale you put up, must specify which one with the sale_id (the number inside the [] brackets)"""
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="💷 Selling 💷",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(embed=embed)

        if not GLOBAL_SHOP.HasSale(sale_id): 
            await ReplyWith("That sale does not exist!")
            return
        sale = GLOBAL_SHOP.GetSale(sale_id)
        if not str(sale.seller.id) == str(ctx.author.id):
            await ReplyWith("That sale is not yours!")
            return
        sale.Cancel()
        await ReplyWith(f"`✔️\u200b` successfully **cancelled**:\n\n {sale}")

    @commands.command()
    @ErrorMessage("\n👋 **Use this:**  \n\n**$Buy** `sale id`")
    async def buy(self, ctx: commands.Context, sale_id : str):
        """Buys an item from the $shop. The sale_id is the corresponding number inside the [] brackets in the shop"""
        sale = GLOBAL_SHOP.GetSale(sale_id.upper())
        
        user = Player.GetPlayer(id = ctx.author.id)
        if sale.seller == user:
            await ctx.reply(content="HEY! stop that. you cannot buy your own items....")
            return
        sale.Buy(client=user)
        embed = discord.Embed(
        title="💷 Selling 💷",
        description=f"You purchased {sale.item} `x{sale.amount}` **for** `{CURRENCY_SYMBOL}{sale.price}` `🎉`!",
        color=discord.Color.dark_teal(),
        )
        await ctx.send(content=f"<@{ctx.author.id}> <@{sale.seller.id}>", embed=embed)
        
    
    @commands.command()
    async def selling(self, ctx: commands.Context, page : int = 1):
        """Shows all the items you are selling"""
        items_for_sale = dict(enumerate(GLOBAL_SHOP.GetAllSalesFor(user = Player.GetPlayer(id = ctx.author.id))))
        pages = GLOBAL_SHOP.__ToPages__(items_for_sale)
        page = max(1, page)
        page = min(page, len(pages))
        page -= 1
        embed = discord.Embed(
        title="💷 My items for sale 💷",
        description=pages[page],
        color=discord.Color.dark_teal(),
        )
        embed.set_footer(text=f"({page + 1}/{len(pages)}) pages")
        await ctx.send(embed=embed)

    @commands.command()
    @ErrorMessage("\n👋 **Use this:**  \n\n**$Gift** `User` `id | name` `amount `...")
    async def Gift(self, ctx: commands.Context, user:  discord.Member, *items: str):
        """Gifts the specified user any items you have"""
        items = ConvertItemList(items=items)
        async def ReplyWith(text : str, content = ""):
            embed = discord.Embed(
            title="🎁 Gifting 🎁",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(content=content,embed=embed)

        if len(items) % 2 != 0 or len(items) == 0:
            await ctx.reply(content="⚙️ Error: Use **$Gift `user` `id | name` `amount` `id | name` `amount` ...** \u200b\u200b⚙️")
            return

        items_to_give : dict[Item, int] = {}

        sender = Player.GetPlayer(id = ctx.author.id)
        recipient : Player = Player.GetPlayer(user.id)
        if len(items) != 0:
            for id,amount in zip(items[0::2], items[1::2]):
                amount = int(amount)
                item = Item.GetItem(id=id)
                if amount <= 0:
                    await ReplyWith(f"⚙️ Error: Amount (`x{amount}`) must be greater than 0! \u200b\u200b⚙️", f"<@{sender.id}>")
                    return
                if not sender.inventory.HasAmount(item, amount):
                    await ReplyWith(f"⚙️ Error: You do not have `x{amount}` of {item} \u200b\u200b⚙️", f"<@{sender.id}>")
                    return
                items_to_give[item] = amount

        sender.Gift(recipient= recipient, items = items_to_give)
        text = ""
        for item in items_to_give:
            text += f'-> {item} `x`{items_to_give[item]}\n'
        await ReplyWith(f"`🎁`**Congrats**`🎁`\n\nThe items:\n{text}\n\n have been `🎁gifted🎁` to you by **{sender.name}**! ", f"<@{recipient.id}>" )


    @commands.command()
    async def Trade(self, ctx: commands.Context,  *items : str):
        """Starts up a trade post with the specified items"""
        items = ConvertItemList(items)
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="💷 Trading 💷",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(embed=embed)

        user = Player.GetPlayer(id = ctx.author.id)
        if IsTrading(user=user):
            await ReplyWith("You are already in a trade!")
            return

        if len(items) % 2 != 0:
            await ReplyWith("⚙️ Error: Use **$Trade `id | name` `amount` `id | name` `amount` ...** \u200b\u200b⚙️")
            return
        if len(items[0::2]) > ITEMS_PER_TRADE_LIMIT:
            await ReplyWith(f"⚙️ Error: You are trading too many items! maximum allowed: {ITEMS_PER_TRADE_LIMIT} \u200b\u200b⚙️")
            return     

        items_trading : dict[Item, int] = {}
        if len(items) != 0:
            for id,amount in zip(items[0::2], items[1::2]):
                amount = int(amount)
                item = Item.GetItem(id=id)
                if amount <= 0:
                    await ReplyWith(f"⚙️ Error: Amount (`x{amount}`) must be greater than 0! \u200b\u200b⚙️")
                    return
                if not user.inventory.HasAmount(item, amount):
                    await ReplyWith(f"⚙️ Error: You do not have `x{amount}` of {item} \u200b\u200b⚙️")
                    return
                items_trading[item] = amount
            
            user.inventory.RemoveItems(items=items_trading)
        ######## CREATE TRADE MESSAGE ########
        embed = discord.Embed(
        title=f"`🎉` **User {user.name} is trading!** `🎉`",
        description= "Items on Trade: ",
        color=discord.Color.dark_teal(),
        )
        embed.add_field(name="\u200b", value=Inventory.CreatePageFrom(items=items_trading))
        embed.add_field(inline=False,name="\u200b", value=f"\n`🎉` To Trade, reply with **$AcceptWith** `id | name` `amount`... `🎉`")
        msg = await ctx.send(embed=embed)
        ######################################
        
        PendingTrade(Items_on_trade=items_trading, seller=user, possible_traders=[], id = msg.id)

    @commands.command()
    async def AcceptWith(self, ctx: commands.Context,  *items : str):
        """"Will attempt to provide an offer to the trade that you have replied to! do not forget to reply to an offer, don't only use the command!"""
        items = ConvertItemList(items)
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="💷 Trading 💷",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(embed=embed)

        user = Player.GetPlayer(id = ctx.author.id)

        if IsTrading(user=user):
          await ReplyWith("You are already in a trade!")
          return

        msg = ctx.message

        if msg.reference == None:
            await ReplyWith("You must reply to a trade post when running this command!")
            return
        if not PendingTrade.Has(id = msg.reference.message_id):
            await ReplyWith("You must reply to a trade post when running this command!")
            return       

        trade = PendingTrade.Get(msg.reference.message_id)

        if not trade.CanTrade(Trader=Player.GetPlayer(id=ctx.author.id)):
            await ReplyWith("You are not allowed to trade in this particular trading post!")
            return

        if  len(items) % 2 != 0:
            await ReplyWith("⚙️ Error! Use while replying to a trade post: **$AcceptWith `id | name` `amount` `id | name` `amount` ...** \u200b\u200b⚙️")
            return
        if len(items) > ITEMS_PER_TRADE_LIMIT:
            await ReplyWith(f"⚙️ Error: You are trading too many items! maximum allowed: {ITEMS_PER_TRADE_LIMIT} \u200b\u200b⚙️")
            return     

        items_trading : dict[Item, int] = {}
        if len(items) != 0:
            for id,amount in zip(items[0::2], items[1::2]):
                amount = int(amount)
                item = Item.GetItem(id=id)
                if amount <= 0:
                    await ReplyWith(f"⚙️ Error: Amount (`x{amount}`) must be greater than 0! \u200b\u200b⚙️")
                    return
                if not user.inventory.HasAmount(item, amount):
                    await ReplyWith(f"⚙️ Error: You do not have `x{amount}` of {item} \u200b\u200b⚙️")
                    return
                items_trading[item] = amount
        
            user.inventory.RemoveItems(items=items_trading)

        trade = trade.ConvertToTrade(Trader=user, items=items_trading)

        ######## CREATE TRADE MESSAGE ########
        embed = discord.Embed(
        title="💷 Trading 💷",
        description= f"`🎉` **User {user} accepted trade with {trade.UserOne}!** `🎉`",
        color=discord.Color.dark_teal(),
        )
        embed.add_field(name=f"{trade.UserOne} is Trading: ", value=Inventory.CreatePageFrom(items=trade.UserOneItems))
        embed.add_field(name=f"{user} is Trading: ", value=Inventory.CreatePageFrom(items=items_trading))
        embed.add_field(inline=False, name=f"\u200b", value=f"**{trade.UserOne}** ! reply with `$accept` to confirm trade!")
        await ctx.send(content=f"<@{trade.UserOne.id}>",embed=embed)
        ######################################

    @commands.command()
    async def CancelTrade(self, ctx: commands.Context):
        """"Will cancel the trade you are in!"""
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="💷 Trading 💷",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.reply(embed=embed)
        user = Player.GetPlayer(ctx.author.id)
        trade = GetAnyTradeInvolving(user)
        trade.Cancel()
        await ReplyWith("`👍`\n Successfully cancelled the trade `✔️` ")

    @commands.command()
    async def accept(self, ctx: commands.Context):
        """"Attempts to accept the trade offer that is going on"""
        user = Player.GetPlayer(ctx.author.id)
        trade = Trade.GetTradeBy(user=user)
        trade.confirm()
        embed = discord.Embed(
            title="💷 Trading 💷",
            description= "`👍` Successfully completed the trade `👍`\n\n ",
            color=discord.Color.dark_teal(),
            )
        embed.add_field(name=f"{trade.UserOne} recieved: ", value=Inventory.CreatePageFrom(items=trade.UserTwoItems))
        embed.add_field(name=f"{trade.UserTwo} recieved: ", value=Inventory.CreatePageFrom(items=trade.UserOneItems))
        await ctx.reply(embed=embed, content=f"<@{trade.UserOne.id}> <@{trade.UserTwo.id}>")

    @commands.command()
    async def hash(self, ctx: commands.Context,  *text : str):
        """hashes the given text"""
        try:
            text = " ".join(text)
            await ctx.reply(content=f"the hash is: `{hash(text)}`")
        except:
            await ctx.reply(content=f"could not hash `{text}` !!")

    @commands.command()
    async def discard(self, ctx: commands.Context,  *items : str):
        """will sell the items for $1 each"""
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="💷 Discarding 💷",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(content=f"<@{ctx.author.id}>", embed=embed)
        items = ConvertItemList(items)
        if  len(items) % 2 != 0 or len(items) == 0:
            await ReplyWith("⚙️ Error! Use **$discard** `id | name` `amount`...⚙️")
            return

        player = Player.GetPlayer(id = ctx.author.id)
        
        items_to_sell = {}
        money_gained = 0
        for id,amount in zip(items[0::2], items[1::2]):
            amount = int(amount)
            item = Item.GetItem(id=id)
            if amount <= 0:
                await ReplyWith(f"⚙️ Error: Amount (`x{amount}`) must be greater than 0! \u200b\u200b⚙️")
                return
            if not player.inventory.HasAmount(item, amount):
                await ReplyWith(f"⚙️ Error: You do not have `x{amount}` of {item} \u200b\u200b⚙️")
                return

            items_to_sell[item] = amount
            money_gained += amount * 1

        player.inventory.RemoveItems(items_to_sell)
        player.balance += money_gained
        await ReplyWith(f"You have discarded `{money_gained}` items and gained `💰{money_gained}` !")

        


    @commands.command()
    async def AcceptWith(self, ctx: commands.Context,  *items : str):
        """"Will attempt to provide an offer to the trade that you have replied to! do not forget to reply to an offer, don't only use the command!"""
        items = ConvertItemList(items)
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="💷 Trading 💷",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(embed=embed)

        user = Player.GetPlayer(id = ctx.author.id)

        if IsTrading(user=user):
          await ReplyWith("You are already in a trade!")
          return

        msg = ctx.message

        if msg.reference == None:
            await ReplyWith("You must reply to a trade post when running this command!")
            return
        if not PendingTrade.Has(id = msg.reference.message_id):
            await ReplyWith("You must reply to a trade post when running this command!")
            return       

        trade = PendingTrade.Get(msg.reference.message_id)

        if not trade.CanTrade(Trader=Player.GetPlayer(id=ctx.author.id)):
            await ReplyWith("You are not allowed to trade in this particular trading post!")
            return

        if  len(items) % 2 != 0:
            await ReplyWith("⚙️ Error! Use while replying to a trade post: **$AcceptWith `id | name` `amount` `id | name` `amount` ...** \u200b\u200b⚙️")
            return
        if len(items) > ITEMS_PER_TRADE_LIMIT:
            await ReplyWith(f"⚙️ Error: You are trading too many items! maximum allowed: {ITEMS_PER_TRADE_LIMIT} \u200b\u200b⚙️")
            return     

        items_trading : dict[Item, int] = {}
        if len(items) != 0:
            for id,amount in zip(items[0::2], items[1::2]):
                amount = int(amount)
                item = Item.GetItem(id=id)
                if amount <= 0:
                    await ReplyWith(f"⚙️ Error: Amount (`x{amount}`) must be greater than 0! \u200b\u200b⚙️")
                    return
                if not user.inventory.HasAmount(item, amount):
                    await ReplyWith(f"⚙️ Error: You do not have `x{amount}` of {item} \u200b\u200b⚙️")
                    return
                items_trading[item] = amount
        
            user.inventory.RemoveItems(items=items_trading)

        trade = trade.ConvertToTrade(Trader=user, items=items_trading)

        ######## CREATE TRADE MESSAGE ########
        embed = discord.Embed(
        title="💷 Trading 💷",
        description= f"`🎉` **User {user} accepted trade with {trade.UserOne}!** `🎉`",
        color=discord.Color.dark_teal(),
        )
        embed.add_field(name=f"{trade.UserOne} is Trading: ", value=Inventory.CreatePageFrom(items=trade.UserOneItems))
        embed.add_field(name=f"{user} is Trading: ", value=Inventory.CreatePageFrom(items=items_trading))
        embed.add_field(inline=False, name=f"\u200b", value=f"**{trade.UserOne}** ! reply with `$accept` to confirm trade!")
        await ctx.send(content=f"<@{trade.UserOne.id}>",embed=embed)
        ######################################


    @commands.command()
    async def use(self, ctx: commands.Context,  *items : str):
        """"Will attempt to use the item!"""
        items = ConvertItemList(items)
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="💷 Using 💷",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(embed=embed)

        user = Player.GetPlayer(id = ctx.author.id)

        if  len(items) % 2 != 0 and len(items) != 0:
            await ReplyWith("⚙️ Error! Use while replying to a trade post: **$use `id | name` `amount`  ...** \u200b\u200b⚙️")
            return

        if len(items) != 0:
            for id,amount in zip(items[0::2], items[1::2]):
                amount = int(amount)
                item = Item.GetItem(id=id)
                if amount <= 0:
                    await ReplyWith(f"⚙️ Error: Amount (`x{amount}`) must be greater than 0! \u200b\u200b⚙️")
                    return
                if not user.inventory.HasAmount(item, amount):
                    await ReplyWith(f"⚙️ Error: You do not have `x{amount}` of {item} \u200b\u200b⚙️")
                    return
                
                name = item.name.lower()
                if not name in ['lootbox']:
                    await ReplyWith(f"⚙️ Error: {item} is not a `usable` item! \u200b\u200b⚙️")
                    return
                
                if name == 'lootbox':
                    await ReplyWith(f"📦 Attempting to open {amount} lootboxes! 📦")
                    for _ in range(amount):
                        amount_to_give = random.randint(1,5)
                        items_to_give = [Item.GetRandomItem() for _ in range(amount_to_give)]
                        hidden_content = ["**->** <a:loading:794672829202300939>" for _ in range(amount_to_give)]
                        embed = discord.Embed(
                        title="📦 Opening Lootbox 📦",
                        description= "\n\n".join(hidden_content),
                        color=discord.Color.dark_teal(),
                        )
                        msg = await ctx.reply(embed=embed)
                        for i in range(amount_to_give):
                            await asyncio.sleep(0.8)
                            hidden_content[i] = f"**->** {items_to_give[i]}"
                            embed.description = "\n\n".join(hidden_content)
                            user.inventory.AddItem(items_to_give[i])
                            await msg.edit(embed=embed)



                user.inventory.RemoveItem(item=item, amount=amount)

def setup(bot):
    bot.add_cog(PlayerCommands(bot))