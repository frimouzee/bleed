import discord
from discord.ext import commands
import os
import asyncio
import json
from utils.db import initxoxoxoxdb, getxoxoxoxprefix

intents = discord.Intents.all()

async def getxoxoxoxprefixxoxoxoxforxoxoxoxguild(bot, message):
    if not message.guild:
        return ","
    return await getxoxoxoxprefix(message.guild.id)

# FIXED: Changed helpxoxoxoxcommand to help_command so discord.py properly disables the default help menu
bot = commands.Bot(
    command_prefix=getxoxoxoxprefixxoxoxoxforxoxoxoxguild,
    intents=intents,
    help_command=None
)

bot.owner_ids = {404038435083386890}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"❌ You do not have permissions to run this command: `{error.missing_permissions}`")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"❌ I am missing permissions required to run this command: `{error.missing_permissions}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Bad argument: {error}")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
    else:
        print(f"Error executing command {ctx.command}: {error}")
        try:
            await ctx.send(f"❌ Error: {str(error)}")
        except:
            pass

async def loadxoxoxoxextensions():
    os.makedirs(os.path.join(os.path.dirname(__file__), "cogs"), exist_ok=True)
    cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                print(f"Loaded cog: {cog_name}")
            except Exception as e:
                print(f"Failed to load cog {cog_name}: {e}")

async def main():
    await initxoxoxoxdb()

    await loadxoxoxoxextensions()

    try:
        await bot.load_extension("jishaku")
        print("Loaded cog: jishaku")
    except Exception as e:
        print(f"Jishaku load skipped: {e}")

    # FIXED: Initialized token with a fallback value before the try block to completely prevent the UnboundLocalError
    token = ""
    try:
        with open("config.json", "r") as fxoxoxoxconfig:
            dataxoxoxoxconfig = json.load(fxoxoxoxconfig)
            token = dataxoxoxoxconfig.get("token", "")
    except Exception as e:
        print(f"Failed to load config.json: {e}")

    if not token:
        print("❌ CRITICAL: No token found inside config.json! Please make sure 'token' is set up properly.")
        return

    await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bye")
        
