import disnake
from disnake import Embed
from disnake.ext import commands
from datetime import datetime
import time

# Your log channel and bot owner ID
LOG_CHANNEL_ID  = 0   # Log channel where errors will be sent
OWNER_ID        = 0   # Your user ID

# Time
utc = datetime.utcnow()
Times = int(time.mktime(utc.timetuple()))

async def cmderror(ctx, error):
    error_message = f"Ошибка на сервере {ctx.guild.name}\n"
    error_message += f"Команда: {ctx.command.qualified_name if ctx.command else 'Неизвестная команда'}\n"
    error_message += f"Описание: {str(error)}"

    # Prepare log embed
    log_embed = disnake.Embed(
        description=f"**❌ Ошибка на сервере {ctx.guild.name}**",
        color=0xFF0000 
    )
    log_embed.add_field(name="Логи:", value=f"```{error_message}```")
    log_embed.add_field(name="Время:", value=f"<t:{Times}:D><t:{Times}:t>")

    log_channel = await ctx.bot.fetch_channel(LOG_CHANNEL_ID)
    await log_channel.send(embed=log_embed)

    return "Произошла непредвиденная ошибка. Разработчик уже уведомлён."

class Error(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.command is None or ctx.command.has_error_handler() or ctx.command.hidden:
            return

        try:
            user_message = await cmderror(ctx, error)
            embed = Embed(color=0xFF0000, description=f'❌ | {user_message}')
            embed.set_author(name=ctx.author.name + '#' + ctx.author.discriminator, icon_url=ctx.author.avatar)
            await ctx.reply(embed=embed, delete_after=30)
        except Exception as e:
            print(f"Error in error handler: {e}")

class SlashError(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        try:
            user_message = await cmderror(inter, error)
            embed = Embed(color=0xFF0000, description=f'❌ | {user_message}')
            embed.set_author(name=inter.author.name + '#' + inter.author.discriminator, icon_url=inter.author.avatar)
            await inter.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error in Slash command: {e}")
            await inter.response.send_message("Произошла ошибка при обработке команды.", ephemeral=True)

def setup(bot):
    bot.add_cog(Error(bot))
    bot.add_cog(SlashError(bot))
