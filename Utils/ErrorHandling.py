import discord, asyncio
from discord.ext.commands import Context
from discord.ext.commands import Bot
from discord.ext.commands.errors import CommandError

#ERRORS#
class ShopError(CommandError): pass
class TradeError(CommandError): pass
class InventoryError(CommandError): pass
HANDLED_ERRORS = (ShopError, TradeError, InventoryError)
########

def ErrorMessage (description : str):
    def decorator(func):
        func.ErrorMessage  = description
        return func
    return decorator
    
async def command_error(ctx: Context, error: CommandError):
    
    embed = discord.Embed(
        title="⚙️ ERROR ⚙️",
        description= f"{error}",
        color=discord.Color.dark_teal(),
        )
    await ctx.reply(embed=embed)
    return

    if ctx.command == None:
        command_name = ctx.invoked_with
        bot : Bot = ctx.bot
        command_name: str = command_name.lower()
        suggestion = ""
        for existing_command in bot.commands:
            existing_command = existing_command.name
            existing: str = existing_command.lower()
            if existing in command_name or command_name in existing:
                suggestion = f"\n\nDid you mean `${existing_command}` ?"
                break
            asyncio.sleep(0)

        embed = discord.Embed(
            title="⚙️ Suggested ⚙️",
            description= f"{command_name} does not exist! {suggestion}",
            color=discord.Color.dark_teal(),
            )
        await ctx.reply(embed=embed)
        return

    if isinstance(error, HANDLED_ERRORS):
        embed = discord.Embed(
            title="⚙️ Error ⚙️",
            description= error,
            color=discord.Color.dark_teal(),
            )
        await ctx.send(embed=embed)
        return
    if "ErrorMessage" in ctx.command.callback.__dict__:
        embed = discord.Embed(
            title="⚙️ Error ⚙️",
            description= ctx.command.callback.ErrorMessage,
            color=discord.Color.dark_teal(),
            )
        await ctx.send(embed=embed)
    else :
        embed = discord.Embed(
            title="⚙️ Error ⚙️",
            description= error,
            color=discord.Color.dark_teal(),
            )
        await ctx.send(embed=embed)