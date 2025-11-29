import disnake
from disnake.ext import commands

import json
import time
import psutil
from datetime import datetime, timedelta
from timeit import default_timer as timer

import setting.color
from setting.color import EColor

invite_link = "[Add Bot](YOUR_INVITE_BOT_LINK)"

times = datetime.utcnow()
edit = times.strftime("%Y")
utc = f"2021 - {edit}"


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.process = psutil.Process()
        self.process.cpu_percent()
        self.uptime = 0

    @commands.command(name="Serverinfo", aliases=["serverinfo"])
    async def command_serverinfo(self, ctx):
        members = ctx.guild.members
        created_at = int(ctx.guild.created_at.timestamp())

        # Counting status
        online = sum(1 for x in members if x.status == disnake.Status.online)
        idle = sum(1 for x in members if x.status == disnake.Status.idle)
        dnd = sum(1 for x in members if x.status == disnake.Status.dnd)
        offline = sum(1 for x in members if x.status == disnake.Status.offline)

        allonline = online + idle + dnd
        allchannels = len(ctx.guild.channels)
        allvoice = len(ctx.guild.voice_channels)
        alltext = len(ctx.guild.text_channels)
        allroles = len(ctx.guild.roles)

        embed = disnake.Embed(
            description=f"**Информация о сервере {ctx.guild.name}**",
            color=EColor["DEFAULT"],
        )

        embed.add_field(
            name="[Основная информация]",
            value=(
                f"↳ **Создатель сервера:** <@!{ctx.guild.owner.id}>\n"
                f"↳ **ID сервера:** `{ctx.guild.id}`\n"
                f"↳ **Сервер создан:** <t:{created_at}:D>"
            ),
            inline=False,
        )

        embed.add_field(
            name="[Статистика по участникам]",
            value=(
                f"↳ **Онлайн:** `{allonline}`\n"
                f"↳ **Оффлайн:** `{offline}`\n"
                f"↳ **Всего участников:** `{ctx.guild.member_count}`"
            ),
            inline=False,
        )

        embed.add_field(
            name="[Статистика по каналам]",
            value=(
                f"↳ **Всего каналов:** `{allchannels}`\n"
                f"↳ **Текстовых каналов:** `{alltext}`\n"
                f"↳ **Голосовых каналов:** `{allvoice}`"
            ),
            inline=False,
        )

        embed.add_field(
            name="[Доп. Информация]",
            value=(
                f"↳ **Кол-во бустов:** `{ctx.guild.premium_subscription_count}`\n"
                f"↳ **Кол-во ролей:** `{allroles}`\n"
                f"↳ **Уровень верификации:** `{ctx.guild.verification_level}`"
            ),
            inline=False,
        )

        embed.set_thumbnail(url=ctx.guild.icon)
        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )
        await ctx.send(embed=embed)

    @commands.command(name="Userinfo", aliases=["userinfo"])
    async def command_userinfo(self, ctx, user: disnake.Member = None):
        user = user or ctx.author
        ACT = None

        join = int(user.joined_at.timestamp())
        regs = int(user.created_at.timestamp())

        roles = ", ".join(
            [role.mention for role in user.roles if role.name != "@everyone"]
        )

        status_map = {
            "online": "Онлайн",
            "idle": "Отошел",
            "dnd": "Не беспокоить",
            "offline": "Оффлайн",
        }

        if user.web_status:
            online_stats = f"{status_map.get(str(user.web_status), 'Неизвестно')} (Веб)"
        elif user.mobile_status:
            online_stats = (
                f"{status_map.get(str(user.mobile_status), 'Неизвестно')} (Телефон)"
            )
        else:
            online_stats = status_map.get(str(user.status), "Неизвестно")

        ACT = next(
            (
                status
                for status in user.activities
                if isinstance(status, disnake.CustomActivity)
            ),
            None,
        )

        premium = "Да" if user in ctx.guild.premium_subscribers else "Нет"

        embed = disnake.Embed(
            description=f"**Информация о {user.name}**", color=user.color
        )

        embed.set_thumbnail(url=user.avatar)

        embed.add_field(
            name="[Основная информация]",
            value=(
                f"↳ **Имя:** `{user}`\n"
                f"↳ **Пинг:** {user.mention}\n"
                f"↳ **ID Аккаунта:** `{user.id}`"
            ),
            inline=False,
        )

        embed.add_field(
            name="[Статистика]",
            value=(
                f"↳ **Статус:** `{online_stats}`\n"
                f"↳ **Буст сервера:** `{premium}`\n"
                f"↳ **Кастомный статус:** `{ACT}`"
            ),
            inline=False,
        )

        embed.add_field(
            name="[Доп. Информация]",
            value=(
                f"↳ **Зарегистрирован в disnake:** <t:{regs}:D>\n"
                f"↳ **Присоединился на сервер:** <t:{join}:D>\n\n"
                f"↳ **Топ роль:** {user.top_role.mention}\n"
                f"↳ **Все роли:** {roles}"
            ),
            inline=False,
        )

        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )

        await ctx.send(embed=embed)

    @commands.command(name="Botinfo", aliases=["botinfo"])
    async def command_botinfo(self, ctx):
        embed = disnake.Embed(
            title=f"{self.bot.user.name} - Информация о Боте",
            description=f"**Хотите добавить бота?\nнажмите сюда -> {invite_link}**",
            color=EColor["DEFAULT"],
        )

        with open("./json/commands.json", "r", encoding="utf8") as file:
            js = json.load(file)

        complite = js["complete"]
        errors = js["error"]
        All_cm = complite + errors

        end = timer()
        seconds = end - self.uptime

        days = int(seconds // (3600 * 24))
        hours = int((seconds // 3600) % 24)
        minutes = int((seconds // 60) % 60)
        seconds = int(seconds % 60)

        uptimes = f"{hours}h {minutes}m {seconds}s"

        ping = self.bot.latency
        ping_emoji = "🟩🔳🔳🔳🔳"
        ping_list = [
            {"ping": 0.0, "emoji": "🟩🔳🔳🔳🔳"},
            {"ping": 0.1, "emoji": "🟧🟩🔳🔳🔳"},
            {"ping": 0.15, "emoji": "🟥🟧🟩🔳🔳"},
            {"ping": 0.2, "emoji": "🟥🟥🟧🟩🔳"},
            {"ping": 0.25, "emoji": "🟥🟥🟥🟧🟩"},
            {"ping": 0.3, "emoji": "🟥🟥🟥🟥🟧"},
            {"ping": 0.35, "emoji": "🟥🟥🟥🟥🟥"},
        ]

        ping_emoji = next(
            (ping_one["emoji"] for ping_one in ping_list if ping <= ping_one["ping"]),
            ping_emoji,
        )

        memory_usage = psutil.virtual_memory().total / (1024.0**3)
        cpu_usage = psutil.cpu_percent()

        embed.add_field(
            name="Состояние сети:",
            value=f"**Пинг:** `{ping * 1000:.0f} ms`\n{ping_emoji}",
            inline=True,
        )
        embed.add_field(
            name="Система:",
            value=f"**CPU:** `{cpu_usage}%`\n**RAM:** `{memory_usage:.2f}GB`",
            inline=True,
        )
        embed.add_field(
            name="Время работы бота:",
            value=f"**Время работы:** `{uptimes}`",
            inline=True,
        )

        embed.add_field(
            name="Статистика:",
            value=(
                f"**Всего обработанных команд:** `{All_cm}`\n"
                f"**Команд выполненных успешно:** `{complite}`\n"
                f"**Команд с ошибками:** `{errors}`"
            ),
            inline=False,
        )

        embed.set_thumbnail(url=self.bot.user.avatar)
        embed.set_footer(
            text=f"{self.bot.user.name} | © {utc} Все права защищены!",
            icon_url=self.bot.user.avatar,
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
