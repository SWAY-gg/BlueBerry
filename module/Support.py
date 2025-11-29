import disnake
from disnake.ext import commands
from disnake.ext.commands import Cog, BucketType, cooldown  

import setting.color
from setting.color import EColor

server = '[Серверу Теx. Поддержки](YOUR_SERVER_INVITE_LINK)'

#Class Support
class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_feedback_or_report(self, ctx, msg: str, report_type: str):
        confirmation_embed = disnake.Embed(
            title=f"{report_type} отправлен!",
            description=f"**Спасибо за вашу поддержку! Мы рассмотрим вашу заявку в скором времени.\n Так же вы можете присоеденится к {server}**",
            color=EColor["DEFAULT"]
        )
        await ctx.send(embed=confirmation_embed)
        
        channel = self.bot.get_channel(YOUR_CHANNEL_ID)
        emb = disnake.Embed(
            description=(
                f"⏵ **{report_type} от `{ctx.message.author.name}#{ctx.message.author.discriminator}` \n\n"
                f"{msg}**"
            ), 
            color=EColor["DEFAULT"]
        )
        await channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = disnake.Embed(
            color=EColor["DEFAULT"], 
            title="BlueBerry - Information!", 
            description=(
                f"Доброго времени суток!\n\n"
                f"Вы получили это сообщение, т.к. на ваш сервер `{guild.name}` был добавлен BlueBerry!\n"
                f"Это чисто информативное сообщение, сделанное для того, чтобы вы знали немного больше о том, чем пользуетесь."
            )
        )
        embed.add_field(name="Полезная информация:", value=(
            f"**Справка по командам:** [`>help`]\n"
            f"**Создатель бота:** [`sweet1e42`]\n"
            f"**Префикс:** [`>`]\n"
        ))
        embed.add_field(name="Поддержка:", value=(
            f"**Если нашли ошибку в работе бота:\n[`>Report <TEXT>`]**\n"
            f"**Оставить отзыв напрямую:\n[`>FeedBack <TEXT>`]**"
        ))
        embed.set_footer(
            text=f'{self.bot.user.name} | © 2021 Все права защищены!',
            icon_url=self.bot.user.avatar.url
        )
        try:
            await guild.owner.send(embed=embed)
        except disnake.Forbidden:
            pass

        channel = self.bot.get_channel(YOUR_CHANNEL_ID)
        emb = disnake.Embed(
            color=EColor["DEFAULT"], 
            title=f"Бот присоединился к серверу: {guild.name}", 
            description=(
                f"**Информация о сервере:** \n"
                f"**Сервер:** `{guild.name}` \n"
                f"**Владелец сервера:** `{guild.owner}` \n"
                f"**ID сервера:** `{guild.id}`"
            )
        ).set_thumbnail(url=guild.icon_url)
        await channel.send(embed=emb)

    @commands.command(name="Report", aliases=["report"])
    @cooldown(1, 3600, BucketType.user)
    async def command_report(self, ctx, *, msg: str):
        await self.send_feedback_or_report(ctx, msg, "Bag-Report")

    @commands.command(name="FeedBack", aliases=["Feedback", "feedback"])
    @cooldown(1, 3600, BucketType.user)
    async def command_feedback(self, ctx, *, msg: str):
        await self.send_feedback_or_report(ctx, msg, "FeedBack")

def setup(bot):
    bot.add_cog(Support(bot))
