# Discod Module
import disnake
from disnake.ext import commands

import os
import json
import random
import requests
import textwrap
import traceback
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw

import setting.color
from setting.color import EColor

import setting.config
from setting.config import KAWAII

class Fan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Ball", aliases=["ball"])
    async def command_ball(self, ctx, arg: str):
        messages = ["Да", "Нет", "Возможно", "Точно нет!", "Точно да!"]
        response = random.choice(messages)
        embed = disnake.Embed(description=f'**:crystal_ball: Знаки говорят:** {response}', color=EColor["DEFAULT"])
        await ctx.send(embed=embed)

    @command_ball.error
    async def ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = disnake.Embed(description='Пожалуйста, укажите сообщение!', color=EColor["RED"])
            await ctx.send(embed=embed)

    @commands.command(name="Hug", aliases=["hug"])
    async def commands_hug(self, ctx, member: disnake.Member = None):
        user = member or ctx.author
        token = KAWAII["TOKEN"]

        try:
            res = requests.get(f"https://kawaii.red/api/gif/hug/token={token}")
            res.raise_for_status()  # Raise an error if the request was unsuccessful
            gif_url = res.json().get("response", "")
            
            if not gif_url:
                raise ValueError("No GIF found in the response")
        except Exception as e:
            embed = disnake.Embed(description=f"Произошла ошибка при получении GIF: {e}", color=EColor["RED"])
            return await ctx.send(embed=embed)

        if user.bot:
            return

        if user == ctx.author:
            embed = disnake.Embed(color=EColor["DEFAULT"], description=f"**<@{ctx.author.id}> Обнял(-ла) себя <3**")
        else:
            embed = disnake.Embed(color=EColor["DEFAULT"], description=f"**<@{ctx.author.id}> Обнял(-ла) <@{user.id}> <3**")
        
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

    @commands.command(name="Lick", aliases=["lick"])
    async def commands_lick(self, ctx, member: disnake.Member = None):
        user = member or ctx.author
        token = KAWAII["TOKEN"]

        try:
            res = requests.get(f"https://kawaii.red/api/gif/lick/token={token}")
            res.raise_for_status()
            gif_url = res.json().get("response", "")
            
            if not gif_url:
                raise ValueError("No GIF found in the response")
        except Exception as e:
            embed = disnake.Embed(description=f"Произошла ошибка при получении GIF: {e}", color=EColor["RED"])
            return await ctx.send(embed=embed)

        if user.bot:
            return

        if user == ctx.author:
            embed = disnake.Embed(color=EColor["DEFAULT"], description=f"**<@{ctx.author.id}> Лизнул(-ла) себя <3**")
        else:
            embed = disnake.Embed(color=EColor["DEFAULT"], description=f"**<@{ctx.author.id}> Лизнул(-ла) <@{user.id}> <3**")
        
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

    @commands.command(name="Slap", aliases=["slap"])
    async def commands_slap(self, ctx, member: disnake.Member = None):
        user = member or ctx.author
        token = KAWAII["TOKEN"]

        try:
            res = requests.get(f"https://kawaii.red/api/gif/slap/token={token}")
            res.raise_for_status()
            gif_url = res.json().get("response", "")
            
            if not gif_url:
                raise ValueError("No GIF found in the response")
        except Exception as e:
            embed = disnake.Embed(description=f"Произошла ошибка при получении GIF: {e}", color=EColor["RED"])
            return await ctx.send(embed=embed)

        if user.bot:
            return

        if user == ctx.author:
            embed = disnake.Embed(color=EColor["DEFAULT"], description=f"**<@{ctx.author.id}> Шлёпнул(-ла) себя <3**")
        else:
            embed = disnake.Embed(color=EColor["DEFAULT"], description=f"**<@{ctx.author.id}> Шлёпнул(-ла) <@{user.id}> <3**")
        
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

    @commands.command(name="Avatar", aliases=["avatar"])
    async def command_avatar(self, ctx, member: disnake.Member = None):
        user = member or ctx.author
        is_animated = user.avatar.is_animated()

        # Avatar URLs for different formats
        PNG = f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png?size=1024"
        JPEG = f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.jpeg?size=1024"
        GIF = f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.gif?size=1024" if is_animated else None

        # Build embed with avatar options
        embed = disnake.Embed(
            title="**Ну разве не милашка?**",
            color=EColor["DEFAULT"]
        )

        download_text = f"**Скачать:**\n[PNG]({PNG}) | [JPEG]({JPEG})"
        if is_animated:
            download_text += f" | [GIF]({GIF})"

        embed.description = download_text
        embed.set_image(url=user.avatar.url)

        await ctx.send(embed=embed)

# Setup
def setup(bot):
    bot.add_cog(Fan(bot))