################Imports##############################
import discord, time

from discord.ext import commands
from GameLogic.Player import Player
from GameLogic.Items import Item
from GameLogic.Bees import BeeStorage, NormalBee

from Utils.Constants import pretty_time_delta

#####################################################


class BeeCommands(commands.Cog):
    '''Bee Commands'''
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command()
    async def GrowBee(self, ctx: commands.Context, *bees : str):
        async def ReplyWith(text):
            embed = discord.Embed(
            title="🐝Beekeeping🐝",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.reply(embed=embed)
        if len(bees) == 0:
            await ReplyWith( f"Error! use **$growbee** `bee name`!" )
            return
        player = Player.GetPlayer(id = ctx.author.id)
        honey = Item.GetItem(id = "honey")
        if not player.inventory.HasItem(item=honey):
            await ReplyWith( f"Error! You do not have any {honey} !" )
            return
        bees = " ".join(bees)
        bee = Item.GetItem(bees)
        if not player.inventory.HasItem(item=bee):
            await ReplyWith( f"Error! You do not have any {bee} !" )
            return

        if bee.name.lower() == "bee":
            bee_growing = NormalBee(user=Player.GetPlayer(ctx.author.id))
            player.inventory.RemoveItem(bee)
            player.inventory.RemoveItem(honey)
            await ReplyWith(f"\n\n {bee} will take `{pretty_time_delta( int(bee_growing.finishing_time - time.time()) )}` to finish! \n\n use `$checkbees` to check on it!")
            return

        await ReplyWith( f"Error! you should not have reached this point..." )

    @commands.command()
    async def CheckBees(self, ctx: commands.Context):
        storage = BeeStorage.GetBeeStorage(id = ctx.author.id)
        await storage.CheckForCompletion(ctx)

        embed = discord.Embed(
        title="🐝Beekeeping🐝",
        description= "Bees In Storage: ",
        color=discord.Color.dark_teal(),
        )

        for slot in storage.storage:
            embed.add_field(inline=False, name="\u200b", value=f"**->** \u200b {storage.storage[slot]}") #**[Slot {slot + 1}]\u200b

        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(BeeCommands(bot))