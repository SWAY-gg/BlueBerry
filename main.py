import disnake
from disnake.ext import commands
import os
import time
import asyncio
import traceback
from rich.console import Console
from rich.table import Table
from rich import box

from setting.config import bot

os.system("cls" if os.name == "nt" else "clear")
console = Console()

COGS = [
    "Information",
    "Economy",
    "Support",
    "Welcome",
    "Command",
    "Error",
    "Admin",
    "Help",
    "Fan"
]

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands = True
command_sync_flags.sync_global_commands = True
command_sync_flags.sync_commands_debug = False

class BlueBerryBot(commands.Bot):
    pass

intents = disnake.Intents.all()
intents.voice_states = True
intents.message_content = True

client = BlueBerryBot(
    help_command=None,
    command_prefix=bot["PREFIX"],
    intents=intents,
    command_sync_flags=command_sync_flags
)

def ts():
    return time.strftime("%b %d %H:%M:%S")


@client.event
async def on_ready():

    print(f"\n{ts()}  [LOAD]  BlueBerry ReadyEvent.service starting...")
    print(f"{ts()}  [INFO]  Logged in as {client.user}")

    try:
        guilds = len(client.guilds)
        members = sum(g.member_count or 0 for g in client.guilds)
        print(f"{ts()}  [INFO]  Guilds: {guilds} | Users: {members}")
    except:
        print(f"{ts()}  [WARN]  Could not fetch guild/member stats")

    try:
        ping_ms = int(client.latency * 1000)
        print(f"{ts()}  [INFO]  Websocket latency: {ping_ms} ms")
    except:
        pass

    print(f"{ts()}  [READY] BlueBerry ReadyEvent.service initialized")
    print(f"{ts()}  [READY] BlueBerry.target reached — all services are up and running\n")


if __name__ == "__main__":

    print("\n● BlueBerry Service — Module Loader\n")

    loaded_modules = []

    for extension in COGS:
        module_name = f"module.{extension}"
        start = time.time()

        print(f"{ts()}  [LOAD]  Loading {extension}.service")

        try:
            client.load_extension(module_name)
            elapsed = (time.time() - start) * 1000
            print(f"{ts()}  [INFO]  {extension}.service loaded ({elapsed:.2f}ms)")
            loaded_modules.append((extension, True, elapsed))

        except Exception:
            elapsed = (time.time() - start) * 1000
            print(f"{ts()}  [ERROR] {extension}.service failed ({elapsed:.2f}ms)")
            traceback.print_exc()
            loaded_modules.append((extension, False, elapsed))

    print(f"\n{ts()}  [INFO]  BlueBerry Service — Load Summary\n")

    max_len = max(len(ext[0]) for ext in loaded_modules)

    for name, ok, t in loaded_modules:
        status = "loaded" if ok else "failed"
        prefix = "[OK]" if ok else "[FAIL]"
        print(f"{ts()}  {prefix}  {name.ljust(max_len)}  {status}  ({t:.2f}ms)")

    print(f"\n{ts()}  [READY] All operations completed. Starting bot...\n")

client.run(bot["TOKEN"])
