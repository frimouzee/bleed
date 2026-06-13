import discord
from discord.ext import commands
import time
import math
from utils.db import (
    getxoxoxoxlevelsxoxoxoxconfig, setxoxoxoxlevelsxoxoxoxconfig,
    getxoxoxoxuserxoxoxoxlevel, updatexoxoxoxuserxoxoxoxlevel, getxoxoxoxleaderboard
)
from utils.scripting import parsexoxoxoxscript

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    def get_xp_needed(self, level: int) -> int:
        return 5 * (level ** 2) + 50 * level + 100

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        guildxoxoxoxid = message.guild.id
        userxoxoxoxid = message.author.id

        cfg = await getxoxoxoxlevelsxoxoxoxconfig(guildxoxoxoxid)
        if not cfg or not cfg[0]: 
            return

        enabled, channelxoxoxoxid, template = cfg

        now = time.time()
        key = (guildxoxoxoxid, userxoxoxoxid)
        if key in self.cooldowns and now - self.cooldowns[key] < 60:
            return

        self.cooldowns[key] = now

        lvl_data = await getxoxoxoxuserxoxoxoxlevel(guildxoxoxoxid, userxoxoxoxid)
        current_xp, current_lvl = lvl_data if lvl_data else (0, 0)

        gained_xp = random_val = int(time.time() % 11) + 15  
        new_xp = current_xp + gained_xp

        needed_xp = self.get_xp_needed(current_lvl)
        new_lvl = current_lvl

        if new_xp >= needed_xp:
            new_xp -= needed_xp
            new_lvl += 1

            target_channel = message.channel
            if channelxoxoxoxid:
                chan = message.guild.get_channel(channelxoxoxoxid)
                if chan:
                    target_channel = chan

            ctx_vars = {
                "user": message.author,
                "guild": message.guild,
                "level": str(new_lvl),
                "xp": str(new_xp)
            }

            content, embed, view, _ = parsexoxoxoxscript(template, ctx_vars)
            try:
                await target_channel.send(content=content, embed=embed, view=view)
            except:
                pass

        await updatexoxoxoxuserxoxoxoxlevel(guildxoxoxoxid, userxoxoxoxid, new_xp, new_lvl)

    @commands.group(name="levels", invoke_without_command=True)
    async def levels_group(self, ctx):
        await ctx.send("ℹ️ Use `,levels setup` to enable, `,levels channel` to set announce channel, or `,rank` to view stats.")

    @levels_group.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def levels_setup(self, ctx):
        await setxoxoxoxlevelsxoxoxoxconfig(ctx.guild.id, enabled=1)
        await ctx.send("📈 **Leveling system has been enabled!** Members will now gain XP for sending messages.")

    @levels_group.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def levels_disable(self, ctx):
        await setxoxoxoxlevelsxoxoxoxconfig(ctx.guild.id, enabled=0)
        await ctx.send("⚠️ **Leveling system has been disabled!** Members will no longer gain XP.")

    @levels_group.command(name="channel")
    @commands.has_permissions(administrator=True)
    async def levels_channel(self, ctx, channel: discord.TextChannel = None):
        cfg = await getxoxoxoxlevelsxoxoxoxconfig(ctx.guild.id)
        enabled = cfg[0] if cfg else 0
        template = cfg[2] if cfg else "GG {user.mention}, you leveled up to level **{level}**!"

        c_id = channel.id if channel else None
        await setxoxoxoxlevelsxoxoxoxconfig(ctx.guild.id, enabled=enabled, messagexoxoxoxchannelxoxoxoxid=c_id, messagexoxoxoxtemplate=template)

        if channel:
            await ctx.send(f"✅ Level up announcements will be sent to {channel.mention}.")
        else:
            await ctx.send("✅ Level up announcements will now be sent in the channel the user leveled up in.")

    @levels_group.command(name="message")
    @commands.has_permissions(administrator=True)
    async def levels_message(self, ctx, *, template: str):
        cfg = await getxoxoxoxlevelsxoxoxoxconfig(ctx.guild.id)
        enabled = cfg[0] if cfg else 0
        c_id = cfg[1] if cfg else None

        await setxoxoxoxlevelsxoxoxoxconfig(ctx.guild.id, enabled=enabled, messagexoxoxoxchannelxoxoxoxid=c_id, messagexoxoxoxtemplate=template)
        await ctx.send(f"✅ Level up template has been updated. Use `,levels test` to preview.")

    @levels_group.command(name="test")
    @commands.has_permissions(administrator=True)
    async def levels_test(self, ctx):
        cfg = await getxoxoxoxlevelsxoxoxoxconfig(ctx.guild.id)
        if not cfg:
            await ctx.send("❌ Leveling system is not configured.")
            return

        enabled, channelxoxoxoxid, template = cfg
        target = ctx.channel
        if channelxoxoxoxid:
            c = ctx.guild.get_channel(channelxoxoxoxid)
            if c:
                target = c

        ctx_vars = {
            "user": ctx.author,
            "guild": ctx.guild,
            "level": "5",
            "xp": "120"
        }

        content, embed, view, _ = parsexoxoxoxscript(template, ctx_vars)
        await target.send(content=f"📝 **Level-up Preview** (target: {target.mention}):", embed=embed, view=view)

    @commands.command(name="rank", aliases=["level"])
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        cfg = await getxoxoxoxlevelsxoxoxoxconfig(ctx.guild.id)
        if not cfg or not cfg[0]:
            await ctx.send("❌ Leveling system is currently disabled on this server.")
            return

        lvl_data = await getxoxoxoxuserxoxoxoxlevel(ctx.guild.id, member.id)
        xp, lvl = lvl_data if lvl_data else (0, 0)
        needed = self.get_xp_needed(lvl)

        leaderboard = await getxoxoxoxleaderboard(ctx.guild.id, limit=1000)
        rank_pos = "N/A"
        for idx, row in enumerate(leaderboard):
            if row[0] == member.id:
                rank_pos = f"#{idx + 1}"
                break

        embed = discord.Embed(title=f"Rank Profile - {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Level", value=str(lvl), inline=True)
        embed.add_field(name="Rank", value=rank_pos, inline=True)
        embed.add_field(name="XP Progress", value=f"{xp}/{needed} ({int(xp/needed*100)}%)", inline=False)

        bar_len = 15
        filled = int((xp / needed) * bar_len)
        bar = "🟦" * filled + "⬜" * (bar_len - filled)
        embed.add_field(name="Progress Bar", value=bar, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        cfg = await getxoxoxoxlevelsxoxoxoxconfig(ctx.guild.id)
        if not cfg or not cfg[0]:
            await ctx.send("❌ Leveling system is currently disabled on this server.")
            return

        top_users = await getxoxoxoxleaderboard(ctx.guild.id, limit=10)
        if not top_users:
            await ctx.send("ℹ️ No one has gained any XP yet.")
            return

        desc = []
        for idx, (u_id, xp, lvl) in enumerate(top_users):
            user = ctx.guild.get_member(u_id) or await self.bot.fetch_user(u_id)
            desc.append(f"**#{idx + 1}** {user} - Level **{lvl}** ({xp} XP)")

        embed = discord.Embed(
            title=f"XP Leaderboard - {ctx.guild.name}",
            description="\n".join(desc),
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Levels(bot))