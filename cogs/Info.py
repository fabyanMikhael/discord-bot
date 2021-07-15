import discord,datetime, platform

from discord.ext import commands
from Utils.Constants import pretty_time_delta

class Info(commands.Cog):
    '''Info Commands'''
    def __init__(self, bot):
        self.bot = bot
        self.start = datetime.datetime.now()


    @commands.command()
    async def info(self, ctx):
        """``info`` info on Arrodes"""

        uptime = pretty_time_delta(
            (datetime.datetime.now() - self.start).total_seconds()
        )

        embed = discord.Embed(
            title="Arrodes Info",
            description=f"```py\nUptime: {uptime}```",
            color=discord.Color.teal(),
        )

        embed.add_field(
            name="Discord Presence",
            value=f"```py\nServers: {len(self.bot.guilds):,}\nChannels: {sum([len(g.channels) for g in self.bot.guilds]):,}\nUsers: {sum([len(g.members) for g in self.bot.guilds]):,}\nShards: {self.bot.shard_count}```",
            inline=False,
        )
        embed.add_field(
            name="System",
            value=f"```py\nLatency: {round(self.bot.latency * 1000)}ms\nPlatform: {platform.system()}```",
            inline=False,
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url,
        )
        await ctx.send(embed=embed)


    @commands.command()
    async def help(self, ctx, *, query: commands.clean_content = None):
        """[category|command]|||Help for every category and command."""
        p = "$"

        embed = discord.Embed(color=discord.Color.blurple(), description="", title="")
        embed.set_author(
            name="Arrodes Help",
        )
        if query is None:
            embed.description += (
                f"```yaml\nUse {p}help <category> to find out more about it.```"
            )
            categs = []
            for cog_name in self.bot.cogs:
                    cmnds = self.bot.cogs[cog_name].get_commands()
                    categs.append(f"• `{cog_name}`― {self.bot.cogs[cog_name].__doc__}")
            embed.title = f"Command Categories"
            embed.add_field(name=f"{len(categs)} Categories", value="\n".join(categs))
        else:
            cog_names = {cog.lower(): cog for cog in self.bot.cogs}
            command_names = [c.name for c in self.bot.commands] + [
                y
                for x in [
                    [alias for alias in cmnd.aliases] for cmnd in self.bot.commands
                ]
                for y in x
            ]
            query = query.lower()

            if query in cog_names:
                cog_name = cog_names[query]
                _cog = self.bot.get_cog(cog_name)
                commands = _cog.get_commands()
                embed.description += (
                    f"```yaml\nUse {p}help <command> to find out more about it.```"
                )

                embed.title = f"`{cog_name}` Commands"

                val = [f"`{c.name}`" for c in commands]
                if val:
                    embed.add_field(
                        name=f"{len(commands)} Commands",
                        value=", ".join(val),
                        inline=False,
                    )
            elif query in command_names:
                embed.title = f"`{p}{query}`"

                for command in self.bot.commands:
                    if query == command.name or query in command.aliases:
                        break

                h = command.help.split("|||")
                embed.description += f"{h[1]}\n\n**Usage**\n> `{p}{query} {h[0]}`"
                if len(command.aliases) > 0:
                    aliases = ", ".join(
                        [f"`{c}`" for c in command.aliases] + [f"`{command.name}`"]
                    )
                    embed.description += f"\n\n**Aliases**\n> {aliases}"

            else:
                embed.title = "Error"
                embed.description += f"```yaml\nI couldn't find help for that.```\n> `{query}` is not a category or command"

                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/emojis/651694663962722304.gif?v=1"
                )


        await ctx.reply(embed=embed, mention_author=False)

def setup(bot):
    bot.add_cog(Info(bot))