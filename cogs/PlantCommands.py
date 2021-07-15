################Imports##############################
import time
import discord

from discord.ext import commands
from GameLogic.Player import Player
from GameLogic.Items import Item
from GameLogic.plants import PlantStorage, XSeedPlant

from Utils.Constants import pretty_time_delta

#####################################################


class PlantCommands(commands.Cog):
    '''Plant Commands'''
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command()
    async def Plant(self, ctx: commands.Context, *seed : str):
        async def ReplyWith(text):
            embed = discord.Embed(
            title="💠Plants💠",
            description= text,
            color=discord.Color.dark_teal(),
            )
            await ctx.reply(embed=embed)
        if len(seed) == 0:
            await ReplyWith( f"Error! use **$Plant** `plantable item`!" )
            return

        player = Player.GetPlayer(id = ctx.author.id)
        water_droplet = Item.GetItem(id = "water droplet")
        if not player.inventory.HasItem(item=water_droplet):
            await ReplyWith( f"Error! You do not have any {water_droplet} !" )
            return
        seed = " ".join(seed)
        seed_item = Item.GetItem(id = seed)
        if not player.inventory.HasItem(item=seed_item):
            await ReplyWith( f"Error! You do not have any {seed_item} !" )
            return

        if seed_item.name == "X Seed":
            plant = XSeedPlant(user=Player.GetPlayer(ctx.author.id))
            player.inventory.RemoveItem(seed_item)
            player.inventory.RemoveItem(water_droplet)
            await ReplyWith(f"Successfully planted {seed_item} !\n\n It will take `{pretty_time_delta( int(plant.finishing_time - time.time()) )}` to finish! \n\n use `$checkplants` to check on it!")
            return

        await ReplyWith( f"Error! {seed_item} is not a plantable item! !" )

    @commands.command()
    async def CheckPlants(self, ctx: commands.Context):
        storage = PlantStorage.GetPlantStorage(id = ctx.author.id )
        await storage.CheckForCompletion(ctx)

        embed = discord.Embed(
        title="💠Plants💠",
        description= "Plants In Storage: ",
        color=discord.Color.dark_teal(),
        )
        for slot in storage.storage:
            embed.add_field(inline=False, name="\u200b", value=f"**->** \u200b {storage.storage[slot]}") #**[Slot {slot + 1}]\u200b 

        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(PlantCommands(bot))