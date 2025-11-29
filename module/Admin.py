import disnake
from disnake.ext import commands
import sqlite3

from Utils.SColor import SColor
from setting.color import EColor

conn = sqlite3.connect("./database/VoiceTool.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS voice (
    'guild_id' BIGINT,
    'voice_id' BIGINT,
    'category_id' BIGINT)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS setvoice (
    'guild_id' BIGINT,
    'voice_id' BIGINT)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS setwelcome (
    'guild_id' BIGINT,
    'role_id' BIGINT,
    'message_id' BIGINT)
""")
conn.commit()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="Say", aliases=["say"])
    @commands.has_permissions(administrator=True)
    async def command_say(self, ctx, *, msg=""):
        if not msg:
            return await ctx.send(embed=disnake.Embed(color=EColor["DEFAULT"], description="Для начала укажите сообщение!"))

        try:
            await ctx.message.delete()
            values = msg.split(" ")
            t, image, author, description = "", None, None, ""
            color = 0x36393f
            toggle = ""
            for i in values:
                if i == "/t":
                    toggle = "T"
                elif i == "/d":
                    toggle = "D"
                elif i == "/c":
                    toggle = "C"
                elif i == "/i":
                    toggle = "I"
                elif i == "/a":
                    toggle = "A"
                else:
                    if toggle == "T":
                        t += f"{i} "
                    elif toggle == "C":
                        try:
                            color = SColor[str(i).strip()]
                        except:
                            color = 0
                    elif toggle == "I":
                        image = str(i).strip()
                    elif toggle == "A":
                        if i.startswith("<@!"):
                            author = await self.bot.fetch_user(int(i[3:-1]))
                        elif i.startswith("<@"):
                            author = await self.bot.fetch_user(int(i[2:-1]))
                    else:
                        description += f"{i} "

            embed = disnake.Embed(title=t, description=description, color=color)
            if author:
                embed.set_author(name=author, icon_url=author.avatar)
            if image:
                embed.set_image(url=image)

            await ctx.send(embed=embed)

        except disnake.Forbidden:
            return await ctx.send(embed=disnake.Embed(color=EColor["DEFAULT"], description="У бота нет достаточно прав для выполнения этой команды."))
        except disnake.HTTPException:
            return

def setup(bot):
    bot.add_cog(Admin(bot))
