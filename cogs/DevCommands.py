from GameLogic.Trading import Trade
from GameLogic.Bees import BeeStorage
from GameLogic.plants import PlantStorage
import discord

from discord.ext import commands
from GameLogic.Player import Player
from GameLogic.Items import Item
from cogs.PlayerCommands import ConvertItemList
from Utils.Constants import CURRENCY_SYMBOL, GLOBAL_SHOP, OnReactionOnly, OnReactionOnlyOnce, RefreshShop, pretty_time_delta


class DevCommands(commands.Cog):
    '''General Commands'''
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def GiveItem(self, ctx: commands.Context, user : discord.Member, *items : str):
        items = ConvertItemList(items=items)
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="`😈` Dev Tools `😈`",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(content=f"<@{user.id}>",embed=embed)

        if len(items) % 2 != 0 or len(items) == 0:
            await ctx.reply(content="⚙️ Error: Use **$giveitem `user` `id | name` `amount` `id | name` `amount` ...** \u200b\u200b⚙️")
            return

        items_to_give : dict[Item, int] = {}

        for id,amount in zip(items[0::2], items[1::2]):
            amount = int(amount)
            item = Item.GetItem(id=id)
            items_to_give[item] = amount

        player : Player = Player.GetPlayer(user.id)
        player.inventory.AddItems(items=items_to_give)
        text = ""
        for item in items_to_give:
            text += f'-> {item} `x{items_to_give[item]}`\n'
        await ReplyWith(f"`🎉`**Congrats**`🎉`\n\nThe items:\n{text}\n\n have been given to you by the owner! ")

    @commands.is_owner()
    @commands.command()
    async def TakeItem(self, ctx: commands.Context, user : discord.Member, *items : str):
        items = ConvertItemList(items=items)
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="`😈` Dev Tools `😈`",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(content=f"<@{user.id}>",embed=embed)

        if len(items) % 2 != 0 or len(items) == 0:
            await ctx.reply(content="⚙️ Error: Use **$giveitem `user` `id | name` `amount` `id | name` `amount` ...** \u200b\u200b⚙️")
            return

        items_to_take : dict[Item, int] = {}

        for id,amount in zip(items[0::2], items[1::2]):
            amount = int(amount)
            item = Item.GetItem(id=id)
            items_to_take[item] = amount

        player : Player = Player.GetPlayer(user.id)
        player.inventory.RemoveItems(items=items_to_take)
        text = ""
        for item in items_to_take:
            text += f'-> {item} `x{items_to_take[item]}`\n'
        await ReplyWith(f"`🤣`**Congrats**`🤣`\n\nThe items:\n{text}\n\n have been taken away by the owner! ")

    @commands.is_owner()
    @commands.command()
    async def Peek(self, ctx: commands.Context, user : discord.Member, page : int = 1):
        player: Player = Player.GetPlayer(user.id)
        pages = player.inventory.ToPages()
        page = max(1, page)
        page = min(page, len(pages))
        page -= 1
        embed = discord.Embed(
        title="`😈` Dev Tools `😈`",
        description= pages[page],
        color=discord.Color.dark_teal(),
        )
        embed.add_field(name="\u200b", value=f"**Balance:**`{CURRENCY_SYMBOL} {player.balance}`")
        embed.set_footer(text=f"({page + 1}/{len(pages)}) pages")
        await ctx.send(content=f"<@{user.id}>", embed=embed)

    @commands.is_owner()
    @commands.command()
    async def PeekSelling(self, ctx: commands.Context, user : discord.Member, page : int = 1):
        items_for_sale = dict(enumerate(GLOBAL_SHOP.GetAllSalesFor(user = Player.GetPlayer(id = user.id))))
        pages = GLOBAL_SHOP.__ToPages__(items_for_sale)
        page = max(1, page)
        page = min(page, len(pages))
        page -= 1
        embed = discord.Embed(
        title=f"`💷` Dev Tools ({user.name}'s items on sale) `💷`",
        description=pages[page],
        color=discord.Color.dark_teal(),
        )
        embed.set_footer(text=f"({page + 1}/{len(pages)}) pages")
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def cancelSalesFor(self, ctx: commands.Context, user : discord.Member):
        sales = GLOBAL_SHOP.GetAllSalesFor(user = Player.GetPlayer(id = user.id))
        for sale in sales:
            sale.Cancel()
        await ctx.reply(content=f"`💸` `x{len(sales)}` sales for {user.name} have been cancelled! `💸`")

    @commands.is_owner()
    @commands.command()
    async def GiveMoney(self, ctx: commands.Context, user : discord.Member, amount : int = 1):
        player: Player = Player.GetPlayer(user.id)
        player.balance += amount
        embed = discord.Embed(
        title="`😈` Dev Tools `😈`",
        description= f"Given `{CURRENCY_SYMBOL}{amount}` to {player.name}\n\n**NEW Balance:**`{CURRENCY_SYMBOL} {player.balance}`",
        color=discord.Color.dark_teal(),
        )
        await ctx.send(content=f"<@{user.id}>", embed=embed)

    @commands.is_owner()
    @commands.command()
    async def TakeMoney(self, ctx: commands.Context, user : discord.Member, amount : int = 1):
        player: Player = Player.GetPlayer(user.id)
        player.balance -= amount
        embed = discord.Embed(
        title="`💰` Money `💰`",
        description= f"Taken {CURRENCY_SYMBOL} {amount} from {player.name}\n\n**NEW Balance:**`{CURRENCY_SYMBOL} {player.balance}`",
        color=discord.Color.dark_teal(),
        )
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def Clear(self, ctx: commands.Context):
        Player.Clear()
        await ctx.reply(content=f"Cleared {len(Player.PLAYER_REFERENCES)} references.")

    @commands.is_owner()
    @commands.command()
    async def Save(self, ctx: commands.Context):
        Player.Save()
        await ctx.reply(content=f"Saved {len(Player.PLAYER_REFERENCES)} references.")

    @commands.is_owner()
    @commands.command()
    async def SetBeeTime(self, ctx: commands.Context, time : int):
        from Utils.Constants import BEE_DURATION
        await ctx.reply(content=f"Ok. changed bee growth time from {pretty_time_delta(BEE_DURATION.normal_bee)} to {pretty_time_delta(time)}")
        BEE_DURATION.normal_bee = time

    @commands.is_owner()
    @commands.command()
    async def SetSeedTime(self, ctx: commands.Context, time : int):
        from Utils.Constants import SEED_DURATION
        await ctx.reply(content=f"Ok. changed plant growth time from {pretty_time_delta(SEED_DURATION.x_seed)} to {pretty_time_delta(time)}")
        SEED_DURATION.x_seed = time

    @commands.is_owner()
    @commands.command()
    async def CancelAllTrades(self, ctx: commands.Context):
        async def ReplyWith(text : str):
            embed = discord.Embed(
            title="`💷` Selling `💷`",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.send(embed=embed)

        sales = GLOBAL_SHOP.GetAllSales()
        num = len(sales)
        for sale in sales: sale.Cancel()
        await ReplyWith(f"`✔️\u200b` successfully **cancelled**: x{num} sales!")

    @commands.is_owner()
    @commands.command()
    async def ClearInv(self, ctx: commands.Context, user : discord.Member):
        """clears the user's inventory"""
        await ctx.reply(content=f"Ok. cleared {user.mention}'s inventory.")
        Player.GetPlayer(user.id).inventory.Clear()

    @commands.is_owner()
    @commands.command()
    async def Delete(self, ctx: commands.Context, user : discord.Member):
        """Deletes a user from the databases"""
        Player.DeletePlayer(user.id)
        PlantStorage.DeletePlantStorage(user.id)
        GLOBAL_SHOP.DeleteSalesFor(user.id)
        BeeStorage.DeleteBeeStorage(user.id)
        Trade.CancelTradesWith(user.id)
        await ctx.reply(content=f"Ok. deleted {user.mention} from database.")

    @commands.is_owner()
    @commands.command()
    async def RefreshShop(self, ctx: commands.Context):
        """Refreshes the shop automagically"""
        await RefreshShop()
        await ctx.reply(content=f"Ok. refreshed the shop.")

    @commands.is_owner()
    @commands.command()
    async def testing(self, ctx: commands.Context):
        # embed = discord.Embed(
        # title="<:egg:864733603949707295> Incubating <:egg:864733603949707295>",
        # description= f"**Name:** `unknown`\n **Time Left:** `2 days 10 hours 37 minutes... ` <a:loading:794672829202300939>\n **Type:** `Aquatic`",
        # color=discord.Color.dark_teal(),
        # )
        # embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/856734093151698947/864732903169458186/119.png")
        # await ctx.send(embed=embed)

        embed = discord.Embed(
        title="<:SoulStone:864725973379186688> Aquatic Bitch <:SoulStone:864725973379186688>",
        description= f"Level: `1`\n experience: `0/100` \n Type: `Aquatic`",
        color=discord.Color.dark_teal(),
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/829405145112248330/864730506826743868/beest_03.png")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DevCommands(bot))