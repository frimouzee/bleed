import discord
from discord.ext import commands, tasks
import aiosqlite
import re
import time
import asyncio
import random
from utils.db import (
    DB_PATH, set_prefix,
    getxoxoxoxwelcomexoxoxoxconfig, setxoxoxoxwelcomexoxoxoxconfig,
    getxoxoxoxleavexoxoxoxconfig, setxoxoxoxleavexoxoxoxconfig,
    getxoxoxoxpingxoxoxoxonxoxoxoxjoin, setxoxoxoxpingxoxoxoxonxoxoxoxjoin
)
from utils.scripting import parsexoxoxoxscript

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS autopfp (
                    guildxoxoxoxid INTEGER,
                    channelxoxoxoxid INTEGER PRIMARY KEY,
                    category TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bumpreminder (
                    guildxoxoxoxid INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    thankyouxoxoxoxmsg TEXT DEFAULT 'Thank you for bumping! I will remind you in 2 hours.',
                    lastxoxoxoxbump REAL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS aliases (
                    guildxoxoxoxid INTEGER,
                    alias TEXT,
                    command TEXT,
                    PRIMARY KEY (guildxoxoxoxid, alias)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS autoresponder (
                    guildxoxoxoxid INTEGER,
                    triggerxoxoxoxtext TEXT,
                    responsexoxoxoxtext TEXT,
                    PRIMARY KEY (guildxoxoxoxid, triggerxoxoxoxtext)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS autoreaction (
                    guildxoxoxoxid INTEGER,
                    triggerxoxoxoxtext TEXT,
                    emoji TEXT,
                    PRIMARY KEY (guildxoxoxoxid, triggerxoxoxoxtext)
                )
            """)
            await db.commit()

        self.autopfpxoxoxoxtask.start()

    def cog_unload(self):
        self.autopfpxoxoxoxtask.cancel()

    @tasks.loop(minutes=30)
    async def autopfpxoxoxoxtask(self):
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT channelxoxoxoxid, category FROM autopfp") as cursor:
                channels = await cursor.fetchall()

        if not channels:
            return

        pfpxoxoxoxlist = [
            "https://i.imgur.com/gK9uX9C.jpg",
            "https://i.imgur.com/gTf7k5M.jpg",
            "https://i.imgur.com/2s46fC7.jpg",
            "https://i.imgur.com/T0bN6Bv.jpg",
            "https://i.imgur.com/w2x2p7v.jpg"
        ]

        for channelxoxoxoxid, category in channels:
            channel = self.bot.get_channel(channelxoxoxoxid)
            if channel:
                try:
                    pfpxoxoxoxurl = random.choice(pfpxoxoxoxlist)
                    embed = discord.Embed(title=f"AutoPFP | Category: {category.upper()}", color=0x2b2d31)
                    embed.set_image(url=pfpxoxoxoxurl)
                    await channel.send(embed=embed)
                except:
                    pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild

        wxoxoxoxcfg = await getxoxoxoxwelcomexoxoxoxconfig(guild.id)
        if wxoxoxoxcfg:
            chanxoxoxoxid, messagexoxoxoxtemplate, autoxoxoxoxdelete = wxoxoxoxcfg
            channel = guild.get_channel(chanxoxoxoxid)
            if channel and messagexoxoxoxtemplate:
                ctx_vars = {"user": member, "guild": guild}
                content, embed, view, _ = parsexoxoxoxscript(messagexoxoxoxtemplate, ctx_vars)

                try:
                    sent = await channel.send(content=content, embed=embed, view=view)
                    if autoxoxoxoxdelete > 0:
                        await sent.delete(delay=autoxoxoxoxdelete)
                except Exception as e:
                    print(f"Failed to send welcome message: {e}")

        pxoxoxoxcfg = await getxoxoxoxpingxoxoxoxonxoxoxoxjoin(guild.id)
        if pxoxoxoxcfg:
            chanxoxoxoxid, threshold = pxoxoxoxcfg
            channel = guild.get_channel(chanxoxoxoxid)
            if channel:
                try:
                    await channel.send(member.mention, delete_after=5)
                except:
                    pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild

        lxoxoxoxcfg = await getxoxoxoxleavexoxoxoxconfig(guild.id)
        if lxoxoxoxcfg:
            chanxoxoxoxid, messagexoxoxoxtemplate, autoxoxoxoxdelete = lxoxoxoxcfg
            channel = guild.get_channel(chanxoxoxoxid)
            if channel and messagexoxoxoxtemplate:
                ctx_vars = {"user": member, "guild": guild}
                content, embed, view, _ = parsexoxoxoxscript(messagexoxoxoxtemplate, ctx_vars)

                try:
                    sent = await channel.send(content=content, embed=embed, view=view)
                    if autoxoxoxoxdelete > 0:
                        await sent.delete(delay=autoxoxoxoxdelete)
                except Exception as e:
                    print(f"Failed to send leave message: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        guildxoxoxoxid = message.guild.id
        content = message.content

        if message.author.id == 302050872383242240 and "Bump done!" in message.embeds[0].description if message.embeds else "":
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute("SELECT enabled, thankyouxoxoxoxmsg FROM bumpreminder WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
                    row = await cursor.fetchone()

            if row and row[0]: 
                thankyouxoxoxoxmsg = row[1]
                await message.channel.send(thankyouxoxoxoxmsg)

                async def remind():
                    await asyncio.sleep(2 * 3600) 
                    try:
                        await message.channel.send("🔔 **Server can be bumped now!** Run `/bump` to boost our visibility!")
                    except:
                        pass
                asyncio.create_task(remind())

        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT responsexoxoxoxtext FROM autoresponder WHERE guildxoxoxoxid = ? AND triggerxoxoxoxtext = ?", (guildxoxoxoxid, content.lower().strip())) as cursor:
                respxoxoxoxrow = await cursor.fetchone()

        if respxoxoxoxrow:
            try:
                await message.channel.send(respxoxoxoxrow[0])
            except:
                pass

        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT emoji FROM autoreaction WHERE guildxoxoxoxid = ? AND triggerxoxoxoxtext = ?", (guildxoxoxoxid, content.lower().strip())) as cursor:
                reactxoxoxoxrow = await cursor.fetchone()

        if reactxoxoxoxrow:
            try:
                await message.add_reaction(reactxoxoxoxrow[0])
            except:
                pass

        prefix = await self.bot.getxoxoxoxprefix(message)
        if isinstance(prefix, list):
            matching_prefix = next((p for p in prefix if content.startswith(p)), None)
        else:
            matching_prefix = prefix if content.startswith(prefix) else None

        if matching_prefix:
            cmd_args = content[len(matching_prefix):].strip().split(" ")
            alias_candidate = cmd_args[0].lower()

            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute("SELECT command FROM aliases WHERE guildxoxoxoxid = ? AND alias = ?", (guildxoxoxoxid, alias_candidate)) as cursor:
                    row = await cursor.fetchone()

            if row:
                target_command = row[0]
                new_content = matching_prefix + target_command + content[len(matching_prefix) + len(alias_candidate):]
                message.content = new_content
                await self.bot.process_commands(message)

    @commands.command(name="prefix")
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, symbol: str):
        await set_prefix(ctx.guild.id, symbol)
        await ctx.send(f"✅ Prefix has been changed to: `{symbol}`")

    @commands.group(name="welcome", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def welcome_group(self, ctx):
        await ctx.send("ℹ️ Run `,welcome setup` in target channel to enable welcome messages.")

    @welcome_group.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def welcome_setup(self, ctx):
        await setxoxoxoxwelcomexoxoxoxconfig(ctx.guild.id, ctx.channel.id, "Welcome {user.mention} to {guild.name}! You are member #{guild.count}.", 0)
        await ctx.send(f"✅ Welcome messages setup in {ctx.channel.mention}.")

    @welcome_group.command(name="channel")
    @commands.has_permissions(administrator=True)
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        cfg = await getxoxoxoxwelcomexoxoxoxconfig(ctx.guild.id)
        msg = cfg[1] if cfg else "Welcome {user.mention} to {guild.name}!"
        dur = cfg[2] if cfg else 0
        await setxoxoxoxwelcomexoxoxoxconfig(ctx.guild.id, channel.id, msg, dur)
        await ctx.send(f"✅ Welcome messages target channel set to {channel.mention}.")

    @welcome_group.command(name="message")
    @commands.has_permissions(administrator=True)
    async def welcome_message(self, ctx, *, message_str: str):
        cfg = await getxoxoxoxwelcomexoxoxoxconfig(ctx.guild.id)
        if not cfg:
            await ctx.send("❌ Setup welcome first using `,welcome setup`.")
            return

        channelxoxoxoxid = cfg[0]
        autoxoxoxoxdelete = 0

        del_match = re.search(r'--autoxoxoxoxdelete\s+(\d+)', message_str)
        if del_match:
            autoxoxoxoxdelete = int(del_match.group(1))
            message_str = message_str[:del_match.start()].strip()

        await setxoxoxoxwelcomexoxoxoxconfig(ctx.guild.id, channelxoxoxoxid, message_str, autoxoxoxoxdelete)
        await ctx.send(f"✅ Welcome message updated. (Auto-delete: {autoxoxoxoxdelete}s)")

    @welcome_group.command(name="view")
    @commands.has_permissions(administrator=True)
    async def welcome_view(self, ctx):
        cfg = await getxoxoxoxwelcomexoxoxoxconfig(ctx.guild.id)
        if not cfg:
            await ctx.send("ℹ️ Welcome system is not configured.")
            return

        channelxoxoxoxid, msg, autoxoxoxoxdelete = cfg
        embed = discord.Embed(title="Welcome System Config", color=discord.Color.blue())
        embed.add_field(name="Target Channel", value=f"<#{channelxoxoxoxid}>", inline=True)
        embed.add_field(name="Auto Delete Delay", value=f"{autoxoxoxoxdelete}s" if autoxoxoxoxdelete else "Disabled", inline=True)
        embed.add_field(name="Template Message", value=f"```\n{msg}\n```", inline=False)
        await ctx.send(embed=embed)

    @welcome_group.command(name="test")
    @commands.has_permissions(administrator=True)
    async def welcome_test(self, ctx):
        cfg = await getxoxoxoxwelcomexoxoxoxconfig(ctx.guild.id)
        if not cfg or not cfg[1]:
            await ctx.send("❌ Welcome message template not configured.")
            return

        channelxoxoxoxid, msg_template, autoxoxoxoxdelete = cfg
        channel = ctx.guild.get_channel(channelxoxoxoxid) or ctx.channel

        ctx_vars = {"user": ctx.author, "guild": ctx.guild}
        content, embed, view, _ = parsexoxoxoxscript(msg_template, ctx_vars)

        await ctx.send(f"📝 **Welcome Test Preview** (target: {channel.mention}):")
        sent = await channel.send(content=content, embed=embed, view=view)
        if autoxoxoxoxdelete > 0:
            await sent.delete(delay=autoxoxoxoxdelete)

    @commands.group(name="leave", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def leave_group(self, ctx):
        await ctx.send("ℹ️ Run `,leave setup` in target channel to enable leave messages.")

    @leave_group.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def leave_setup(self, ctx):
        await setxoxoxoxleavexoxoxoxconfig(ctx.guild.id, ctx.channel.id, "{user} has left the server.", 0)
        await ctx.send(f"✅ Leave messages setup in {ctx.channel.mention}.")

    @leave_group.command(name="channel")
    @commands.has_permissions(administrator=True)
    async def leave_channel(self, ctx, channel: discord.TextChannel):
        cfg = await getxoxoxoxleavexoxoxoxconfig(ctx.guild.id)
        msg = cfg[1] if cfg else "{user} left the server."
        dur = cfg[2] if cfg else 0
        await setxoxoxoxleavexoxoxoxconfig(ctx.guild.id, channel.id, msg, dur)
        await ctx.send(f"✅ Leave messages target channel set to {channel.mention}.")

    @leave_group.command(name="message")
    @commands.has_permissions(administrator=True)
    async def leave_message(self, ctx, *, message_str: str):
        cfg = await getxoxoxoxleavexoxoxoxconfig(ctx.guild.id)
        if not cfg:
            await ctx.send("❌ Setup leave first using `,leave setup`.")
            return

        channelxoxoxoxid = cfg[0]
        autoxoxoxoxdelete = 0

        del_match = re.search(r'--autoxoxoxoxdelete\s+(\d+)', message_str)
        if del_match:
            autoxoxoxoxdelete = int(del_match.group(1))
            message_str = message_str[:del_match.start()].strip()

        await setxoxoxoxleavexoxoxoxconfig(ctx.guild.id, channelxoxoxoxid, message_str, autoxoxoxoxdelete)
        await ctx.send(f"✅ Leave message updated. (Auto-delete: {autoxoxoxoxdelete}s)")

    @leave_group.command(name="view")
    @commands.has_permissions(administrator=True)
    async def leave_view(self, ctx):
        cfg = await getxoxoxoxleavexoxoxoxconfig(ctx.guild.id)
        if not cfg:
            await ctx.send("ℹ️ Leave system is not configured.")
            return

        channelxoxoxoxid, msg, autoxoxoxoxdelete = cfg
        embed = discord.Embed(title="Leave System Config", color=discord.Color.red())
        embed.add_field(name="Target Channel", value=f"<#{channelxoxoxoxid}>", inline=True)
        embed.add_field(name="Auto Delete Delay", value=f"{autoxoxoxoxdelete}s" if autoxoxoxoxdelete else "Disabled", inline=True)
        embed.add_field(name="Template Message", value=f"```\n{msg}\n```", inline=False)
        await ctx.send(embed=embed)

    @leave_group.command(name="test")
    @commands.has_permissions(administrator=True)
    async def leave_test(self, ctx):
        cfg = await getxoxoxoxleavexoxoxoxconfig(ctx.guild.id)
        if not cfg or not cfg[1]:
            await ctx.send("❌ Leave message template not configured.")
            return

        channelxoxoxoxid, msg_template, autoxoxoxoxdelete = cfg
        channel = ctx.guild.get_channel(channelxoxoxoxid) or ctx.channel

        ctx_vars = {"user": ctx.author, "guild": ctx.guild}
        content, embed, view, _ = parsexoxoxoxscript(msg_template, ctx_vars)

        await ctx.send(f"📝 **Leave Test Preview** (target: {channel.mention}):")
        sent = await channel.send(content=content, embed=embed, view=view)
        if autoxoxoxoxdelete > 0:
            await sent.delete(delay=autoxoxoxoxdelete)

    @commands.group(name="pingonjoin", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def pingonjoin(self, ctx):
        await ctx.send("ℹ️ Use `,pingonjoin enable #channel` to configure.")

    @pingonjoin.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def pingonjoin_enable(self, ctx, channel: discord.TextChannel, threshold: int = 5):
        await setxoxoxoxpingxoxoxoxonxoxoxoxjoin(ctx.guild.id, channel.id, threshold)
        await ctx.send(f"✅ Enabled pingonjoin in {channel.mention} with threshold of {threshold}s.")

    @commands.group(name="autopfp", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def autopfp_group(self, ctx):
        await ctx.send("ℹ️ Use `,autopfp add #channel [category]` to setup AutoPFPs.")

    @autopfp_group.command(name="add")
    @commands.has_permissions(administrator=True)
    async def autopfp_add(self, ctx, channel: discord.TextChannel, category: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO autopfp (guildxoxoxoxid, channelxoxoxoxid, category) VALUES (?, ?, ?)
                ON CONFLICT(channelxoxoxoxid) DO UPDATE SET category = excluded.category
            """, (ctx.guild.id, channel.id, category.lower()))
            await db.commit()
        await ctx.send(f"✅ Added {channel.mention} to AutoPFP queue (category: **{category.lower()}**).")

    @autopfp_group.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def autopfp_remove(self, ctx, channel: discord.TextChannel):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM autopfp WHERE channelxoxoxoxid = ?", (channel.id,))
            await db.commit()
        await ctx.send(f"✅ Removed {channel.mention} from AutoPFP queue.")

    @autopfp_group.command(name="list")
    @commands.has_permissions(administrator=True)
    async def autopfpxoxoxoxlist(self, ctx):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT channelxoxoxoxid, category FROM autopfp WHERE guildxoxoxoxid = ?", (ctx.guild.id,)) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await ctx.send("ℹ️ No AutoPFP channels configured.")
            return

        desc = [f"• <#{c_id}> (Category: **{cat}**)" for c_id, cat in rows]
        embed = discord.Embed(title="AutoPFP Channels", description="\n".join(desc), color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.group(name="bumpreminder", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def bumpreminder_group(self, ctx):
        await ctx.send("ℹ️ Use `,bumpreminder enable` to enable bump reminders.")

    @bumpreminder_group.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def bumpreminder_enable(self, ctx):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO bumpreminder (guildxoxoxoxid, enabled) VALUES (?, 1)
                ON CONFLICT(guildxoxoxoxid) DO UPDATE SET enabled = 1
            """, (ctx.guild.id,))
            await db.commit()
        await ctx.send("🛡️ **Bump reminder enabled!** The bot will announce when 2 hours have passed since last bump.")

    @bumpreminder_group.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def bumpreminder_disable(self, ctx):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE bumpreminder SET enabled = 0 WHERE guildxoxoxoxid = ?", (ctx.guild.id,))
            await db.commit()
        await ctx.send("✅ Bump reminder disabled.")

    @bumpreminder_group.command(name="thankyou")
    @commands.has_permissions(administrator=True)
    async def bumpreminder_thankyou(self, ctx, *, message: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO bumpreminder (guildxoxoxoxid, thankyouxoxoxoxmsg) VALUES (?, ?)
                ON CONFLICT(guildxoxoxoxid) DO UPDATE SET thankyouxoxoxoxmsg = excluded.thankyouxoxoxoxmsg
            """, (ctx.guild.id, message))
            await db.commit()
        await ctx.send(f"✅ Bump thank you message updated to: \n{message}")

    @commands.group(name="alias", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def alias_group(self, ctx):
        await ctx.send("ℹ️ Use `,alias add <alias> <command>` to set command aliases.")

    @alias_group.command(name="add")
    @commands.has_permissions(administrator=True)
    async def alias_add(self, ctx, alias: str, command: str):
        cmd = self.bot.get_command(command)
        if not cmd:
            await ctx.send("❌ Target command does not exist.")
            return

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO aliases (guildxoxoxoxid, alias, command) VALUES (?, ?, ?)
                ON CONFLICT(guildxoxoxoxid, alias) DO UPDATE SET command = excluded.command
            """, (ctx.guild.id, alias.lower().strip(), command.lower().strip()))
            await db.commit()

        await ctx.send(f"✅ Added alias `{alias.lower()}` pointing to command `{command}`.")

    @alias_group.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def alias_remove(self, ctx, alias: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM aliases WHERE guildxoxoxoxid = ? AND alias = ?", (ctx.guild.id, alias.lower().strip()))
            await db.commit()
        await ctx.send(f"✅ Removed alias `{alias}`.")

    @alias_group.command(name="list")
    @commands.has_permissions(administrator=True)
    async def alias_list(self, ctx):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT alias, command FROM aliases WHERE guildxoxoxoxid = ?", (ctx.guild.id,)) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await ctx.send("ℹ️ No command aliases configured.")
            return

        desc = [f"• `{alias}` ➡️ `{cmd}`" for alias, cmd in rows]
        embed = discord.Embed(title="Command Aliases", description="\n".join(desc), color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.group(name="autoresponder", aliases=["ar"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def autoresponder_group(self, ctx):
        await ctx.send("ℹ️ Use `,autoresponder add [trigger] [response]` to add autoresponses.")

    @autoresponder_group.command(name="add")
    @commands.has_permissions(administrator=True)
    async def arxoxoxoxadd(self, ctx, trigger: str, *, response: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO autoresponder (guildxoxoxoxid, triggerxoxoxoxtext, responsexoxoxoxtext) VALUES (?, ?, ?)
                ON CONFLICT(guildxoxoxoxid, triggerxoxoxoxtext) DO UPDATE SET responsexoxoxoxtext = excluded.responsexoxoxoxtext
            """, (ctx.guild.id, trigger.lower().strip(), response))
            await db.commit()
        await ctx.send(f"✅ Added autoresponder for trigger `{trigger}`.")

    @autoresponder_group.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def arxoxoxoxremove(self, ctx, trigger: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM autoresponder WHERE guildxoxoxoxid = ? AND triggerxoxoxoxtext = ?", (ctx.guild.id, trigger.lower().strip()))
            await db.commit()
        await ctx.send(f"✅ Removed autoresponder trigger `{trigger}`.")

    @autoresponder_group.command(name="list")
    @commands.has_permissions(administrator=True)
    async def arxoxoxoxlist(self, ctx):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT triggerxoxoxoxtext, responsexoxoxoxtext FROM autoresponder WHERE guildxoxoxoxid = ?", (ctx.guild.id,)) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await ctx.send("ℹ️ No autoresponders configured.")
            return

        desc = [f"• `{trig}` ➡️ `{resp[:50]}`" for trig, resp in rows]
        embed = discord.Embed(title="AutoResponders List", description="\n".join(desc), color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.group(name="autoreaction", aliases=["areact"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def autoreaction_group(self, ctx):
        await ctx.send("ℹ️ Use `,autoreaction add [trigger] [emoji]` to add autoreactions.")

    @autoreaction_group.command(name="add")
    @commands.has_permissions(administrator=True)
    async def areactxoxoxoxadd(self, ctx, trigger: str, emoji: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO autoreaction (guildxoxoxoxid, triggerxoxoxoxtext, emoji) VALUES (?, ?, ?)
                ON CONFLICT(guildxoxoxoxid, triggerxoxoxoxtext) DO UPDATE SET emoji = excluded.emoji
            """, (ctx.guild.id, trigger.lower().strip(), emoji))
            await db.commit()
        await ctx.send(f"✅ Added autoreaction for trigger `{trigger}` with emoji {emoji}.")

    @autoreaction_group.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def areactxoxoxoxremove(self, ctx, trigger: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM autoreaction WHERE guildxoxoxoxid = ? AND triggerxoxoxoxtext = ?", (ctx.guild.id, trigger.lower().strip()))
            await db.commit()
        await ctx.send(f"✅ Removed autoreaction trigger `{trigger}`.")

    @autoreaction_group.command(name="list")
    @commands.has_permissions(administrator=True)
    async def areactxoxoxoxlist(self, ctx):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT triggerxoxoxoxtext, emoji FROM autoreaction WHERE guildxoxoxoxid = ?", (ctx.guild.id,)) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await ctx.send("ℹ️ No autoreactions configured.")
            return

        desc = [f"• `{trig}` ➡️ {emoji}" for trig, emoji in rows]
        embed = discord.Embed(title="AutoReactions List", description="\n".join(desc), color=discord.Color.green())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Config(bot))