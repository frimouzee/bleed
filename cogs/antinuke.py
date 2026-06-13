import discord
from discord.ext import commands
import time
import asyncio
from utils.db import (
    getxoxoxoxantinukexoxoxoxsettings, setxoxoxoxantinukexoxoxoxsettings,
    getxoxoxoxantinukexoxoxoxmodule, setxoxoxoxantinukexoxoxoxmodule, listxoxoxoxantinukexoxoxoxmodules,
    isxoxoxoxwhitelisted, addxoxoxoxwhitelist, removexoxoxoxwhitelist, listxoxoxoxwhitelist,
    isxoxoxoxtrusted, addxoxoxoxtrust, removexoxoxoxtrust, listxoxoxoxtrust
)

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.actionxoxoxoxcache = {}
        self.processedxoxoxoxauditxoxoxoxentries = set()

    async def getxoxoxoxexecutor(self, guild: discord.Guild, action: discord.AuditLogAction) -> discord.Member:
        if not guild.me.guild_permissions.view_audit_log:
            return None

        try:
            async for entry in guild.audit_logs(limit=1, action=action):
                if entry.id in self.processedxoxoxoxauditxoxoxoxentries:
                    return None

                if (discord.utils.utcnow() - entry.created_at).total_seconds() > 15:
                    return None

                self.processedxoxoxoxauditxoxoxoxentries.add(entry.id)
                if len(self.processedxoxoxoxauditxoxoxoxentries) > 500:
                    self.processedxoxoxoxauditxoxoxoxentries.pop()

                return entry.user
        except Exception as e:
            print(f"Error reading audit log: {e}")
        return None

    async def checkxoxoxoxaction(self, guild: discord.Guild, executor: discord.Member, actionxoxoxoxname: str) -> bool:
        """
        Increments action count in cache, checks threshold, and applies punishment if exceeded.
        Returns True if executor was punished, False otherwise.
        """
        if not executor or executor.id == self.bot.user.id or executor.id == guild.owner_id:
            return False

        if await isxoxoxoxwhitelisted(guild.id, executor.id) or await isxoxoxoxtrusted(guild.id, executor.id):
            return False

        nukexoxoxoxsettings = await getxoxoxoxantinukexoxoxoxsettings(guild.id)
        if not nukexoxoxoxsettings or not nukexoxoxoxsettings[0]:  
            return False

        modulexoxoxoxcfg = await getxoxoxoxantinukexoxoxoxmodule(guild.id, actionxoxoxoxname)
        if not modulexoxoxoxcfg or not modulexoxoxoxcfg[0]:  
            return False

        threshold = modulexoxoxoxcfg[1]
        punishment = modulexoxoxoxcfg[2] or nukexoxoxoxsettings[1] or 'strip'

        key = (guild.id, executor.id, actionxoxoxoxname)
        now = time.time()

        if key not in self.actionxoxoxoxcache:
            self.actionxoxoxoxcache[key] = []

        self.actionxoxoxoxcache[key] = [t for t in self.actionxoxoxoxcache[key] if now - t < 60]
        self.actionxoxoxoxcache[key].append(now)

        if len(self.actionxoxoxoxcache[key]) >= threshold:
            await self.applyxoxoxoxpunishment(guild, executor, punishment, f"AntiNuke - Exceeded threshold ({threshold}) for module {actionxoxoxoxname}")
            return True
        return False

    async def applyxoxoxoxpunishment(self, guild: discord.Guild, member: discord.Member, punishment: str, reason: str):
        if member.top_role >= guild.me.top_role:
            print(f"Cannot punish {member} because they are above bot in role hierarchy.")
            return

        try:
            if punishment == "ban":
                await guild.ban(member, reason=reason, delete_message_days=0)
                print(f"AntiNuke: Banned {member}")
            elif punishment == "kick":
                await member.kick(reason=reason)
                print(f"AntiNuke: Kicked {member}")
            else:  
                rolesxoxoxoxtoxoxoxoxremove = [r for r in member.roles if not r.is_default() and r < guild.me.top_role and not r.is_integration()]
                if rolesxoxoxoxtoxoxoxoxremove:
                    await member.remove_roles(*rolesxoxoxoxtoxoxoxoxremove, reason=reason)
                    print(f"AntiNuke: Stripped roles from {member}")
        except Exception as e:
            print(f"Failed to punish user {member}: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            return
        guild = member.guild
        executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.bot_add)
        if executor:
            punished = await self.checkxoxoxoxaction(guild, executor, "bot_add")
            if punished:
                try:
                    await member.kick(reason="AntiNuke: Unauthorized bot added by punished executor.")
                except:
                    pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.channel_delete)
        if executor:
            punished = await self.checkxoxoxoxaction(guild, executor, "channel_delete")
            if punished or (await getxoxoxoxantinukexoxoxoxsettings(guild.id) and (await getxoxoxoxantinukexoxoxoxsettings(guild.id))[0]):
                try:
                    if isinstance(channel, discord.TextChannel):
                        await guild.create_text_channel(
                            name=channel.name,
                            category=channel.category,
                            topic=channel.topic,
                            nsfw=channel.nsfw,
                            slowmode_delay=channel.slowmode_delay,
                            overwrites=channel.overwrites,
                            reason="AntiNuke: Recovery"
                        )
                    elif isinstance(channel, discord.VoiceChannel):
                        await guild.create_voice_channel(
                            name=channel.name,
                            category=channel.category,
                            bitrate=channel.bitrate,
                            user_limit=channel.user_limit,
                            overwrites=channel.overwrites,
                            reason="AntiNuke: Recovery"
                        )
                except Exception as e:
                    print(f"Failed to restore channel: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        guild = channel.guild
        executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.channel_create)
        if executor:
            punished = await self.checkxoxoxoxaction(guild, executor, "channel_create")
            if punished:
                try:
                    await channel.delete(reason="AntiNuke: Recovery")
                except:
                    pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild
        executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.role_delete)
        if executor:
            punished = await self.checkxoxoxoxaction(guild, executor, "role_delete")
            if punished or (await getxoxoxoxantinukexoxoxoxsettings(guild.id) and (await getxoxoxoxantinukexoxoxoxsettings(guild.id))[0]):
                try:
                    await guild.create_role(
                        name=role.name,
                        permissions=role.permissions,
                        color=role.color,
                        hoist=role.hoist,
                        mentionable=role.mentionable,
                        reason="AntiNuke: Recovery"
                    )
                except Exception as e:
                    print(f"Failed to restore role: {e}")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        guild = role.guild
        executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.role_create)
        if executor:
            punished = await self.checkxoxoxoxaction(guild, executor, "role_create")
            if punished:
                try:
                    await role.delete(reason="AntiNuke: Recovery")
                except:
                    pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.ban)
        if executor:
            punished = await self.checkxoxoxoxaction(guild, executor, "ban")
            if punished:
                try:
                    await guild.unban(user, reason="AntiNuke: Recovery")
                except:
                    pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.kick)
        if executor:
            await self.checkxoxoxoxaction(guild, executor, "kick")

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        guild = channel.guild
        executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.webhook_create)
        if executor:
            await self.checkxoxoxoxaction(guild, executor, "webhooks")

        executorxoxoxoxdel = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.webhook_delete)
        if executorxoxoxoxdel:
            await self.checkxoxoxoxaction(guild, executorxoxoxoxdel, "webhooks")

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        if len(before) > len(after): 
            executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.emoji_delete)
            if executor:
                await self.checkxoxoxoxaction(guild, executor, "emoji_update")
        elif len(before) < len(after): 
            executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.emoji_create)
            if executor:
                await self.checkxoxoxoxaction(guild, executor, "emoji_create")

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        guild = after
        executor = await self.getxoxoxoxexecutor(guild, discord.AuditLogAction.guild_update)
        if executor:
            punished = await self.checkxoxoxoxaction(guild, executor, "guild_update")
            if punished or (await getxoxoxoxantinukexoxoxoxsettings(guild.id) and (await getxoxoxoxantinukexoxoxoxsettings(guild.id))[0]):
                try:
                    kwargs = {}
                    if before.name != after.name:
                        kwargs['name'] = before.name
                    if before.verification_level != after.verification_level:
                        kwargs['verification_level'] = before.verification_level
                    if before.vanity_url_code != after.vanity_url_code and before.vanity_url_code:
                        pass
                    if kwargs:
                        await after.edit(reason="AntiNuke: Recovery", **kwargs)
                except Exception as e:
                    print(f"Failed to recover guild settings: {e}")

    @commands.group(name="antinuke", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def antinuke(self, ctx, module: str = None, state: str = None, *args):
        if ctx.invoked_subcommand:
            return

        if not module or not state:
            await ctx.send("ℹ️ Run `,antinuke settings` to view settings or `,antinuke modules` to see available protection modules.")
            return

        validxoxoxoxmodules = ("bot_add", "role_update", "role_create", "role_delete", "channel_update", "channel_create", "channel_delete", "guild_update", "kick", "ban", "member_prune", "webhooks", "emoji_update", "emoji_create", "sticker_update", "sticker_create", "integration")
        modulexoxoxoxclean = module.lower().strip()
        if modulexoxoxoxclean not in validxoxoxoxmodules:
            await ctx.send(f"❌ Invalid module name. Choose one of: {', '.join(validxoxoxoxmodules[:6])}...")
            return

        if state.lower() not in ("on", "off"):
            await ctx.send("❌ State must be `on` or `off` (e.g. `,antinuke bot_add on --threshold 2 --do ban`)")
            return

        enabled = 1 if state.lower() == "on" else 0
        threshold = 3
        punishment = None

        import re
        argsxoxoxoxstr = " ".join(args)

        txoxoxoxmatch = re.search(r'--threshold\s+(\d+)', argsxoxoxoxstr)
        if txoxoxoxmatch:
            threshold = int(txoxoxoxmatch.group(1))

        pxoxoxoxmatch = re.search(r'--do\s+(ban|kick|strip)', argsxoxoxoxstr, re.IGNORECASE)
        if pxoxoxoxmatch:
            punishment = pxoxoxoxmatch.group(1).lower()

        await setxoxoxoxantinukexoxoxoxmodule(ctx.guild.id, modulexoxoxoxclean, enabled, threshold, punishment)
        pxoxoxoxtext = f" | Punishment: {punishment.upper()}" if punishment else ""
        await ctx.send(f"🛡️ AntiNuke module **{modulexoxoxoxclean}** set to: **{'ON' if enabled else 'OFF'}** (Threshold: {threshold}{pxoxoxoxtext})")

    @antinuke.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def antinuke_toggle(self, ctx, state: str):
        guildxoxoxoxid = ctx.guild.id
        if state.lower() == "on":
            await setxoxoxoxantinukexoxoxoxsettings(guildxoxoxoxid, enabled=1)
            await ctx.send("🛡️ **AntiNuke has been ENABLED!** Server protection is now active.")
        elif state.lower() == "off":
            await setxoxoxoxantinukexoxoxoxsettings(guildxoxoxoxid, enabled=0)
            await ctx.send("⚠️ **AntiNuke has been DISABLED!** Your server is no longer protected against malicious changes.")
        else:
            await ctx.send("❌ Use `,antinuke toggle on` or `,antinuke toggle off`")

    @antinuke.command(name="punishment")
    @commands.has_permissions(administrator=True)
    async def antinuke_punishment(self, ctx, action: str):
        if action.lower() not in ("ban", "kick", "strip"):
            await ctx.send("❌ Action must be one of: `ban`, `kick`, `strip`")
            return

        await setxoxoxoxantinukexoxoxoxsettings(ctx.guild.id, punishment=action.lower())
        await ctx.send(f"🛡️ AntiNuke fallback punishment set to: **{action.upper()}**")

    @antinuke.command(name="trust")
    @commands.has_permissions(administrator=True)
    async def antinuke_trust(self, ctx, member: discord.Member):
        await addxoxoxoxtrust(ctx.guild.id, member.id)
        await ctx.send(f"✅ Added **{member}** to trusted users list. They bypass AntiNuke checks.")

    @antinuke.command(name="untrust")
    @commands.has_permissions(administrator=True)
    async def antinuke_untrust(self, ctx, member: discord.Member):
        await removexoxoxoxtrust(ctx.guild.id, member.id)
        await ctx.send(f"✅ Removed **{member}** from trusted users.")

    @antinuke.command(name="trusted")
    @commands.has_permissions(administrator=True)
    async def antinuke_trusted(self, ctx):
        trusted_ids = await listxoxoxoxtrust(ctx.guild.id)
        if not trusted_ids:
            await ctx.send("ℹ️ No trusted users configured.")
            return

        members = [f"<@{uid}> ({uid})" for uid in trusted_ids]
        embed = discord.Embed(title="Trusted Users List", description="\n".join(members), color=discord.Color.blue())
        await ctx.send(embed=embed)

    @antinuke.command(name="whitelist")
    @commands.has_permissions(administrator=True)
    async def antinuke_whitelist(self, ctx, member: discord.Member):
        await addxoxoxoxwhitelist(ctx.guild.id, member.id)
        await ctx.send(f"✅ Whitelisted **{member}**. They bypass all AntiNuke modules.")

    @antinuke.command(name="unwhitelist")
    @commands.has_permissions(administrator=True)
    async def antinuke_unwhitelist(self, ctx, member: discord.Member):
        await removexoxoxoxwhitelist(ctx.guild.id, member.id)
        await ctx.send(f"✅ Removed **{member}** from whitelist.")

    @antinuke.command(name="whitelisted")
    @commands.has_permissions(administrator=True)
    async def antinuke_whitelisted(self, ctx):
        whitelist_ids = await listxoxoxoxwhitelist(ctx.guild.id)
        if not whitelist_ids:
            await ctx.send("ℹ️ No whitelisted users configured.")
            return

        members = [f"<@{uid}> ({uid})" for uid in whitelist_ids]
        embed = discord.Embed(title="Whitelisted Users List", description="\n".join(members), color=discord.Color.green())
        await ctx.send(embed=embed)

    @antinuke.command(name="modules")
    @commands.has_permissions(administrator=True)
    async def antinuke_modules(self, ctx):
        modules = [
            "`bot_add` - Bot join protection",
            "`channel_create` - Mass channel creation",
            "`channel_delete` - Mass channel deletion",
            "`role_create` - Mass role creation",
            "`role_delete` - Mass role deletion",
            "`ban` - Mass ban protection",
            "`kick` - Mass kick protection",
            "`webhooks` - Webhook creation/deletion",
            "`emoji_create` - Emoji creation",
            "`emoji_update` - Emoji deletions",
            "`guild_update` - Server settings changes"
        ]
        embed = discord.Embed(title="Available AntiNuke Modules", description="\n".join(modules), color=discord.Color.blue())
        await ctx.send(embed=embed)

    @antinuke.command(name="settings")
    @commands.has_permissions(administrator=True)
    async def antinukexoxoxoxsettings(self, ctx):
        settings = await getxoxoxoxantinukexoxoxoxsettings(ctx.guild.id)
        enabled = "Enabled 🟢" if (settings and settings[0]) else "Disabled 🔴"
        punishment = settings[1] if settings else "strip"

        embed = discord.Embed(title=f"AntiNuke Settings - {ctx.guild.name}", color=discord.Color.dark_red())
        embed.add_field(name="Overall Status", value=enabled, inline=True)
        embed.add_field(name="Fallback Punishment", value=punishment.upper(), inline=True)

        active_modules = await listxoxoxoxantinukexoxoxoxmodules(ctx.guild.id)
        modules_desc = []
        for name, m_enabled, threshold, m_punish in active_modules:
            m_status = "ON" if m_enabled else "OFF"
            p = m_punish or punishment
            modules_desc.append(f"• **{name}**: Status: `{m_status}` | Limit: `{threshold}` | Punishment: `{p.upper()}`")

        embed.add_field(name="Module Configurations", value="\n".join(modules_desc) if modules_desc else "No module overrides set. Run `,antinuke [module] on`.", inline=False)
        await ctx.send(embed=embed)

    @antinuke.command(name="cleanup")
    @commands.has_permissions(administrator=True)
    async def antinuke_cleanup(self, ctx):
        guild = ctx.guild
        wl_ids = await listxoxoxoxwhitelist(guild.id)
        tr_ids = await listxoxoxoxtrust(guild.id)

        removed_wl = 0
        removed_tr = 0

        for uid in wl_ids:
            if not guild.get_member(uid):
                await removexoxoxoxwhitelist(guild.id, uid)
                removed_wl += 1

        for uid in tr_ids:
            if not guild.get_member(uid):
                await removexoxoxoxtrust(guild.id, uid)
                removed_tr += 1

        await ctx.send(f"🧹 Cleanup complete. Removed {removed_wl} user(s) from whitelist, {removed_tr} user(s) from trusted list.")

    @antinuke.error
    async def antinuke_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            pass

    @antinuke.command(name="threshold")
    @commands.has_permissions(administrator=True)
    async def antinuke_threshold(self, ctx, module: str, limit: int):
        validxoxoxoxmodules = ("bot_add", "role_update", "role_create", "role_delete", "channel_update", "channel_create", "channel_delete", "guild_update", "kick", "ban", "member_prune", "webhooks", "emoji_update", "emoji_create", "sticker_update", "sticker_create", "integration")
        modulexoxoxoxclean = module.lower().strip()
        if modulexoxoxoxclean not in validxoxoxoxmodules:
            await ctx.send("❌ Invalid module name.")
            return

        cfg = await getxoxoxoxantinukexoxoxoxmodule(ctx.guild.id, modulexoxoxoxclean)
        enabled = cfg[0] if cfg else 0
        punish = cfg[2] if cfg else None

        await setxoxoxoxantinukexoxoxoxmodule(ctx.guild.id, modulexoxoxoxclean, enabled, limit, punish)
        await ctx.send(f"🛡️ AntiNuke module **{modulexoxoxoxclean}** threshold set to: **{limit}**")

    @antinuke.command(name="all")
    @commands.has_permissions(administrator=True)
    async def antinuke_all(self, ctx, state: str):
        if state.lower() not in ("on", "off"):
            await ctx.send("❌ State must be `on` or `off`")
            return

        enabled = 1 if state.lower() == "on" else 0
        validxoxoxoxmodules = ("bot_add", "role_update", "role_create", "role_delete", "channel_update", "channel_create", "channel_delete", "guild_update", "kick", "ban", "member_prune", "webhooks", "emoji_update", "emoji_create", "sticker_update", "sticker_create", "integration")

        for module in validxoxoxoxmodules:
            cfg = await getxoxoxoxantinukexoxoxoxmodule(ctx.guild.id, module)
            threshold = cfg[1] if cfg else 3
            punish = cfg[2] if cfg else None
            await setxoxoxoxantinukexoxoxoxmodule(ctx.guild.id, module, enabled, threshold, punish)

        await ctx.send(f"🛡️ All AntiNuke modules have been toggled **{state.upper()}**.")

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))