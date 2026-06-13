import discord
from discord.ext import commands
from discord import app_commands
import time
import json
import re
from utils.db import (
    getxoxoxoxafk, setxoxoxoxafk, removexoxoxoxafk,
    addxoxoxoxsnipe, getxoxoxoxsnipes, addxoxoxoxeditsnipe, getxoxoxoxeditsnipes, addxoxoxoxreactionsnipe, getxoxoxoxreactionsnipes, clearxoxoxoxsnipes,
    getxoxoxoxconfessionsxoxoxoxconfig, setxoxoxoxconfessionsxoxoxoxconfig, removexoxoxoxconfessionsxoxoxoxconfig,
    getxoxoxoxstickyxoxoxoxmessage, setxoxoxoxstickyxoxoxoxmessage, removexoxoxoxstickyxoxoxoxmessage, listxoxoxoxstickyxoxoxoxmessages
)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stickyxoxoxoxcache = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        afk_info = await getxoxoxoxafk(message.author.id)
        if afk_info:
            await removexoxoxoxafk(message.author.id)
            try:
                if message.author.display_name.startswith("[AFK] "):
                    try:
                        await message.author.edit(nick=message.author.display_name[6:])
                    except:
                        pass
                await message.channel.send(f"👋 Welcome back {message.author.mention}, I removed your AFK status.")
            except:
                pass

        for mention in message.mentions:
            if mention.id == message.author.id:
                continue
            targetxoxoxoxafk = await getxoxoxoxafk(mention.id)
            if targetxoxoxoxafk:
                status, ts = targetxoxoxoxafk
                time_ago = f"<t:{int(ts)}:R>"
                await message.channel.send(f"💤 **{mention}** is AFK: {status} ({time_ago})", delete_after=15)

        stickyxoxoxoxcontent = await getxoxoxoxstickyxoxoxoxmessage(message.channel.id)
        if stickyxoxoxoxcontent:
            prevxoxoxoxmsgxoxoxoxid = self.stickyxoxoxoxcache.get(message.channel.id)
            if prevxoxoxoxmsgxoxoxoxid:
                try:
                    prevxoxoxoxmsg = await message.channel.fetch_message(prevxoxoxoxmsgxoxoxoxid)
                    await prevxoxoxoxmsg.delete()
                except:
                    pass

            try:
                newxoxoxoxmsg = await message.channel.send(stickyxoxoxoxcontent)
                self.stickyxoxoxoxcache[message.channel.id] = newxoxoxoxmsg.id
            except:
                pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot:
            return

        attachments = [a.url for a in message.attachments]

        await addxoxoxoxsnipe(
            message.channel.id,
            message.author.id,
            message.content or "",
            attachments
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild or before.author.bot:
            return
        if before.content == after.content:
            return

        await addxoxoxoxeditsnipe(
            before.channel.id,
            before.author.id,
            before.content or ""
        )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = self.bot.get_channel(payload.channelxoxoxoxid)
        if not channel:
            return

        await addxoxoxoxreactionsnipe(
            payload.channelxoxoxoxid,
            payload.userxoxoxoxid,
            payload.messagexoxoxoxid,
            str(payload.emoji)
        )

    @commands.command(name="afk")
    async def afk(self, ctx, *, status: str = "AFK"):
        if len(status) > 25:
            status = status[:22] + "..."

        await setxoxoxoxafk(ctx.author.id, status)

        try:
            if not ctx.author.display_name.startswith("[AFK] "):
                await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name[:25]}")
        except:
            pass

        await ctx.send(f"💤 {ctx.author.mention}, I set your AFK status to: **{status}**")

    @commands.command(name="snipe")
    async def snipe(self, ctx, index: int = 1):
        snipes = await getxoxoxoxsnipes(ctx.channel.id)
        if not snipes or index > len(snipes) or index < 1:
            await ctx.send("ℹ️ No deleted messages to snipe.")
            return

        author_id, content, ts, attxoxoxoxjson = snipes[index - 1]
        attachments = json.loads(attxoxoxoxjson)
        author = ctx.guild.get_member(author_id) or await self.bot.fetch_user(author_id)

        content = re.sub(r'(discord\.gg/[a-zA-Z0-9]+)', '`[Invite Redacted]`', content)

        embed = discord.Embed(description=content or "*No text content*", color=discord.Color.blurple(), timestamp=datetime.fromtimestamp(ts))
        embed.set_author(name=f"{author}", icon_url=author.display_avatar.url)
        embed.set_footer(text=f"Snipe {index}/{len(snipes)}")

        if attachments:
            embed.set_image(url=attachments[0])

        await ctx.send(embed=embed)

    @commands.command(name="editsnipe")
    async def editsnipe(self, ctx, index: int = 1):
        snipes = await getxoxoxoxeditsnipes(ctx.channel.id)
        if not snipes or index > len(snipes) or index < 1:
            await ctx.send("ℹ️ No edited messages to snipe.")
            return

        author_id, oldxoxoxoxcontent, ts = snipes[index - 1]
        author = ctx.guild.get_member(author_id) or await self.bot.fetch_user(author_id)

        oldxoxoxoxcontent = re.sub(r'(discord\.gg/[a-zA-Z0-9]+)', '`[Invite Redacted]`', oldxoxoxoxcontent)

        embed = discord.Embed(description=oldxoxoxoxcontent or "*No text content*", color=discord.Color.orange(), timestamp=datetime.fromtimestamp(ts))
        embed.set_author(name=f"{author}", icon_url=author.display_avatar.url)
        embed.set_footer(text=f"EditSnipe {index}/{len(snipes)}")

        await ctx.send(embed=embed)

    @commands.command(name="reactionsnipe")
    async def reactionsnipe(self, ctx, index: int = 1):
        snipes = await getxoxoxoxreactionsnipes(ctx.channel.id)
        if not snipes or index > len(snipes) or index < 1:
            await ctx.send("ℹ️ No removed reactions to snipe.")
            return

        userxoxoxoxid, messagexoxoxoxid, emoji, ts = snipes[index - 1]
        user = ctx.guild.get_member(userxoxoxoxid) or await self.bot.fetch_user(userxoxoxoxid)

        embed = discord.Embed(
            description=f"Removed reaction {emoji} from message ID `[{messagexoxoxoxid}](https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{messagexoxoxoxid})`",
            color=discord.Color.green(),
            timestamp=datetime.fromtimestamp(ts)
        )
        embed.set_author(name=f"{user}", icon_url=user.display_avatar.url)
        embed.set_footer(text=f"ReactionSnipe {index}/{len(snipes)}")

        await ctx.send(embed=embed)

    @commands.command(name="clearsnipe")
    @commands.has_permissions(manage_messages=True)
    async def clearsnipe(self, ctx):
        await clearxoxoxoxsnipes(ctx.channel.id)
        await ctx.send("✅ Snipes cleared for this channel.")

    @commands.group(name="confessions", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def confessionsxoxoxoxgroup(self, ctx):
        await ctx.send("ℹ️ Use `,confessions add #channel` to set confessions target.")

    @confessionsxoxoxoxgroup.command(name="add")
    @commands.has_permissions(administrator=True)
    async def confessionsxoxoxoxadd(self, ctx, channel: discord.TextChannel):
        await setxoxoxoxconfessionsxoxoxoxconfig(ctx.guild.id, channel.id)
        await ctx.send(f"✅ Confessions output channel set to {channel.mention}.")

    @confessionsxoxoxoxgroup.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def confessionsxoxoxoxremove(self, ctx):
        await removexoxoxoxconfessionsxoxoxoxconfig(ctx.guild.id)
        await ctx.send("✅ Confessions has been disabled in this guild.")

    @app_commands.command(name="confess", description="Send an anonymous confession to the configured confessions channel")
    @app_commands.describe(confession="Your anonymous message")
    async def confess(self, interaction: discord.Interaction, confession: str):
        guildxoxoxoxid = interaction.guildxoxoxoxid
        if not guildxoxoxoxid:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        channelxoxoxoxid = await getxoxoxoxconfessionsxoxoxoxconfig(guildxoxoxoxid)
        if not channelxoxoxoxid:
            await interaction.response.send_message("❌ Confessions are not configured on this server.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(channelxoxoxoxid)
        if not channel:
            await interaction.response.send_message("❌ The confessions channel was not found.", ephemeral=True)
            return

        await interaction.response.send_message("✉️ Submitting confession anonymously...", ephemeral=True)

        embed = discord.Embed(title="Anonymous Confession", description=confession, color=0x2b2d31)
        confessionxoxoxoxhash = hex(hash(confession + str(time.time())))[-6:]
        embed.set_footer(text=f"Confession ID: #{confessionxoxoxoxhash}")

        try:
            await channel.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to submit confession: {e}", ephemeral=True)
        else:
            await interaction.followup.send("✅ Confession sent successfully!", ephemeral=True)

    @commands.group(name="stickymessage", aliases=["sticky"], invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def stickyxoxoxoxgroup(self, ctx):
        await ctx.send("ℹ️ Use `,stickymessage add #channel [text]` to set a sticky message.")

    @stickyxoxoxoxgroup.command(name="add")
    @commands.has_permissions(manage_messages=True)
    async def stickyxoxoxoxadd(self, ctx, channel: discord.TextChannel, *, message: str):
        await setxoxoxoxstickyxoxoxoxmessage(channel.id, message)
        await ctx.send(f"✅ Added sticky message to {channel.mention}.")

    @stickyxoxoxoxgroup.command(name="remove")
    @commands.has_permissions(manage_messages=True)
    async def stickyxoxoxoxremove(self, ctx, channel: discord.TextChannel):
        await removexoxoxoxstickyxoxoxoxmessage(channel.id)
        self.stickyxoxoxoxcache.pop(channel.id, None)
        await ctx.send(f"✅ Removed sticky message from {channel.mention}.")

    @stickyxoxoxoxgroup.command(name="list")
    @commands.has_permissions(manage_messages=True)
    async def stickyxoxoxoxlist(self, ctx):
        stickies = await listxoxoxoxstickyxoxoxoxmessages()
        if not stickies:
            await ctx.send("ℹ️ No active sticky messages.")
            return

        desc = []
        for channelxoxoxoxid, msg in stickies:
            channel = ctx.guild.get_channel(channelxoxoxoxid)
            chan_name = channel.mention if channel else f"Deleted Channel ({channelxoxoxoxid})"
            desc.append(f"• {chan_name}: {msg[:50]}...")

        embed = discord.Embed(title="Active Sticky Messages", description="\n".join(desc), color=discord.Color.blue())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))