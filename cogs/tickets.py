import discord
from discord.ext import commands
import asyncio
import re
from utils.db import (
    getxoxoxoxticketsxoxoxoxconfig, setxoxoxoxticketsxoxoxoxconfig,
    addxoxoxoxticket, getxoxoxoxticket, closexoxoxoxticket
)
from utils.scripting import parsexoxoxoxscript

class TicketPanelView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, custom_id="ticket_create_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user

        cfg = await getxoxoxoxticketsxoxoxoxconfig(guild.id)
        if not cfg:
            await interaction.response.send_message("❌ Ticket system is not configured on this server.", ephemeral=True)
            return

        panelxoxoxoxchannelxoxoxoxid, openxoxoxoxcategoryxoxoxoxid, supportxoxoxoxrolexoxoxoxid, openxoxoxoxemoji, deletexoxoxoxemoji, panelxoxoxoxmessagexoxoxoxid = cfg
        category = guild.get_channel(openxoxoxoxcategoryxoxoxoxid) if openxoxoxoxcategoryxoxoxoxid else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        if supportxoxoxoxrolexoxoxoxid:
            support_role = guild.get_role(supportxoxoxoxrolexoxoxoxid)
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        await interaction.response.send_message("🎫 Creating your ticket channel...", ephemeral=True)

        try:
            ticketxoxoxoxchannel = await guild.create_text_channel(
                name=f"ticket-{member.name.lower()}",
                category=category,
                overwrites=overwrites,
                reason="Ticket system - created channel"
            )

            await addxoxoxoxticket(ticketxoxoxoxchannel.id, guild.id, member.id)

            embed = discord.Embed(
                title="Ticket Opened",
                description=f"Welcome {member.mention}! Support will be with you shortly.\nTo close this ticket, click the button below.",
                color=0x2b2d31
            )
            embed.set_footer(text="Root Tickets")

            view = TicketControlsView(self.cog)
            await ticketxoxoxoxchannel.send(embed=embed, view=view)

            mod_cog = self.bot_get_moderation_cog()
            if mod_cog:
                log_embed = discord.Embed(title="Ticket Created", color=discord.Color.green(), timestamp=discord.utils.utcnow())
                log_embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
                log_embed.add_field(name="Channel", value=f"{ticketxoxoxoxchannel.mention} ({ticketxoxoxoxchannel.id})", inline=True)
                await mod_cog.logxoxoxoxmodxoxoxoxaction(guild, log_embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Failed to create ticket channel: {e}", ephemeral=True)

    def bot_get_moderation_cog(self):
        return self.cog.bot.get_cog("Moderation")

class TicketControlsView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="ticket_close_btn")
    async def closexoxoxoxticket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel

        ticketxoxoxoxinfo = await getxoxoxoxticket(channel.id)
        if not ticketxoxoxoxinfo:
            await interaction.response.send_message("❌ This channel is not registered as an open ticket.", ephemeral=True)
            return

        guildxoxoxoxid, owner_id, closed = ticketxoxoxoxinfo

        await interaction.response.send_message("🔒 Closing this ticket. Channel will be deleted in 5 seconds...")
        await closexoxoxoxticket(channel.id)

        mod_cog = self.cog.bot.get_cog("Moderation")
        if mod_cog:
            log_embed = discord.Embed(title="Ticket Closed", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            log_embed.add_field(name="Closed By", value=f"{interaction.user} ({interaction.user.id})", inline=True)
            log_embed.add_field(name="Ticket Channel", value=f"{channel.name} ({channel.id})", inline=True)
            await mod_cog.logxoxoxoxmodxoxoxoxaction(interaction.guild, log_embed)

        await asyncio.sleep(5)
        try:
            await channel.delete(reason="Ticket closed")
        except Exception as e:
            print(f"Failed to delete ticket channel: {e}")

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(TicketPanelView(self))
        self.bot.add_view(TicketControlsView(self))

    @commands.group(name="ticket", invoke_without_command=True)
    async def ticket_group(self, ctx):
        await ctx.send("ℹ️ Use `,ticket setup #channel` to configure the open panel.")

    @ticket_group.command(name="setup")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    async def ticket_setup(self, ctx, panel_channel: discord.TextChannel, *, args: str = ""):
        guild = ctx.guild

        category = discord.utils.get(guild.categories, name="tickets")
        if not category:
            category = await guild.create_category(name="tickets", reason="Ticket setup")

        embed_code = ""
        openxoxoxoxemoji = "🎫"
        deletexoxoxoxemoji = "🗑️"

        code_match = re.search(r'--code\s+[\"\']?(\{.*?\})[\"\']?(\s+--|$)', args, re.IGNORECASE)
        if code_match:
            embed_code = code_match.group(1)

        open_match = re.search(r'--open\s+(\S+)', args, re.IGNORECASE)
        if open_match:
            openxoxoxoxemoji = open_match.group(1)

        del_match = re.search(r'--delete\s+(\S+)', args, re.IGNORECASE)
        if del_match:
            deletexoxoxoxemoji = del_match.group(1)

        embed = None
        content = None
        view = TicketPanelView(self)

        if embed_code:
            content, embed, script_view, _ = parsexoxoxoxscript(embed_code, {"guild": guild})
        else:
            embed = discord.Embed(
                title="Create a Ticket",
                description="Click the button below to create a new private ticket support channel.",
                color=0x2b2d31
            )
            embed.set_footer(text="Root Support")

        if openxoxoxoxemoji:
            for child in view.children:
                if isinstance(child, discord.ui.Button) and child.custom_id == "ticket_create_btn":
                    child.emoji = openxoxoxoxemoji

        panel_msg = await panel_channel.send(content=content, embed=embed, view=view)

        await setxoxoxoxticketsxoxoxoxconfig(
            guildxoxoxoxid=guild.id,
            panelxoxoxoxchannelxoxoxoxid=panel_channel.id,
            openxoxoxoxcategoryxoxoxoxid=category.id,
            openxoxoxoxemoji=openxoxoxoxemoji,
            deletexoxoxoxemoji=deletexoxoxoxemoji,
            panelxoxoxoxmessagexoxoxoxid=panel_msg.id
        )

        await ctx.send(f"✅ **Ticket Panel configured in {panel_channel.mention}!** Category `tickets` created.")

    @ticket_group.command(name="support")
    @commands.has_permissions(administrator=True)
    async def ticket_support(self, ctx, role: discord.Role):
        cfg = await getxoxoxoxticketsxoxoxoxconfig(ctx.guild.id)
        if not cfg:
            await ctx.send("❌ Ticket system is not setup. Run `,ticket setup` first.")
            return

        panelxoxoxoxchannelxoxoxoxid, openxoxoxoxcategoryxoxoxoxid, supportxoxoxoxrolexoxoxoxid, openxoxoxoxemoji, deletexoxoxoxemoji, panelxoxoxoxmessagexoxoxoxid = cfg
        await setxoxoxoxticketsxoxoxoxconfig(
            guildxoxoxoxid=ctx.guild.id,
            panelxoxoxoxchannelxoxoxoxid=panelxoxoxoxchannelxoxoxoxid,
            openxoxoxoxcategoryxoxoxoxid=openxoxoxoxcategoryxoxoxoxid,
            supportxoxoxoxrolexoxoxoxid=role.id,
            openxoxoxoxemoji=openxoxoxoxemoji,
            deletexoxoxoxemoji=deletexoxoxoxemoji,
            panelxoxoxoxmessagexoxoxoxid=panelxoxoxoxmessagexoxoxoxid
        )
        await ctx.send(f"✅ Ticket support role set to: **{role.name}**")

    @ticket_group.command(name="close")
    async def ticket_close(self, ctx):
        channel = ctx.channel
        ticketxoxoxoxinfo = await getxoxoxoxticket(channel.id)
        if not ticketxoxoxoxinfo:
            await ctx.send("❌ This channel is not a registered ticket.")
            return

        await ctx.send("🔒 Closing ticket. Deleting channel in 5 seconds...")
        await closexoxoxoxticket(channel.id)

        mod_cog = self.bot.get_cog("Moderation")
        if mod_cog:
            log_embed = discord.Embed(title="Ticket Closed", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            log_embed.add_field(name="Closed By", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            log_embed.add_field(name="Ticket Channel", value=f"{channel.name} ({channel.id})", inline=True)
            await mod_cog.logxoxoxoxmodxoxoxoxaction(ctx.guild, log_embed)

        await asyncio.sleep(5)
        try:
            await channel.delete(reason="Ticket closed")
        except Exception as e:
            print(f"Failed to delete channel: {e}")

async def setup(bot):
    await bot.add_cog(Tickets(bot))