import disnake
from disnake.ext import commands
from disnake.ext.commands import BucketType, cooldown

import io
import time
import random
import asyncio
import sqlite3
import requests
import traceback

from io import BytesIO
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter

import setting.color
from setting.color import EColor

conn = sqlite3.connect("./database/Economy.db")
cursor = conn.cursor()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS users (
    'id' INT,
    'xp' INT,
    'lvl' INT,
    'rank' INT,
    'name' TEXT,
    'marry' INT,
    'status' TEXT,
    'money' BIGINT,
    'server_id' INT)
"""
)

cursor.execute(
    """CREATE TABLE IF NOT EXISTS shop (
    'role_id' INT,
    'id' INT,
    'cost' BIGINT)
"""
)
conn.commit()

# XP
XP_MIN = 10
XP_MAX = 30


def xp_to_next_level(level: int) -> int:
    return 100 + (level * 50)


XP_COOLDOWN = 30
last_xp_gain = {}


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_rank_title(self, level):
        if level < 5:
            return "Новичок"
        if level < 10:
            return "Ученик"
        if level < 20:
            return "Опытный"
        if level < 35:
            return "Профессионал"
        if level < 50:
            return "Мастер"
        return "Легенда"

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue
                cursor.execute(
                    f"SELECT * FROM users WHERE id = ? AND server_id = ?",
                    (member.id, member.guild.id),
                )
                if cursor.fetchone() is None:
                    cursor.execute(
                        f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            member.id,
                            0,
                            0,
                            0,
                            member.name,
                            0,
                            "Не задано",
                            0,
                            member.guild.id,
                        ),
                    )
                    conn.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        cursor.execute(
            f"SELECT * FROM users WHERE id = ? AND server_id = ?",
            (member.id, member.guild.id),
        )
        if cursor.fetchone() is None:
            if not member.bot:
                cursor.execute(
                    f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        member.id,
                        0,
                        0,
                        0,
                        member.name,
                        0,
                        "Не задано",
                        0,
                        member.guild.id,
                    ),
                )
                conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if len(message.content) < 5:
            return

        user_id = message.author.id
        now = time.time()

        if user_id in last_xp_gain and now - last_xp_gain[user_id] < XP_COOLDOWN:
            return
        last_xp_gain[user_id] = now

        cursor.execute("SELECT xp, lvl, money FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            return

        xp, lvl, money = row
        gained = random.randint(XP_MIN, XP_MAX)
        xp += gained

        leveled_up = False
        new_levels = 0

        while xp >= xp_to_next_level(lvl):
            xp -= xp_to_next_level(lvl)
            lvl += 1
            money += 500
            new_levels += 1
            leveled_up = True

        cursor.execute(
            "UPDATE users SET xp = ?, lvl = ?, money = ? WHERE id = ?",
            (xp, lvl, money, user_id),
        )
        conn.commit()

        if leveled_up:
            embed = disnake.Embed(
                title="LVL UP 🎉",
                description=(
                    f"**🎉 Поздравляю, {message.author.mention}!**\n\n"
                    f"Ты достиг **{lvl} уровня** 🔥\n\n"
                    + (f"**+{new_levels * 500} монеток** 🎁" if new_levels > 0 else "")
                ),
                color=EColor["DEFAULT"],
            )

            embed.add_field(
                name="🎯 Новый уровень",
                value=f"Теперь ты на уровне **{lvl}**!",
                inline=False,
            )
            embed.add_field(
                name="💰 Бонусы",
                value=(
                    f"Ты получил **+{new_levels * 500} монеток**!"
                    if new_levels > 0
                    else "Продолжай развиваться!"
                ),
                inline=False,
            )

            embed.set_footer(
                text=f"Достижение {message.author.name}",
                icon_url=message.author.avatar.url,
            )
            await message.channel.send(embed=embed)

    @commands.command(name="card")
    async def card(self, ctx, member: disnake.Member = None):
        if member is None:
            member = ctx.author

        cursor.execute(
            "SELECT id, xp, lvl FROM users WHERE server_id = ? ORDER BY lvl DESC, xp DESC",
            (ctx.guild.id,),
        )
        users = cursor.fetchall()

        row = next((u for u in users if u[0] == member.id), None)
        if not row:
            return await ctx.send("Пользователь не найден.")

        xp = row[1]
        lvl = row[2]
        xp_need = 1000
        progress = xp / xp_need
        rank = users.index(row) + 1

        embed = disnake.Embed(
            title=f"{member.name} - Уровень {lvl}",
            description=f"Ранг: #{rank}\n\n**XP:** {xp}/{xp_need} ({int(progress*100)}% прогресса)",
            color=0x2F3136,
        )

        progress_bar = "▰" * int(progress * 20) + "▱" * (20 - int(progress * 20))

        embed.add_field(
            name=f"Прогресс: ({int(progress * 100)}%)",
            value=f"{progress_bar}",
            inline=False,
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        title = self.get_rank_title(lvl)
        embed.add_field(name="Титул:", value=f"■ {title}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="Marry", aliases=["marry"])
    async def command_marry(self, ctx, member: disnake.Member = None):
        cursor.execute(
            "SELECT * FROM users WHERE server_id = ? AND id = ?",
            (ctx.guild.id, ctx.author.id),
        )

        Times = int(time.mktime(datetime.utcnow().timetuple()))
        db = cursor.fetchone()
        user = member or ctx.author

        if user.bot:
            return
        if user.id == ctx.author.id:
            return

        cursor.execute("SELECT marry FROM users WHERE id = ?", (user.id,))
        check = cursor.fetchone()

        if check is None or check[0] != 0:
            return await ctx.send("Данный человек уже находится в браке!")
        if db is None or db[5] != 0:
            return await ctx.send("Вы уже находитесь в браке!")

        embed = disnake.Embed(
            color=EColor["DEFAULT"],
            title="Marry - Вам предложили бракосочетание!",
            description=f"**У вас есть 1 минута для принятия предложения!**\nПредложил: <@{ctx.author.id}>",
        )

        message = await ctx.send(embed=embed)

        def reaction_check(m):
            return (
                m.message_id == message.id
                and m.user_id == user.id
                and str(m.emoji) == "💕"
            )

        try:
            await message.add_reaction("💕")
            await self.bot.wait_for(
                "raw_reaction_add", timeout=60.0, check=reaction_check
            )

            cursor.execute(
                "UPDATE users SET marry = ? WHERE id = ? AND server_id = ?",
                (user.id, ctx.author.id, ctx.guild.id),
            )
            cursor.execute(
                "UPDATE users SET marry = ? WHERE id = ? AND server_id = ?",
                (ctx.author.id, user.id, ctx.guild.id),
            )

            conn.commit()

            await message.edit(
                embed=disnake.Embed(
                    color=EColor["DEFAULT"],
                    title="💕 Поздравляем наших новобрачных 💕",
                    description=f"**<@{ctx.author.id}> и <@{user.id}> вступили в брак!**\n**Брак вступил в силу:** <t:{Times}:D>",
                )
            )

        except asyncio.TimeoutError:
            try:
                await message.delete()
            except disnake.NotFound:
                pass

    @commands.command(
        name="Marry-Divorce",
        aliases=["Marry-divorce", "marry-divorce", "marry-Divorce"],
    )
    async def commands_Marry_Divorce(self, ctx, member: disnake.Member = None):
        cursor.execute(
            "SELECT * FROM users WHERE server_id = ? AND id = ?",
            (ctx.guild.id, ctx.author.id),
        )
        db = cursor.fetchone()

        if db is None:
            return await ctx.send("Не удалось найти вашу запись в базе данных!")

        if db[5] == 0:
            return await ctx.send("Вы не состоите в браке!")

        usless_man = db[5]

        cursor.execute(
            "SELECT * FROM users WHERE id = ? AND server_id = ?",
            (usless_man, ctx.guild.id),
        )
        partner = cursor.fetchone()

        if partner is None:
            return await ctx.send(
                "Не удалось найти информацию о вашем супруге в базе данных!"
            )

        if partner[5] != ctx.author.id:
            return await ctx.send("Этот человек не состоит с вами в браке!")

        Times = int(time.mktime(datetime.utcnow().timetuple()))  # Дата развода

        try:
            cursor.execute(
                "UPDATE users SET marry = ? WHERE id = ? AND server_id = ?",
                (0, usless_man, ctx.guild.id),
            )
            cursor.execute(
                "UPDATE users SET marry = ? WHERE id = ? AND server_id = ?",
                (0, ctx.author.id, ctx.guild.id),
            )
            conn.commit()

            embed = disnake.Embed(
                description=(
                    f"**Что ж, это случается! <@{usless_man}> и <@{ctx.author.id}> развелись!**\n"
                    f"**Дата расторжения брака:** <t:{Times}:D>"
                ),
                color=EColor["DEFAULT"],
            )
            await ctx.send(embed=embed)
        except Exception as e:
            conn.rollback()
            await ctx.send(f"Произошла ошибка при расторжении брака: {str(e)}")

    @commands.command(name="user", aliases=["User"])
    async def Command_User(self, ctx, member: disnake.Member = None):
        user = member or ctx.author
        if user.bot:
            return await ctx.send("Боты не могут иметь профили.")

        cursor.execute(
            "SELECT marry, status, money FROM users WHERE id = ? AND server_id = ?",
            (user.id, ctx.guild.id),
        )
        user_data = cursor.fetchone()

        if user_data is None:
            return await ctx.send(
                f"Не удалось найти профиль для {user.name} в базе данных."
            )

        marry, status, money = user_data

        if marry == 0:
            user_marry = "Не в браке 😔"
        else:
            user_marry = f"<@{marry}> 💍"

        embed = disnake.Embed(
            title=f"📊 Профиль пользователя: {user.name}",
            description=f"**Профиль {user.name}**\nДавайте заглянем в его профиль! 🧐",
            color=0x00FF00,
        )

        embed.set_thumbnail(url=user.avatar.url)

        embed.add_field(name="💰 Баланс:", value=f"**{money} монет** 💸", inline=False)
        embed.add_field(
            name="📜 Статус:",
            value=f"**{status if status else 'Не задан'}**",
            inline=False,
        )
        embed.add_field(name="💑 Пара:", value=f"**{user_marry}**", inline=False)

        embed.add_field(
            name="🎯 Уровень:",
            value=f"**{user.name}** достиг **{level} уровня**",
            inline=False,
        )

        embed.add_field(
            name="🏅 Ранг:", value=f"**{rank}** - Текущий ранг на сервере", inline=False
        )

        embed.set_footer(
            text=f"Запрос от {ctx.author.name}", icon_url=ctx.author.avatar.url
        )

        await ctx.send(embed=embed)

    @commands.command(name="status", aliases=["Status"])
    async def Command_Status(self, ctx, *, arg: str):

        if len(arg) == 0:
            return await ctx.send("Ваш статус не может быть пустым!")
        elif len(arg) > 50:
            return await ctx.send("Статус не может быть длиннее 50 символов!")

        try:
            cursor.execute(
                "UPDATE users SET status = ? WHERE id = ? AND server_id = ?",
                (arg, ctx.author.id, ctx.guild.id),
            )
            conn.commit()

            embed = disnake.Embed(color=EColor["DEFAULT"])
            embed.add_field(
                name="Статус изменён",
                value=f"**Ваш новый статус:**\n```{arg}```",
                inline=False,
            )
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Произошла ошибка при обновлении статуса: {e}")

    @commands.command(name="money", aliases=["Money"])
    async def Command_Money(self, ctx, member: disnake.Member = None):
        user = member or ctx.author
        if user.bot:
            return

        for row in cursor.execute(f"SELECT money FROM users WHERE id = '{user.id}'"):
            money = row[0]

        embed = disnake.Embed(color=EColor["DEFAULT"])
        embed.set_thumbnail(url=user.avatar)
        embed.add_field(
            name=f"Баланс пользователя: {user.name}",
            value=(f"> **Монеты:** \n" f"```{money}```"),
            inline=False,
        )

        await ctx.send(embed=embed)

    # Command Give
    @commands.command(name="give", aliases=["Give"])
    async def Command_Give(self, ctx, member: disnake.Member, summ: int):
        for row in cursor.execute(
            f"SELECT money FROM users WHERE id = '{ctx.message.author.id}'"
        ):
            for raw in cursor.execute(
                f"SELECT money FROM users WHERE id = '{member.id}'"
            ):
                if summ > row[0]:
                    await ctx.send("У вас не такой суммы на балансе!")

                else:
                    new_m = raw[0] + summ
                    cursor.execute(
                        f"UPDATE users SET money = '{new_m}' WHERE id = '{member.id}'"
                    )
                    conn.commit()

                    new_b = row[0] - summ
                    cursor.execute(
                        f"UPDATE users SET money = '{new_b}' WHERE id = '{ctx.message.author.id}'"
                    )
                    conn.commit()

                embed = disnake.Embed(color=EColor["DEFAULT"])
                embed.set_thumbnail(url=ctx.author.avatar)
                embed.add_field(
                    name=f"💸 Перевод от пользователя: {ctx.author.name}",
                    value=(
                        f"> **Сумма перевода:** \n"
                        f"```{summ}```\n"
                        f"> **Получатель:** \n"
                        f"```{member.name}```"
                    ),
                    inline=False,
                )

                await ctx.send(embed=embed)

    @commands.command(name="daily", aliases=["Daily"])
    @cooldown(1, 60 * 60 * 24, BucketType.user)
    async def Command_Daily(self, ctx):
        cursor.execute(f"SELECT money FROM users WHERE id = '{ctx.message.author.id}'")

        daily = 1000
        new_money = cursor.fetchone()[0] + daily
        cursor.execute(
            f"UPDATE users SET money = '{new_money}' WHERE id = '{ctx.message.author.id}'"
        )
        conn.commit()

        embed = disnake.Embed(color=EColor["DEFAULT"])
        embed.set_thumbnail(url=ctx.author.avatar)
        embed.add_field(
            name=f"💵 Ежедневная награда: {ctx.author.name}",
            value=(
                f"**Вы получили ежедневную награду \n"
                f"В размере: \n"
                f"```{daily}```**"
            ),
            inline=False,
        )

        await ctx.send(embed=embed)

    @Command_Daily.error
    async def Daily_Error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(color=EColor["DEFAULT"])
            embed.add_field(
                name="Команда временно недоступна!",
                value=f"**Попробуйте через: {error.retry_after / 60 / 60 :.0f} ч {error.retry_after / 60 % 60 :.0f} м {error.retry_after % 60 % 60 :.0f} с**",
            )

            await ctx.send(embed=embed)

    @commands.command(name="top", aliases=["Top"])
    async def Command_Top(self, ctx):
        if not ctx.guild:
            return await ctx.send("Эта команда доступна только на сервере!")

        embed = disnake.Embed(
            title="💎 Топ 5 лидеров по монетам 💎",
            description="Вот лидеры нашего сервера, кто собрал наибольшее количество монет! 🎉",
            color=0xFFD700,
        )

        Counter = 0

        cursor.execute(
            "SELECT name, money FROM users WHERE server_id = ? ORDER BY money DESC LIMIT 5",
            (ctx.guild.id,),
        )
        top_users = cursor.fetchall()

        if not top_users:
            return await ctx.send("На сервере нет пользователей с монетами.")

        for row in top_users:
            Counter += 1
            embed.add_field(
                name=f"#{Counter} {row[0]}",
                value=f"**Монеты:** {row[1]} 💰",
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command(name="bet", aliases=["Bet"])
    @cooldown(1, 1, BucketType.user)
    async def Command_Bet(self, ctx, num: str):
        user_id = ctx.author.id

        cursor.execute("SELECT money FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return await ctx.send("⚠ Ошибка: пользователь не найден в базе.")

        balance = row[0]

        num = num.replace("_", "")

        if num.lower() == "all":
            bet = balance
        else:
            if not num.isdigit():
                return await ctx.send("❌ Укажи корректную ставку числом.")
            bet = int(num)

        if bet < 10:
            return await ctx.send(
                embed=disnake.Embed(
                    description=f"**Минимальная ставка — `10` монет.**",
                    color=EColor["DEFAULT"],
                )
            )

        if bet > balance:
            return await ctx.send(
                embed=disnake.Embed(
                    description=f"**У тебя недостаточно монет!**",
                    color=EColor["DEFAULT"],
                )
            )

        reels = ["🍒", "🍋", "🔔", "⭐", "🍇", "💎"]

        embed = disnake.Embed(
            title="🎰 Слот-машина",
            description=f"`| ❓ | ❓ | ❓ |`\n**Ставка:** `{bet}` монет",
            color=EColor["DEFAULT"],
        )
        msg = await ctx.send(embed=embed)

        for _ in range(3):
            a, b, c = random.choice(reels), random.choice(reels), random.choice(reels)

            embed.description = f"`| {a} | {b} | {c} |`\n**Ставка:** `{bet}` монет"
            await msg.edit(embed=embed)

            await asyncio.sleep(random.uniform(2.0, 3.0))

        final = [random.choice(reels) for _ in range(3)]
        a, b, c = final

        if a == b == c:
            win = bet * 3
            text = f"🎉 **ДЖЕКПОТ!**\nТы выиграл `{win}` монет!"
            color = EColor["GREEN"]
        elif a == b or b == c or a == c:
            win = bet * 1.5
            win = int(win)
            text = f"✨ **Неплохо!**\nТы выиграл `{win}` монет!"
            color = EColor["GREEN"]
        else:
            win = -bet
            text = f"💀 Ты проиграл `{bet}` монет."
            color = EColor["RED"]

        new_balance = balance + win
        cursor.execute(
            "UPDATE users SET money = ? WHERE id = ?", (new_balance, user_id)
        )
        conn.commit()

        embed = disnake.Embed(
            title="🎰 Слот-машина | Результат",
            description=f"`| {a} | {b} | {c} |`\n{text}",
            color=color,
        )
        embed.set_footer(text=f"Баланс: {new_balance} монет")

        await msg.edit(embed=embed)

    @Command_Bet.error
    async def bet_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            pass

    @commands.command(name="add-shop", aliases=["Add-shop"])
    @commands.has_permissions(administrator=True)
    async def Command_add_shop(self, ctx, role: disnake.Role = None, cost: int = None):
        if role is None:
            embed = disnake.Embed(
                colour=EColor["RED"],
                title="Извените, произошла ошибка!",
                description=f"Необходимо указать роль!",
            )
            await ctx.send(embed=embed)
        else:
            if cost is None:
                embed = disnake.Embed(
                    colour=EColor["RED"],
                    title="Извените, произошла ошибка!",
                    description=f"Необходимо указать цену роли!",
                )
                await ctx.send(embed=embed)

            elif cost < 0:
                embed = disnake.Embed(
                    colour=EColor["RED"],
                    title="Извените, произошла ошибка!",
                    description=f"Цена не может быть такой маленькой!",
                )
                await ctx.send(embed=embed)

            else:
                cursor.execute(
                    "INSERT INTO shop VALUES ('{}', '{}', '{}')".format(
                        role.id, ctx.guild.id, cost
                    )
                )
                conn.commit()

                await ctx.message.add_reaction("✅")

    @commands.command(name="remove-shop", aliases=["Remove-shop"])
    @commands.has_permissions(administrator=True)
    async def Command_remove_shop(self, ctx, role: disnake.Role = None):
        if role is None:
            embed = disnake.Embed(
                colour=EColor["RED"],
                title="Извените, произошла ошибка!",
                description=f"Укажите роль для удаления!",
            )
            await ctx.send(embed=embed)

        else:
            cursor.execute("DELETE FROM shop WHERE role_id = '{}'".format(role.id))
            conn.commit()

            await ctx.message.add_reaction("✅")

    @commands.command(name="shop", aliases=["Shop"])
    async def Command_shop(self, ctx):
        embed = disnake.Embed(
            title=f"Магазин ролей сервера: {ctx.guild.name}", color=EColor["DEFAULT"]
        )
        count = 0

        for row in cursor.execute(
            "SELECT role_id, cost FROM shop WHERE id = '{}'".format(ctx.guild.id)
        ):
            if ctx.guild.get_role(row[0]) != None:
                count += 1

                embed.add_field(
                    name=f"Стоимость роли: **{row[1]} :dollar:**",
                    value=f"**Вы получите роль:** {ctx.guild.get_role(row[0]).mention}",
                    inline=False,
                )

        if count == 0:
            embed.description = "**В магазине на данный момент нет ролей!**"

        await ctx.send(embed=embed)

    @commands.command(name="buy", aliases=["Buy"])
    async def Command_buy(self, ctx, role: disnake.Role = None):
        if role is None:
            embed = disnake.Embed(
                colour=EColor["RED"],
                title="Извените, произошла ошибка!",
                description=f"Укажите роль для покупки!",
            )
            await ctx.send(embed=embed)

        else:
            if role in ctx.author.roles:
                embed = disnake.Embed(
                    colour=EColor["RED"],
                    title="Извените, произошла ошибка!",
                    description=f"У вас есть данная роль!",
                )
                await ctx.send(embed=embed)

            elif (
                cursor.execute(
                    "SELECT cost FROM shop WHERE role_id = '{}'".format(role.id)
                ).fetchone()[0]
                > cursor.execute(
                    "SELECT money FROM users WHERE id = '{}'".format(ctx.author.id)
                ).fetchone()[0]
            ):
                embed = disnake.Embed(
                    colour=EColor["RED"],
                    title="Извените, произошла ошибка!",
                    description=f"У вас нет столько денег!",
                )
                await ctx.send(embed=embed)

            else:
                await ctx.author.add_roles(role)
                cursor.execute(
                    "UPDATE users SET money = money - '{}' WHERE id = '{}'".format(
                        cursor.execute(
                            "SELECT cost FROM shop WHERE role_id = '{}'".format(role.id)
                        ).fetchone()[0],
                        ctx.author.id,
                    )
                )
                conn.commit()
                await ctx.message.add_reaction("✅")


def setup(bot):
    bot.add_cog(Economy(bot))
