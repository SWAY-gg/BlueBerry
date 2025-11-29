import disnake  
from disnake.ext import commands  
import sqlite3
import io
from PIL import Image, ImageDraw, ImageFont  
import time
import traceback


from setting.color import EColor

conn = sqlite3.connect("./database/Tool.db", check_same_thread=False)
cursor = conn.cursor()

cursor.executescript(
    """
CREATE TABLE IF NOT EXISTS welcome (
    channel_id BIGINT,
    channel_name TEXT,
    guild_id BIGINT UNIQUE,
    guild_name TEXT
);

CREATE TABLE IF NOT EXISTS roles (
    role_id BIGINT,
    role_name TEXT,
    guild_id BIGINT UNIQUE,
    guild_name TEXT
);
"""
)
conn.commit()

def db_get(table: str, guild_id: int):
    cursor.execute(f"SELECT * FROM {table} WHERE guild_id = ?", (guild_id,))
    return cursor.fetchone()


def db_set_welcome(guild_id, guild_name, channel_id, channel_name):
    cursor.execute(
        """
    INSERT INTO welcome (channel_id, channel_name, guild_id, guild_name)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(guild_id) DO UPDATE SET
        channel_id = excluded.channel_id,
        channel_name = excluded.channel_name,
        guild_name = excluded.guild_name
    """,
        (channel_id, channel_name, guild_id, guild_name),
    )
    conn.commit()


def db_set_role(guild_id, guild_name, role_id, role_name):
    cursor.execute(
        """
    INSERT INTO roles (role_id, role_name, guild_id, guild_name)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(guild_id) DO UPDATE SET
        role_id = excluded.role_id,
        role_name = excluded.role_name,
        guild_name = excluded.guild_name
    """,
        (role_id, role_name, guild_id, guild_name),
    )
    conn.commit()


def db_delete(table: str, guild_id: int):
    cursor.execute(f"DELETE FROM {table} WHERE guild_id = ?", (guild_id,))
    conn.commit()


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _get_avatar_image(
        self, member: disnake.Member, size: int = 256
    ) -> Image.Image:
        """Download member avatar and return PIL Image RGBA resized to (size,size)."""
        avatar_asset = member.display_avatar.replace(size=size)
        avatar_bytes = await avatar_asset.read()
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
        avatar = avatar.resize((size, size), Image.LANCZOS)
        return avatar

    def _circle_mask(self, size: int):
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        return mask

    async def generate_welcome_card(self, member: disnake.Member) -> disnake.File:
        width, height = 900, 300
        bg_color = (30, 30, 30)
        overlay_alpha = 150

        background = Image.new("RGBA", (width, height), bg_color)

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle((0, 180, width, height), fill=(0, 0, 0, overlay_alpha))
        background = Image.alpha_composite(background, overlay)

        avatar = await self._get_avatar_image(member, size=180)
        mask = self._circle_mask(180)
        avatar.putalpha(mask)
        background.paste(avatar, (30, 60), avatar)

        draw = ImageDraw.Draw(background)

        try:
            font_big = ImageFont.truetype("arial.ttf", 48)
            font_med = ImageFont.truetype("arial.ttf", 28)
            font_small = ImageFont.truetype("arial.ttf", 22)
        except Exception:
            font_big = ImageFont.load_default()
            font_med = ImageFont.load_default()
            font_small = ImageFont.load_default()

        welcome_text = "Добро пожаловать,"
        name_text = f"{member.name}#{member.discriminator}"
        count_text = f"Ты стал участником №{member.guild.member_count}"

        x_start = 240
        draw.text((x_start, 80), welcome_text, font=font_med, fill=(235, 235, 235))
        draw.text((x_start, 120), name_text, font=font_big, fill=(255, 255, 255))
        draw.text((x_start, 190), count_text, font=font_small, fill=(200, 200, 200))

        try:
            if member.guild.icon:
                icon_asset = member.guild.icon.replace(size=128)
                icon_bytes = await icon_asset.read()
                icon = (
                    Image.open(io.BytesIO(icon_bytes))
                    .convert("RGBA")
                    .resize((80, 80), Image.LANCZOS)
                )
                # small rounded mask
                icon_mask = self._circle_mask(80)
                icon.putalpha(icon_mask)
                background.paste(icon, (width - 110, 20), icon)
        except Exception:
            pass

        out = io.BytesIO()
        background.convert("RGB").save(out, format="PNG")
        out.seek(0)
        return disnake.File(fp=out, filename="welcome.png")

    async def generate_leave_card(self, member: disnake.Member) -> disnake.File:
        width, height = 900, 300
        bg_color = (25, 25, 25)
        overlay_alpha = 140

        background = Image.new("RGBA", (width, height), bg_color)

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle((0, 180, width, height), fill=(0, 0, 0, overlay_alpha))
        background = Image.alpha_composite(background, overlay)

        avatar = await self._get_avatar_image(member, size=180)
        mask = self._circle_mask(180)
        avatar.putalpha(mask)
        background.paste(avatar, (30, 60), avatar)

        draw = ImageDraw.Draw(background)

        try:
            font_big = ImageFont.truetype("arial.ttf", 48)
            font_med = ImageFont.truetype("arial.ttf", 28)
            font_small = ImageFont.truetype("arial.ttf", 22)
        except Exception:
            font_big = ImageFont.load_default()
            font_med = ImageFont.load_default()
            font_small = ImageFont.load_default()

        left_text = "Покинул сервер,"
        name_text = f"{member.name}#{member.discriminator}"
        count_text = f"Теперь нас: {member.guild.member_count}"

        x_start = 240
        draw.text((x_start, 80), left_text, font=font_med, fill=(235, 235, 235))
        draw.text((x_start, 120), name_text, font=font_big, fill=(255, 255, 255))
        draw.text((x_start, 190), count_text, font=font_small, fill=(200, 200, 200))

        # export
        out = io.BytesIO()
        background.convert("RGB").save(out, format="PNG")
        out.seek(0)
        return disnake.File(fp=out, filename="leave.png")

    @commands.command(name="Set-welcome", aliases=["set-welcome"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, channel: disnake.TextChannel = None):
        try:
            channel = channel or ctx.channel
            db_set_welcome(ctx.guild.id, ctx.guild.name, channel.id, channel.name)
            embed = disnake.Embed(
                title="🟢 Welcome обновлён",
                description=f"Канал установлен: {channel.mention}",
                color=EColor["GREEN"],
            )
            await ctx.send(embed=embed)
        except Exception as e:
            # log and inform
            print("ERROR in set_welcome:", e)
            traceback.print_exc()
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"],
                    description="Произошла ошибка при сохранении канала.",
                )
            )

    @set_welcome.error
    async def err_set_welcome(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏳ Подожди `{round(error.retry_after, 1)} сек.` перед повторным использованием!"
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"], description="Недостаточно прав!"
                )
            )

    @commands.command(name="Del-welcome", aliases=["del-welcome"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def del_welcome(self, ctx):
        try:
            if not db_get("welcome", ctx.guild.id):
                return await ctx.send(
                    embed=disnake.Embed(
                        color=EColor["RED"], description="Welcome канал не установлен."
                    )
                )
            db_delete("welcome", ctx.guild.id)
            embed = disnake.Embed(
                title="✔ Welcome удалён",
                description="Приветственный канал успешно сброшен.",
                color=EColor["GREEN"],
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("ERROR in del_welcome:", e)
            traceback.print_exc()
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"],
                    description="Произошла ошибка при удалении канала.",
                )
            )

    @del_welcome.error
    async def err_del_welcome(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Подожди `{round(error.retry_after, 1)} сек.`!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"], description="Недостаточно прав!"
                )
            )

    @commands.command(name="Set-role", aliases=["set-role"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def set_role(self, ctx, role: disnake.Role = None):
        try:
            if not role:
                return await ctx.send(
                    embed=disnake.Embed(
                        color=EColor["RED"], description="Укажите роль!"
                    )
                )

            me = ctx.guild.me or ctx.guild.get_member(self.bot.user.id)
            if not me.guild_permissions.manage_roles:
                return await ctx.send(
                    embed=disnake.Embed(
                        color=EColor["RED"], description="У меня нет прав Manage Roles!"
                    )
                )

            bot_top = me.top_role.position if me.top_role else 0
            if role.position >= bot_top:
                return await ctx.send(
                    embed=disnake.Embed(
                        color=EColor["RED"],
                        description="Моя роль ниже целевой роли — сделайте мою роль выше.",
                    )
                )

            db_set_role(ctx.guild.id, ctx.guild.name, role.id, role.name)

            perms = ctx.channel.permissions_for(me)
            color_value = EColor.get("DEFAULT", 0x2F3136)
            try:
                if isinstance(color_value, str) and color_value.startswith("#"):
                    color_value = int(color_value.lstrip("#"), 16)
            except Exception:
                color_value = 0x2F3136

            embed = disnake.Embed(
                title="🟢 Роль установлена",
                description=f"Роль: {role.mention}",
                color=color_value,
            )

            if not perms.embed_links:
                await ctx.send(
                    f"✅ Роль установлена: {role.mention}\n⚠ У меня нет права `Embed Links`"
                )
            else:
                await ctx.send(embed=embed)

        except Exception as e:
            print("ERROR in set_role:", e)
            traceback.print_exc()
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"],
                    description="Произошла ошибка при сохранении роли.",
                )
            )

    @set_role.error
    async def err_set_role(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Подожди `{round(error.retry_after, 1)} сек.`!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"], description="Недостаточно прав!"
                )
            )

    @commands.command(name="Del-role", aliases=["del-role"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def del_role(self, ctx):
        try:
            if not db_get("roles", ctx.guild.id):
                return await ctx.send(
                    embed=disnake.Embed(
                        color=EColor["RED"],
                        description="Роль при входе не установлена.",
                    )
                )

            db_delete("roles", ctx.guild.id)

            embed = disnake.Embed(
                title="✔ Роль удалена",
                description="Автовыдаваемая роль успешно сброшена.",
                color=EColor["GREEN"],
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("ERROR in del_role:", e)
            traceback.print_exc()
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"],
                    description="Произошла ошибка при удалении роли.",
                )
            )

    @del_role.error
    async def err_del_role(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Подожди `{round(error.retry_after, 1)} сек.`!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"], description="Недостаточно прав!"
                )
            )

    @commands.command(name="Check", aliases=["check"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def check(self, ctx):
        try:
            welcome = db_get("welcome", ctx.guild.id)
            roles = db_get("roles", ctx.guild.id)

            if welcome:
                ch_status = "🟢 Настроено"
                channel_value = (
                    f"<#{welcome[0]}> (`{welcome[1]}`)\n**ID:** `{welcome[0]}`"
                )
            else:
                ch_status = "🔴 Не установлено"
                channel_value = "*Канал отсутствует*"

            if roles:
                role_status = "🟢 Настроено"
                role_value = f"<@&{roles[0]}> (`{roles[1]}`)\n**ID:** `{roles[0]}`"
            else:
                role_status = "🔴 Не установлено"
                role_value = "*Роль отсутствует*"


            embed = disnake.Embed(
                title="⚙ Настройки модуля Welcome",
                color=EColor["DEFAULT"],
                description=f"Проверка конфигурации сервера **{ctx.guild.name}**",
            )

            embed.add_field(
                name=f"📨 Welcome-канал — {ch_status}",
                value=channel_value,
                inline=False,
            )

            embed.add_field(
                name=f"🎖 Роль при входе — {role_status}", value=role_value, inline=False
            )

            embed.add_field(
                name="🧩 Состояние системы",
                value=(
                    "🟢 **Готово к работе**"
                    if welcome and roles
                    else (
                        "🟡 **Частично настроено** — рекомендуется завершить конфигурацию."
                        if welcome or roles
                        else "🔴 **Не настроено** — требуется установка канала и роли."
                    )
                ),
                inline=False,
            )

            embed.set_footer(
                text=f"ID сервера: {ctx.guild.id} • Проверил: {ctx.author}",
                icon_url=ctx.author.display_avatar.url,
            )

            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

            await ctx.send(embed=embed)
        except Exception as e:
            print("ERROR in check:", e)
            traceback.print_exc()
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"],
                    description="Произошла ошибка при проверке конфигурации.",
                )
            )

    @check.error
    async def err_check(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Подожди `{round(error.retry_after, 1)} сек.`!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=disnake.Embed(
                    color=EColor["RED"], description="Недостаточно прав!"
                )
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        try:
            welcome = db_get("welcome", member.guild.id)
            if not welcome:
                return

            channel = member.guild.get_channel(welcome[0])
            if not channel:
                return

            try:
                card_file = await self.generate_welcome_card(member)
                embed = disnake.Embed(
                    title="🎉 Добро пожаловать!",
                    description=f"{member.mention} присоединился к серверу! Поздравим нового участника.",
                    color=EColor["GREEN"],
                )
                embed.set_image(url="attachment://welcome.png")
                await channel.send(embed=embed, file=card_file)
            except Exception:
                # fallback to simple embed if image generation fails
                embed = disnake.Embed(
                    title="🎉 Добро пожаловать!",
                    description=f"{member.mention} присоединился к серверу!",
                    color=EColor["GREEN"],
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(embed=embed)

            roles = db_get("roles", member.guild.id)
            if roles:
                role = member.guild.get_role(roles[0])
                if role:
                    try:
                        await member.add_roles(role, reason="Welcome role assignment")
                    except Exception:
                        pass
        except Exception:
            return

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        try:
            welcome = db_get("welcome", member.guild.id)
            if not welcome:
                return

            channel = member.guild.get_channel(welcome[0])
            if not channel:
                return

            try:
                card_file = await self.generate_leave_card(member)
                embed = disnake.Embed(
                    title="👋 Участник покинул сервер",
                    description=f"`{member}` больше не с нами.",
                    color=EColor["RED"],
                )
                embed.set_image(url="attachment://leave.png")
                await channel.send(embed=embed, file=card_file)
            except Exception:
                embed = disnake.Embed(
                    title="👋 Участник покинул сервер",
                    description=f"`{member}` больше не с нами.",
                    color=EColor["RED"],
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(embed=embed)
        except Exception:
            return

    @commands.command(name="debug_commands")
    @commands.is_owner()
    async def debug_commands(self, ctx):
        cmds = [c.name for c in self.get_commands() if isinstance(c, commands.Command)]
        await ctx.send(f"Commands in this cog: {', '.join(cmds)}")


def setup(bot):
    bot.add_cog(Welcome(bot))
