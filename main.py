import discord
from discord.ext import commands

# from utilities.discord_utilities import EmbedCreator
from utilities import LocalImageEmbed

bot = commands.Bot(command_prefix="h ", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")


@bot.command()
async def cmd(ctx):
    # view = EmbedCreator()
    # await ctx.send(embed=view.embed, view=view)
    file = discord.File(fp=r"C:\aseprite\pngs\die_6.png")
    embed = LocalImageEmbed(title='Hello World!')
    embed.set_image(url=file)
    await embed.send(ctx)


bot.run("ODYzODAxNzIxNzI0MzM4MTg3.GdI5Dk.eZDlBDPqzZFo1kZykxc5f5UpHr06x-atWQONt4")
