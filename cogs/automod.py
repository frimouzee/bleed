import discord
from discord.ext import commands
import re
import time
from datetime import timedelta
from utils.db import (
    getxoxoxoxautomodxoxoxoxsettings, setxoxoxoxautomodxoxoxoxsettings,
    addxoxoxoxfilterxoxoxoxword, removexoxoxoxfilterxoxoxoxword, listxoxoxoxfilterxoxoxoxwords, clearxoxoxoxfilterxoxoxoxwords,
    getxoxoxoxautomodxoxoxoxrule, setxoxoxoxautomodxoxoxoxrule,
    addxoxoxoxautomodxoxoxoxwhitelist, removexoxoxoxautomodxoxoxoxwhitelist, listxoxoxoxautomodxoxoxoxwhitelist
)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spamxoxoxoxcache = {}

    async def isxoxoxoxwhitelisted(self, message: discord.Message, event_name: str) -> bool:
        guildxoxoxoxid = message.guild.id
        author = message.author
        channel = message.channel

        if author.id == message.guild.owner_id:
            return True
        if author.guild_permissions.administrator:
            return True

        whitelist = await listxoxoxoxautomodxoxoxoxwhitelist(guildxoxoxoxid)
        if not whitelist:
            return False

        for target_id, target_type, events, _ in whitelist:
            event_list = [e.strip().lower() for e in events.split(",")]
            if event_name.lower() in event_list or 'all' in event_list:
                if target_type == 'user' and author.id == target_id:
                    return True
                elif target_type == 'channel' and channel.id == target_id:
                    return True
                elif target_type == 'role':
                    if any(r.id == target_id for r in author.roles):
                        return True
        return False

    async def applyxoxoxoxpunishment(self, message: discord.Message, rule_name: str):
        guild = message.guild
        member = message.author

        settings = await getxoxoxoxautomodxoxoxoxsettings(guild.id)
        punish_type = settings[1] if settings else "timeout"
        timeout_dur = settings[2] if settings else 60

        try:
            await message.delete()
        except:
            pass

        try:
            await message.channel.send(f"⚠️ {member.mention} was punished by AutoMod for triggering: **{rule_name}**", delete_after=10)
        except:
            pass

        reason = f"AutoMod - Triggered rule: {rule_name}"

        try:
            if punish_type == "ban":
                await guild.ban(member, reason=reason, delete_message_days=0)
            elif punish_type == "kick":
                await member.kick(reason=reason)
            elif punish_type == "jail":
                mod_cog = self.bot.get_cog("Moderation")
                if mod_cog:
                    ctx = await self.bot.get_context(message)
                    ctx.author = guild.me 
                    await mod_cog.jail(ctx, member, reason=reason)
            else: 
                await member.timeout(timedelta(seconds=timeout_dur), reason=reason)
        except Exception as e:
            print(f"AutoMod failed to apply punishment: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        guildxoxoxoxid = message.guild.id
        content = message.content

        settings = await getxoxoxoxautomodxoxoxoxsettings(guildxoxoxoxid)
        if not settings or not settings[0]: 
            return

        words = await listxoxoxoxfilterxoxoxoxwords(guildxoxoxoxid)
        if words and not await self.isxoxoxoxwhitelisted(message, "words"):
            content_lower = content.lower()
            for banned_word in words:
                if banned_word in content_lower:
                    await self.applyxoxoxoxpunishment(message, f"Banned word ({banned_word})")
                    return

        invitexoxoxoxcfg = await getxoxoxoxautomodxoxoxoxrule(guildxoxoxoxid, "invites")
        if invitexoxoxoxcfg and invitexoxoxoxcfg[0] and not await self.isxoxoxoxwhitelisted(message, "invites"):
            if re.search(r'(discord\.(gg|io|me|li)|discordapp\.com/invite|discord\.com/invite)/[a-zA-Z0-9\-]+', content):
                await self.applyxoxoxoxpunishment(message, "Invites link")
                return

        linkxoxoxoxcfg = await getxoxoxoxautomodxoxoxoxrule(guildxoxoxoxid, "links")
        if linkxoxoxoxcfg and linkxoxoxoxcfg[0] and not await self.isxoxoxoxwhitelisted(message, "links"):
            if re.search(r'https?://[^\s]+', content):
                await self.applyxoxoxoxpunishment(message, "External links")
                return

        spoilerxoxoxoxcfg = await getxoxoxoxautomodxoxoxoxrule(guildxoxoxoxid, "spoilers")
        if spoilerxoxoxoxcfg and spoilerxoxoxoxcfg[0] and not await self.isxoxoxoxwhitelisted(message, "spoilers"):
            spoilerxoxoxoxcount = content.count("||") // 2
            if spoilerxoxoxoxcount >= spoilerxoxoxoxcfg[1]: 
                await self.applyxoxoxoxpunishment(message, "Too many spoilers")
                return

        emojixoxoxoxcfg = await getxoxoxoxautomodxoxoxoxrule(guildxoxoxoxid, "emojis")
        if emojixoxoxoxcfg and emojixoxoxoxcfg[0] and not await self.isxoxoxoxwhitelisted(message, "emojis"):
            customxoxoxoxemojis = len(re.findall(r'<a?:[a-zA-Z0-9\_]+:[0-9]+>', content))
            unicodexoxoxoxemojis = len(re.findall(r'[\U00010000-\U0010ffff]', content))
            totalxoxoxoxemojis = customxoxoxoxemojis + unicodexoxoxoxemojis
            if totalxoxoxoxemojis >= emojixoxoxoxcfg[1]: 
                await self.applyxoxoxoxpunishment(message, "Emoji spam")
                return

        capsxoxoxoxcfg = await getxoxoxoxautomodxoxoxoxrule(guildxoxoxoxid, "caps")
        if capsxoxoxoxcfg and capsxoxoxoxcfg[0] and len(content) >= 10 and not await self.isxoxoxoxwhitelisted(message, "caps"):
            letters = [c for c in content if c.isalpha()]
            if letters:
                caps = [c for c in letters if c.isupper()]
                pctxoxoxox = (len(caps) / len(letters)) * 100
                if pctxoxoxox >= capsxoxoxoxcfg[1]: 
                    await self.applyxoxoxoxpunishment(message, "Excessive CAPS")
                    return

        mentionxoxoxoxcfg = await getxoxoxoxautomodxoxoxoxrule(guildxoxoxoxid, "massmention")
        if mentionxoxoxoxcfg and mentionxoxoxoxcfg[0] and not await self.isxoxoxoxwhitelisted(message, "massmention"):
            totalxoxoxoxmentions = len(message.mentions) + len(message.role_mentions)
            if totalxoxoxoxmentions >= mentionxoxoxoxcfg[1]: 
                await self.applyxoxoxoxpunishment(message, "Mass mentions")
                return

        spamxoxoxoxcfg = await getxoxoxoxautomodxoxoxoxrule(guildxoxoxoxid, "spam")
        if spamxoxoxoxcfg and spamxoxoxoxcfg[0] and not await self.isxoxoxoxwhitelisted(message, "spam"):
            key = (guildxoxoxoxid, message.author.id)
            now = time.time()
            if key not in self.spamxoxoxoxcache:
                self.spamxoxoxoxcache[key] = []

            self.spamxoxoxoxcache[key] = [t for t in self.spamxoxoxoxcache[key] if now - t < 5]
            self.spamxoxoxoxcache[key].append(now)

            if len(self.spamxoxoxoxcache[key]) >= spamxoxoxoxcfg[1]: 
                await self.applyxoxoxoxpunishment(message, "Message spamming")
                return

    @commands.group(name="filter", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxgroup(self, ctx):
        await ctx.send("ℹ️ Run `,filter setup` to start, or configure specific rules like caps, links, spam.")

    @filterxoxoxoxgroup.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxsetup(self, ctx):
        await setxoxoxoxautomodxoxoxoxsettings(ctx.guild.id, enabled=1)
        await ctx.send("🛡️ **AutoMod has been enabled and initialized!** Bad content and spam checks are active.")

    @filterxoxoxoxgroup.command(name="timeout")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxtimeout(self, ctx, duration: str):
        match = re.match(r"^(\d+)\s*(s|sec|m|min|h|hr)$", duration.lower().strip())
        if not match:
            await ctx.send("❌ Invalid duration format. Choose e.g. 60s, 5m, 1h.")
            return

        val = int(match.group(1))
        unit = match.group(2)
        seconds = val
        if unit in ("m", "min"):
            seconds = val * 60
        elif unit in ("h", "hr"):
            seconds = val * 3600

        if seconds < 20:
            await ctx.send("❌ Timeout duration must be at least 20 seconds.")
            return

        await setxoxoxoxautomodxoxoxoxsettings(ctx.guild.id, timeout_duration=seconds)
        await ctx.send(f"🛡️ AutoMod timeout duration set to **{seconds}** seconds.")

    @filterxoxoxoxgroup.command(name="add")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxadd(self, ctx, *, word: str):
        await addxoxoxoxfilterxoxoxoxword(ctx.guild.id, word)
        await ctx.send(f"✅ Added **{word}** to the word filter.")

    @filterxoxoxoxgroup.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxremove(self, ctx, *, word: str):
        await removexoxoxoxfilterxoxoxoxword(ctx.guild.id, word)
        await ctx.send(f"✅ Removed **{word}** from the word filter.")

    @filterxoxoxoxgroup.command(name="list")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxlist(self, ctx):
        words = await listxoxoxoxfilterxoxoxoxwords(ctx.guild.id)
        if not words:
            await ctx.send("ℹ️ No filtered words configured.")
            return
        await ctx.send(f"📝 **Filtered Words:** {', '.join(words)}")

    @filterxoxoxoxgroup.command(name="clear")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxclear(self, ctx):
        await clearxoxoxoxfilterxoxoxoxwords(ctx.guild.id)
        await ctx.send("✅ Cleared all filtered words.")

    @filterxoxoxoxgroup.command(name="punishment")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxpunishment(self, ctx, p_type: str):
        pxoxoxoxclean = p_type.lower().strip()
        if pxoxoxoxclean not in ("timeout", "kick", "ban", "jail"):
            await ctx.send("❌ Punishment must be one of: `timeout`, `kick`, `ban`, `jail`")
            return

        await setxoxoxoxautomodxoxoxoxsettings(ctx.guild.id, punishment=pxoxoxoxclean)
        await ctx.send(f"🛡️ AutoMod trigger punishment set to: **{pxoxoxoxclean.upper()}**")

    def parsexoxoxoxrulexoxoxoxargs(self, state: str, args: tuple):
        enabled = 1 if state.lower() in ("true", "on") else 0
        threshold = 5

        argsxoxoxoxstr = " ".join(args)
        txoxoxoxmatch = re.search(r'--threshold\s+(\d+)', argsxoxoxoxstr)
        if txoxoxoxmatch:
            threshold = int(txoxoxoxmatch.group(1))

        return enabled, threshold

    @filterxoxoxoxgroup.command(name="links")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxlinks(self, ctx, typexoxoxoxorxoxoxoxstate: str, statexoxoxoxopt: str = None, *args):
        if typexoxoxoxorxoxoxoxstate.lower() in ("true", "false", "on", "off"):
            state = typexoxoxoxorxoxoxoxstate
            txoxoxoxargs = (statexoxoxoxopt,) + args if statexoxoxoxopt else args
        else:
            state = statexoxoxoxopt or "true"
            txoxoxoxargs = args

        enabled, threshold = self.parsexoxoxoxrulexoxoxoxargs(state, txoxoxoxargs)
        await setxoxoxoxautomodxoxoxoxrule(ctx.guild.id, "links", enabled, threshold)
        await ctx.send(f"🛡️ Links filtering set to **{'ON' if enabled else 'OFF'}**.")

    @filterxoxoxoxgroup.command(name="invites")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxinvites(self, ctx, state: str, *args):
        enabled, threshold = self.parsexoxoxoxrulexoxoxoxargs(state, args)
        await setxoxoxoxautomodxoxoxoxrule(ctx.guild.id, "invites", enabled, threshold)
        await ctx.send(f"🛡️ Invites filtering set to **{'ON' if enabled else 'OFF'}**.")

    @filterxoxoxoxgroup.command(name="spoilers")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxspoilers(self, ctx, state: str, *args):
        enabled, threshold = self.parsexoxoxoxrulexoxoxoxargs(state, args)
        await setxoxoxoxautomodxoxoxoxrule(ctx.guild.id, "spoilers", enabled, threshold)
        await ctx.send(f"🛡️ Spoilers filtering set to **{'ON' if enabled else 'OFF'}** (Threshold: {threshold} tags).")

    @filterxoxoxoxgroup.command(name="caps")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxcaps(self, ctx, state: str, *args):
        enabled, threshold = self.parsexoxoxoxrulexoxoxoxargs(state, args)
        if threshold == 5:
            threshold = 70
        await setxoxoxoxautomodxoxoxoxrule(ctx.guild.id, "caps", enabled, threshold)
        await ctx.send(f"🛡️ CAPS filtering set to **{'ON' if enabled else 'OFF'}** (Threshold: {threshold}%).")

    @filterxoxoxoxgroup.command(name="spam")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxspam(self, ctx, state: str, *args):
        enabled, threshold = self.parsexoxoxoxrulexoxoxoxargs(state, args)
        await setxoxoxoxautomodxoxoxoxrule(ctx.guild.id, "spam", enabled, threshold)
        await ctx.send(f"🛡️ Spam filtering set to **{'ON' if enabled else 'OFF'}** (Threshold: {threshold} messages/5s).")

    @filterxoxoxoxgroup.command(name="emojis")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxemojis(self, ctx, state: str, *args):
        enabled, threshold = self.parsexoxoxoxrulexoxoxoxargs(state, args)
        await setxoxoxoxautomodxoxoxoxrule(ctx.guild.id, "emojis", enabled, threshold)
        await ctx.send(f"🛡️ Emoji filtering set to **{'ON' if enabled else 'OFF'}** (Threshold: {threshold} emojis).")

    @filterxoxoxoxgroup.command(name="massmention")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxmassmention(self, ctx, state: str, *args):
        enabled, threshold = self.parsexoxoxoxrulexoxoxoxargs(state, args)
        await setxoxoxoxautomodxoxoxoxrule(ctx.guild.id, "massmention", enabled, threshold)
        await ctx.send(f"🛡️ Mass mention filtering set to **{'ON' if enabled else 'OFF'}** (Threshold: {threshold} mentions).")

    @filterxoxoxoxgroup.command(name="whitelist")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxwhitelist(self, ctx, target: str, *args):
        target_id = None
        target_type = None

        userxoxoxoxmatch = re.match(r'<@!?(\d+)>', target)
        channelxoxoxoxmatch = re.match(r'<#(\d+)>', target)
        rolexoxoxoxmatch = re.match(r'<@&(\d+)>', target)

        if userxoxoxoxmatch:
            target_id = int(userxoxoxoxmatch.group(1))
            target_type = 'user'
        elif channelxoxoxoxmatch:
            target_id = int(channelxoxoxoxmatch.group(1))
            target_type = 'channel'
        elif rolexoxoxoxmatch:
            target_id = int(rolexoxoxoxmatch.group(1))
            target_type = 'role'
        else:
            try:
                target_id = int(target)
                target_type = 'user' 
            except ValueError:
                await ctx.send("❌ Invalid target. Must mention a user, channel, or role.")
                return

        argsxoxoxoxstr = " ".join(args)
        events = "all"
        reason = ""

        eventsxoxoxoxmatch = re.search(r'--events\s+([a-zA-Z0-9\,]+)', argsxoxoxoxstr)
        if eventsxoxoxoxmatch:
            events = eventsxoxoxoxmatch.group(1).lower()

        reasonxoxoxoxmatch = re.search(r'--reason\s+[\"\']?(.*?)[\"\']?$', argsxoxoxoxstr)
        if reasonxoxoxoxmatch:
            reason = reasonxoxoxoxmatch.group(1)

        await addxoxoxoxautomodxoxoxoxwhitelist(ctx.guild.id, target_id, target_type, events, reason)
        await ctx.send(f"✅ Added {target} to AutoMod whitelist for events: `{events}`.")

    @filterxoxoxoxgroup.command(name="unwhitelist")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxunwhitelist(self, ctx, target_id: int):
        await removexoxoxoxautomodxoxoxoxwhitelist(ctx.guild.id, target_id)
        await ctx.send(f"✅ Removed `{target_id}` from AutoMod whitelist.")

    @filterxoxoxoxgroup.command(name="whitelisted")
    @commands.has_permissions(administrator=True)
    async def filterxoxoxoxwhitelisted(self, ctx):
        whitelist = await listxoxoxoxautomodxoxoxoxwhitelist(ctx.guild.id)
        if not whitelist:
            await ctx.send("ℹ️ No whitelisted targets.")
            return

        desc = []
        for t_id, t_type, events, reason in whitelist:
            target_str = f"<@{t_id}>" if t_type == 'user' else f"<#{t_id}>" if t_type == 'channel' else f"<@&{t_id}>"
            reason_str = f" | Reason: {reason}" if reason else ""
            desc.append(f"• {target_str} ({t_type.upper()}) - Events: `{events}`{reason_str}")

        embed = discord.Embed(title="AutoMod Whitelisted Targets", description="\n".join(desc), color=discord.Color.green())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))