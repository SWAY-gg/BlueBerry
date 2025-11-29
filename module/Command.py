import disnake
from disnake.ext import commands, tasks

from datetime import datetime
import traceback
import asyncio
import json
import os
import aiohttp


class Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.commands_file = "./json/commands.json"
        self.js = self.load_json()

        self.task.start()

    def load_json(self):
        if os.path.exists(self.commands_file):
            with open(self.commands_file, "r", encoding="utf8") as file:
                return json.load(file)
        return {"error": 0, "complete": 0}

    def save_json(self):
        with open(self.commands_file, "w", encoding="utf8") as file:
            json.dump(self.js, file, indent=2)

    @tasks.loop(seconds=10, reconnect=True)
    async def task(self):
        try:
            if self.bot.is_closed() or self.bot.ws is None:
                return

            members = sum(g.member_count for g in self.bot.guilds)
            statuses = [
                "BETA 10.2 | >help",
                f"Серверов: {len(self.bot.guilds)}",
                f"Пользователей: {members}",
            ]

            index = int(datetime.utcnow().timestamp() / 10) % len(statuses)
            status_message = statuses[index]

            try:
                await self.bot.change_presence(
                    status=disnake.Status.idle,
                    activity=disnake.Game(name=status_message),
                )
            except (disnake.ConnectionClosed, aiohttp.ClientConnectionResetError):

                return
            except Exception:

                traceback.print_exc()

        except Exception:
            traceback.print_exc()

    @task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        self.js["error"] += 1
        self.save_json()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.js["complete"] += 1
        self.save_json()


def setup(bot):
    bot.add_cog(Command(bot))
