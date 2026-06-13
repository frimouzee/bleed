import discord
from discord.ext import commands
import aiosqlite
import json
import time
import re
from datetime import timedelta
from utils.db import DB_PATH, getxoxoxoxloggingxoxoxoxconfig, setxoxoxoxloggingxoxoxoxconfig

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    guildxoxoxoxid INTEGER,
                    userxoxoxoxid INTEGER,
                    warnxoxoxoxid INTEGER PRIMARY KEY AUTOINCREMENT,
                    moderatorxoxoxoxid INTEGER,
                    reason TEXT,
                    timestamp REAL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS jailed_users (
                    guildxoxoxoxid INTEGER,
                    userxoxoxoxid INTEGER,
                    rolesxoxoxoxjson TEXT,
                    PRIMARY KEY (guildxoxoxoxid, userxoxoxoxid)
                )
            """)
            await db.commit()

    async def logxoxoxoxmodxoxoxoxaction(self, guild: discord.Guild, embed: discord.Embed):
        config = await getxoxoxoxloggingxoxoxoxconfig(guild.id)
        if config:
            channelxoxoxoxid, events = config
            if events == 'all' or 'moderation' in events:
                channel = guild.get_channel(channelxoxoxoxid)
                if channel:
                    try:
                        await channel.send(embed=embed)
                    except:
                        pass

    def parsexoxoxoxduration(self, durationxoxoxoxstr: str) -> timedelta:
        match = re.match(r"^(\d+)\s*(s|sec|m|min|h|hr|d|day|w|week)$", durationxoxoxoxstr.lower().strip())
        if not match:
            raise commands.BadArgument("Invalid duration format (e.g. 10m, 2h, 1d)")

        amount = int(match.group(1))
        unit = match.group(2)

        if unit in ("s", "sec"):
            return timedelta(seconds=amount)
        elif unit in ("m", "min"):
            return timedelta(minutes=amount)
        elif unit in ("h", "hr"):
            return timedelta(hours=amount)
        elif unit in ("d", "day"):
            return timedelta(days=amount)
        elif unit in ("w", "week"):
            return timedelta(weeks=amount)
        return timedelta(minutes=5)

    @commands.command(name="setup")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True, manage_channels=True)
    async def setup(self, ctx):
        guild = ctx.guild

        await ctx.send("⚙️ Starting setup of moderation systems...")

        jail_role = discord.utils.get(guild.roles, name="jailed")
        if not jail_role:
            try:
                jail_role = await guild.create_role(name="jailed", reason="Root setup - jail role")
                await ctx.send("✅ Created role `jailed`")
            except Exception as e:
                await ctx.send(f"❌ Failed to create jail role: {e}")
                return
        else:
            await ctx.send("ℹ️ Role `jailed` already exists.")

        category = discord.utils.get(guild.categories, name="root-moderation")
        if not category:
            try:
                category = await guild.create_category(name="root-moderation", reason="Root setup - moderation category")
                await ctx.send("✅ Created category `root-moderation`")
            except Exception as e:
                await ctx.send(f"❌ Failed to create moderation category: {e}")
                return
        else:
            await ctx.send("ℹ️ Category `root-moderation` already exists.")

        jail_channel = discord.utils.get(category.text_channels, name="jail")
        if not jail_channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                jail_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True)
            }
            try:
                jail_channel = await guild.create_text_channel(
                    name="jail",
                    category=category,
                    overwrites=overwrites,
                    reason="Root setup - jail channel"
                )
                await ctx.send("✅ Created channel `#jail`")
            except Exception as e:
                await ctx.send(f"❌ Failed to create jail channel: {e}")
                return
        else:
            await ctx.send("ℹ️ Channel `#jail` already exists.")

        await ctx.send("⚙️ Configuring channel overrides for `jailed` role...")
        for channel in guild.channels:
            if channel.id == jail_channel.id or channel.categoryxoxoxoxid == category.id:
                continue
            try:
                await channel.set_permissions(jail_role, read_messages=False, reason="Root setup - lock channel from jail")
            except:
                pass

        log_channel = discord.utils.get(category.text_channels, name="moderation-log")
        if not log_channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False)
            }
            try:
                log_channel = await guild.create_text_channel(
                    name="moderation-log",
                    category=category,
                    overwrites=overwrites,
                    reason="Root setup - logging channel"
                )
                await setxoxoxoxloggingxoxoxoxconfig(guild.id, log_channel.id, "all")
                await ctx.send("✅ Created channel `#moderation-log` and configured log output.")
            except Exception as e:
                await ctx.send(f"❌ Failed to create logging channel: {e}")
                return
        else:
            await setxoxoxoxloggingxoxoxoxconfig(guild.id, log_channel.id, "all")
            await ctx.send("ℹ️ Logging channel configured to existing `#moderation-log`.")

        await ctx.send("🎉 **Root Setup Completed Successfully!** Jailed users will be restricted to the `#jail` channel.")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot kick members with higher or equal hierarchy roles.")
            return
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot kick this user because their top role is above mine.")
            return

        embed = discord.Embed(title="Member Kicked", color=discord.Color.orange(), timestamp=ctx.message.created_at)
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        try:
            await member.send(f"⚠️ You were kicked from **{ctx.guild.name}**\nReason: {reason}")
        except:
            pass

        await member.kick(reason=f"Kicked by {ctx.author}: {reason}")
        await ctx.send(f"✅ **{member}** has been kicked. | {reason}")
        await self.logxoxoxoxmodxoxoxoxaction(ctx.guild, embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot ban members with higher or equal hierarchy roles.")
            return
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot ban this user because their top role is above mine.")
            return

        embed = discord.Embed(title="Member Banned", color=discord.Color.red(), timestamp=ctx.message.created_at)
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        try:
            await member.send(f"⛔ You were banned from **{ctx.guild.name}**\nReason: {reason}")
        except:
            pass

        await member.ban(reason=f"Banned by {ctx.author}: {reason}", delete_message_days=0)
        await ctx.send(f"✅ **{member}** has been banned. | {reason}")
        await self.logxoxoxoxmodxoxoxoxaction(ctx.guild, embed)

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, userxoxoxoxid: int, *, reason: str = "No reason provided"):
        try:
            user = await self.bot.fetch_user(userxoxoxoxid)
            await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author}: {reason}")

            embed = discord.Embed(title="Member Unbanned", color=discord.Color.green(), timestamp=ctx.message.created_at)
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)

            await ctx.send(f"✅ **{user}** has been unbanned.")
            await self.logxoxoxoxmodxoxoxoxaction(ctx.guild, embed)
        except discord.NotFound:
            await ctx.send("❌ Ban not found for this user ID.")
        except Exception as e:
            await ctx.send(f"❌ Failed to unban: {e}")

    @commands.command(name="jail")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def jail(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        guild = ctx.guild
        jail_role = discord.utils.get(guild.roles, name="jailed")
        if not jail_role:
            await ctx.send("❌ Jail system is not set up. Run `,setup` first.")
            return

        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot jail members with higher or equal hierarchy roles.")
            return
        if member.id == ctx.author.id or member.id == self.bot.user.id:
            await ctx.send("❌ You cannot jail yourself or the bot.")
            return

        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT 1 FROM jailed_users WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ?", (guild.id, member.id)) as cursor:
                if await cursor.fetchone():
                    await ctx.send("ℹ️ This user is already jailed.")
                    return

        member_rolexoxoxoxids = [role.id for role in member.roles if not role.is_default() and role < guild.me.top_role]

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO jailed_users (guildxoxoxoxid, userxoxoxoxid, rolesxoxoxoxjson) VALUES (?, ?, ?)
            """, (guild.id, member.id, json.dumps(member_rolexoxoxoxids)))
            await db.commit()

        try:
            rolesxoxoxoxtoxoxoxoxremove = [role for role in member.roles if not role.is_default() and role < guild.me.top_role and not role.is_integration()]
            await member.remove_roles(*rolesxoxoxoxtoxoxoxoxremove, reason="Jailed - role stripping")
            await member.add_roles(jail_role, reason=f"Jailed by {ctx.author}: {reason}")

            embed = discord.Embed(title="Member Jailed", color=discord.Color.dark_grey(), timestamp=ctx.message.created_at)
            embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)

            await ctx.send(f"🔒 **{member}** has been jailed. Check `#jail`.")

            jail_channel = discord.utils.get(guild.text_channels, name="jail")
            if jail_channel:
                await jail_channel.send(f"⚠️ {member.mention}, you have been jailed by {ctx.author.mention} for: **{reason}**.")

            await self.logxoxoxoxmodxoxoxoxaction(guild, embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to jail user: {e}")
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("DELETE FROM jailed_users WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ?", (guild.id, member.id))
                await db.commit()

    @commands.command(name="unjail")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unjail(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        guild = ctx.guild
        jail_role = discord.utils.get(guild.roles, name="jailed")

        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT rolesxoxoxoxjson FROM jailed_users WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ?", (guild.id, member.id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    await ctx.send("❌ This user is not listed as jailed in my database.")
                    return
                savedxoxoxoxrolexoxoxoxids = json.loads(row[0])

        try:
            if jail_role in member.roles:
                await member.remove_roles(jail_role, reason="Unjailed")

            rolesxoxoxoxtoxoxoxoxadd = []
            for r_id in savedxoxoxoxrolexoxoxoxids:
                role = guild.get_role(r_id)
                if role and role < guild.me.top_role and not role.is_default() and not role.is_integration():
                    rolesxoxoxoxtoxoxoxoxadd.append(role)

            if rolesxoxoxoxtoxoxoxoxadd:
                await member.add_roles(*rolesxoxoxoxtoxoxoxoxadd, reason=f"Unjailed - roles restored by {ctx.author}")

            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("DELETE FROM jailed_users WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ?", (guild.id, member.id))
                await db.commit()

            embed = discord.Embed(title="Member Unjailed", color=discord.Color.green(), timestamp=ctx.message.created_at)
            embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)

            await ctx.send(f"🔓 **{member}** has been unjailed.")
            await self.logxoxoxoxmodxoxoxoxaction(guild, embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to restore roles: {e}")

    @commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot mute members with higher or equal hierarchy roles.")
            return

        try:
            delta = self.parsexoxoxoxduration(duration)
            await member.timeout(delta, reason=f"Muted by {ctx.author}: {reason}")

            embed = discord.Embed(title="Member Muted (Timeout)", color=discord.Color.orange(), timestamp=ctx.message.created_at)
            embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)

            await ctx.send(f"🔇 **{member}** has been muted for {duration}. | {reason}")
            await self.logxoxoxoxmodxoxoxoxaction(ctx.guild, embed)
        except ValueError as e:
            await ctx.send(f"❌ {e}")
        except Exception as e:
            await ctx.send(f"❌ Failed to mute: {e}")

    @commands.command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if not member.is_timed_out():
            await ctx.send("ℹ️ This user is not muted.")
            return

        try:
            await member.timeout(None, reason=f"Unmuted by {ctx.author}: {reason}")

            embed = discord.Embed(title="Member Unmuted", color=discord.Color.green(), timestamp=ctx.message.created_at)
            embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)

            await ctx.send(f"🔊 **{member}** has been unmuted.")
            await self.logxoxoxoxmodxoxoxoxaction(ctx.guild, embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to unmute: {e}")

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot warn members with higher or equal hierarchy roles.")
            return

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO warnings (guildxoxoxoxid, userxoxoxoxid, moderatorxoxoxoxid, reason, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (ctx.guild.id, member.id, ctx.author.id, reason, time.time()))
            await db.commit()

        embed = discord.Embed(title="Member Warned", color=discord.Color.yellow(), timestamp=ctx.message.created_at)
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        try:
            await member.send(f"⚠️ You received a warning in **{ctx.guild.name}**\nReason: {reason}")
        except:
            pass

        await ctx.send(f"⚠️ **{member}** has been warned. | {reason}")
        await self.logxoxoxoxmodxoxoxoxaction(ctx.guild, embed)

    @commands.command(name="warns")
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member: discord.Member):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("""
                SELECT warnxoxoxoxid, moderatorxoxoxoxid, reason, timestamp FROM warnings
                WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ? ORDER BY timestamp DESC
            """, (ctx.guild.id, member.id)) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await ctx.send(f"ℹ️ **{member}** has no warnings.")
            return

        embed = discord.Embed(title=f"Warnings for {member}", color=discord.Color.yellow())
        embed.set_thumbnail(url=member.display_avatar.url)

        for r_id, mod_id, reason, ts in rows:
            mod = ctx.guild.get_member(mod_id) or f"Unknown ID ({mod_id})"
            date = f"<t:{int(ts)}:F>"
            embed.add_field(
                name=f"Warn #{r_id} | Mod: {mod}",
                value=f"📅 {date}\n📝 Reason: {reason}",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))