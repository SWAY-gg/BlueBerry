import disnake
from disnake.ext import commands

import time
import json
from datetime import datetime

import setting.color
from setting.color import EColor

times = datetime.utcnow()
edit = times.strftime("%Y")
utc = "2021 - " + f"{edit}"


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Help", aliases=["help"])
    async def command_help(self, ctx):
        embed = disnake.Embed(
            title=f"**Список всех категорий бота {self.bot.user.name}**",
            color=EColor["DEFAULT"],
        )
        embed.set_thumbnail(url=self.bot.user.avatar)

        embed.add_field(
            name=f"**<:information:918232119015264286> Info**",
            value=f"**>help-info**",
            inline=True,
        )
        embed.add_field(
            name=f"**<:admin:918232122517491772> Admin**",
            value=f"**>help-admin**",
            inline=True,
        )
        embed.add_field(
            name=f"**<:welcome:918232122626564137> Welcome**",
            value=f"**>help-welcome**",
            inline=True,
        )
        embed.add_field(
            name=f"**<:game:918232118662950972> Economy**",
            value=f"**>help-economy**",
            inline=True,
        )
        embed.add_field(
            name=f"**<:support:918232122228088863> Support**",
            value=f"**>help-support**",
            inline=True,
        )
        embed.add_field(
            name=f"**<:fun:918232122244870245> Fun**",
            value=f"**>help-fun**",
            inline=True,
        )

        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )

        await ctx.send(embed=embed)

    @commands.command(name="help-info", aliases=["help-Info"])
    async def command_help_info(self, ctx):
        embed = disnake.Embed(
            description=f"**<:information:918232119015264286> | Список команд категории: 'Info'**",
            color=EColor["DEFAULT"],
        )

        embed.add_field(
            name="ℹ️ **Основная информация**:",
            value=(
                f"**Команда:** `Server Info`\n"
                f"**Использование:** [`>serverinfo`]\n"
                f"**Описание:** [`Полная информация об сервере`]\n\n"
                f"**Команда:** `Help Command`\n"
                f"**Использование:** [`>help`]\n"
                f"**Описание:** [`Список категорий бота`]\n\n"
            ),
        )

        embed.add_field(
            name="👤 **Информация о пользователе и боте**:",
            value=(
                f"**Команда:** `User Info`\n"
                f"**Использование:** [`>userinfo <@member>`]\n"
                f"**Описание:** [`Информация о пользователе!`]\n\n"
                f"**Команда:** `Bot Info`\n"
                f"**Использование:** [`>botinfo`]\n"
                f"**Описание:** [`Информация о состоянии бота`]**"
            ),
        )

        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )

        await ctx.send(embed=embed)

    @commands.command(name="help-admin", aliases=["help-Admin"])
    async def command_help_admin(self, ctx):
        embed = disnake.Embed(
            description=f"**<:admin:918232122517491772> | Список команд категории: 'Admin'**",
            color=EColor["DEFAULT"],
        )

        # Первая группа команд
        embed.add_field(
            name="🛑 **Команды для администраторов**:",
            value=(
                f"**Команда:** `Hban`\n"
                f"**Использование:** [`>HBan <member id>`]\n"
                f"**Описание:** [`Бан пользователя по его ID`]\n\n"
                f"**Команда:** `Kick`\n"
                f"**Использование:** [`>Kick <@member>`]\n"
                f"**Описание:** [`Кик пользователя с сервера`]\n\n"
                f"**Команда:** `Ban`\n"
                f"**Использование:** [`>Ban <@member> <reason>`]\n"
                f"**Описание:** [`Бан пользователя на сервере`]\n\n"
            ),
        )

        embed.add_field(
            name="⚙️ **Управление сервером**:",
            value=(
                f"**Команда:** `Clear`\n"
                f"**Использование:** [`>Clear <count message>`]\n"
                f"**Описание:** [`Очистка чата от сообщений`]\n\n"
                f"**Команда:** `Voice-install`\n"
                f"**Использование:** [`>Voice-install`]\n"
                f"**Описание:** [`Создание кастомного войс канала`]\n\n"
                f"**Команда:** `Say`\n"
                f"**Использование:** [`>Say /t Title /d Description /c WHITE`]\n"
                f"**Описание:** [`Сказать что-либо в чат, при помощи embed`]\n\n"
                f"**Команда:** `SColor`\n"
                f"**Использование:** [`>SColor`]\n"
                f"**Описание:** [`Узнать список цветов для команды say`]**"
            ),
        )

        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )

        await ctx.send(embed=embed)

    @commands.command(name="help-welcome", aliases=["help-Welcome"])
    async def command_help_welcome(self, ctx):
        embed = disnake.Embed(
            description=f"**<:welcome:918232122626564137> | Список команд категории: 'Welcome'**",
            color=EColor["DEFAULT"],
        )

        embed.add_field(
            name="👋 **Приветственные команды**:",
            value=(
                f"**Команда:** `Set Welcome`\n"
                f"**Использование:** [`>Set-welcome <#channel>`]\n"
                f"**Описание:** [`Задать welcome канал для уведомления о новых участниках`]\n\n"
                f"**Команда:** `Del Welcome`\n"
                f"**Использование:** [`>Del-welcome`]\n"
                f"**Описание:** [`Удалить welcome`]\n\n"
                f"**Команда:** `Check`\n"
                f"**Использование:** [`>Check`]\n"
                f"**Описание:** [`Проверка, заданы ли параметры welcome`]\n\n"
            ),
        )

        embed.add_field(
            name="🔑 **Управление ролями для новичков**:",
            value=(
                f"**Команда:** `Set Role`\n"
                f"**Использование:** [`>Set-role <@role>`]\n"
                f"**Описание:** [`Задать роль для выдачи новичкам`]\n\n"
                f"**Команда:** `Del Role`\n"
                f"**Использование:** [`>Del-role`]\n"
                f"**Описание:** [`Удалить роль`]**"
            ),
        )

        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )

        await ctx.send(embed=embed)

    @commands.command(name="help-fun", aliases=["help-Fun"])
    async def command_help_fun(self, ctx):
        embed = disnake.Embed(
            description=f"**<:fun:918232122244870245> | Список команд категории: 'Fun'**",
            color=EColor["DEFAULT"],
        )

        embed.add_field(
            name="🎮 **Развлекательные команды**:",
            value=(
                f"**Команда:** `User Avatar`\n"
                f"**Использование:** [`>Avatar <@member>`]\n"
                f"**Описание:** [`Посмотреть аватарку пользователя в полном размере`]\n\n"
                f"**Команда:** `Hug`\n"
                f"**Использование:** [`>Hug | >Hug <@user>`]\n"
                f"**Описание:** [`Обнять себя/пользователя`]\n\n"
            ),
        )

        embed.add_field(
            name="😜 **Команды для шуток и приколов**:",
            value=(
                f"**Команда:** `Lick`\n"
                f"**Использование:** [`>Lick | >Lick <@user>`]\n"
                f"**Описание:** [`Лизнуть себя/пользователя`]\n\n"
                f"**Команда:** `Slap`\n"
                f"**Использование:** [`>Slap | >Slap <@user>`]\n"
                f"**Описание:** [`Шлёпнуть себя/пользователя`]\n\n"
            ),
        )

        embed.add_field(
            name="🔮 **Игры и гадания**:",
            value=(
                f"**Команда:** `Ball`\n"
                f"**Использование:** [`>Ball <Question>`]\n"
                f"**Описание:** [`Шар гадалка`]**"
            ),
        )

        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )

        await ctx.send(embed=embed)

    @commands.command(name="help-support", aliases=["help-Support"])
    async def command_help_support(self, ctx):
        embed = disnake.Embed(
            description=f"**<:support:918232122228088863> Support | Список команд категории: 'Support'**",
            color=EColor["DEFAULT"],
        )

        embed.add_field(
            name="🛠️ **Команды для поддержки**:",
            value=(
                f"**Команда:** `Report`\n"
                f"**Использование:** [`>Report <TEXT>`]\n"
                f"**Описание:** [`Сообщить создателям бота об ошибках в работе!`]\n\n"
                f"**Команда:** `Feedback`\n"
                f"**Использование:** [`>Feedback <TEXT>`]\n"
                f"**Описание:** [`Поблагодарить создателей бота!`]**"
            ),
        )

        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )

        await ctx.send(embed=embed)

    @commands.command(name="help-economy", aliases=["help-Economy"])
    async def command_help_economy(self, ctx):
        embed = disnake.Embed(
            description=f"**<:game:918232118662950972> Economy | Список команд категории: 'Economy'**",
            color=EColor["DEFAULT"],
        )

        embed.add_field(
            name="💍 **Команды для отношений**:",
            value=(
                f"**Команда:** `Marry`\n"
                f"**Использование:** [`>Marry <@user>`]\n"
                f"**Описание:** [`Свадьба с пользователем`]\n\n"
                f"**Команда:** `Marry Divorce`\n"
                f"**Использование:** [`>Marry-Divorce <@user>`]\n"
                f"**Описание:** [`Развод с пользователем`]**"
            ),
        )

        embed.add_field(
            name="📊 **Команды для статистики**:",
            value=(
                f"**Команда:** `User`\n"
                f"**Использование:** [`>User`]\n"
                f"**Описание:** [`Статистика пользователя`]\n\n"
                f"**Команда:** `Status`\n"
                f"**Использование:** [`>Status <TEXT>`]\n"
                f"**Описание:** [`Задать свой статус`]\n\n"
                f"**Команда:** `Card`\n"
                f"**Использование:** [`>Card`]\n"
                f"**Описание:** [`Карта пользователя`]**"
            ),
        )

        embed.add_field(
            name="💰 **Команды для заработка**:",
            value=(
                f"**Команда:** `Give`\n"
                f"**Использование:** [`>Give <@user> <Ammount>`]\n"
                f"**Описание:** [`Передать деньги пользователю`]\n\n"
                f"**Команда:** `Daily`\n"
                f"**Использование:** [`>Daily`]\n"
                f"**Описание:** [`Ежедневные бонусы`]\n\n"
                f"**Команда:** `Top`\n"
                f"**Использование:** [`>Top`]\n"
                f"**Описание:** [`Топ пользователей по балансу`]**"
            ),
        )

        embed.add_field(
            name="🎲 **Команды для ставок и покупок**:",
            value=(
                f"**Команда:** `Bet`\n"
                f"**Использование:** [`>Bet <Ammount>`]\n"
                f"**Описание:** [`Сделать ставку`]\n\n"
                f"**Команда:** `Shop`\n"
                f"**Использование:** [`>Shop`]\n"
                f"**Описание:** [`Магазин ролей сервера`]\n\n"
                f"**Команда:** `Buy`\n"
                f"**Использование:** [`>Buy <@role>`]\n"
                f"**Описание:** [`Купить роль за монеты`]**"
            ),
        )

        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
