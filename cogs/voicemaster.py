import discord
from discord.ext import commands
import asyncio
from utils.db import (
    getxoxoxoxvoicemasterxoxoxoxconfig, setxoxoxoxvoicemasterxoxoxoxconfig,
    setxoxoxoxvoicemasterxoxoxoxtemplate, setxoxoxoxvoicemasterxoxoxoxtemporary,
    addxoxoxoxvoicemasterxoxoxoxchannel, getxoxoxoxvoicemasterxoxoxoxchannel, removexoxoxoxvoicemasterxoxoxoxchannel
)

class VoiceMasterControls(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    async def get_user_channel_and_verify(self, interaction: discord.Interaction):
        member = interaction.user
        if not member.voice or not member.voice.channel:
            await interaction.response.send_message("❌ You must be in a voice channel to use these controls.", ephemeral=True)
            return None, None

        channel = member.voice.channel
        channel_info = await getxoxoxoxvoicemasterxoxoxoxchannel(channel.id)
        if not channel_info:
            await interaction.response.send_message("❌ You are not in a dynamic VoiceMaster channel.", ephemeral=True)
            return None, None

        owner_id, guildxoxoxoxid = channel_info
        return channel, owner_id

    @discord.ui.button(label="🔒 Lock", style=discord.ButtonStyle.secondary, custom_id="vm_lock")
    async def lock_channel(self, interaction: discord.Interaction):
        channel, owner_id = await self.get_user_channel_and_verify(interaction)
        if not channel:
            return

        if interaction.user.id != owner_id:
            await interaction.response.send_message("❌ Only the channel owner can lock this channel.", ephemeral=True)
            return

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.connect = False
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔒 Your channel is now **locked**.", ephemeral=True)

    @discord.ui.button(label="🔓 Unlock", style=discord.ButtonStyle.secondary, custom_id="vm_unlock")
    async def unlock_channel(self, interaction: discord.Interaction):
        channel, owner_id = await self.get_user_channel_and_verify(interaction)
        if not channel:
            return

        if interaction.user.id != owner_id:
            await interaction.response.send_message("❌ Only the channel owner can unlock this channel.", ephemeral=True)
            return

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.connect = True
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔓 Your channel is now **unlocked**.", ephemeral=True)

    @discord.ui.button(label="👻 Hide", style=discord.ButtonStyle.secondary, custom_id="vm_hide")
    async def hide_channel(self, interaction: discord.Interaction):
        channel, owner_id = await self.get_user_channel_and_verify(interaction)
        if not channel:
            return

        if interaction.user.id != owner_id:
            await interaction.response.send_message("❌ Only the channel owner can hide this channel.", ephemeral=True)
            return

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.view_channel = False
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("👻 Your channel is now **hidden**.", ephemeral=True)

    @discord.ui.button(label="👁️ Reveal", style=discord.ButtonStyle.secondary, custom_id="vm_reveal")
    async def reveal_channel(self, interaction: discord.Interaction):
        channel, owner_id = await self.get_user_channel_and_verify(interaction)
        if not channel:
            return

        if interaction.user.id != owner_id:
            await interaction.response.send_message("❌ Only the channel owner can reveal this channel.", ephemeral=True)
            return

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.view_channel = True
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("👁️ Your channel is now **revealed**.", ephemeral=True)

    @discord.ui.button(label="✍️ Rename", style=discord.ButtonStyle.primary, custom_id="vm_rename")
    async def rename_channel(self, interaction: discord.Interaction):
        channel, owner_id = await self.get_user_channel_and_verify(interaction)
        if not channel:
            return

        if interaction.user.id != owner_id:
            await interaction.response.send_message("❌ Only the channel owner can rename this channel.", ephemeral=True)
            return

        class RenameModal(discord.ui.Modal, title="Rename Voice Channel"):
            new_name = discord.ui.TextInput(label="New Channel Name", placeholder="My cool channel", max_length=100)

            def __init__(self, vc_channel):
                super().__init__()
                self.vc_channel = vc_channel

            async def on_submit(self, modal_interaction: discord.Interaction):
                await self.vc_channel.edit(name=self.new_name.value)
                await modal_interaction.response.send_message(f"✅ Renamed channel to: **{self.new_name.value}**", ephemeral=True)

        await interaction.response.send_modal(RenameModal(channel))

    @discord.ui.button(label="👑 Claim", style=discord.ButtonStyle.success, custom_id="vm_claim")
    async def claim_channel(self, interaction: discord.Interaction):
        channel, owner_id = await self.get_user_channel_and_verify(interaction)
        if not channel:
            return

        owner_present = any(m.id == owner_id for m in channel.members)
        if owner_present:
            await interaction.response.send_message("❌ The current channel owner is still in the voice channel.", ephemeral=True)
            return

        await removexoxoxoxvoicemasterxoxoxoxchannel(channel.id)
        await addxoxoxoxvoicemasterxoxoxoxchannel(channel.id, interaction.user.id, interaction.guild.id)

        await channel.set_permissions(interaction.user, connect=True, speak=True, mute_members=True, move_members=True)
        await interaction.response.send_message("👑 You have **claimed** ownership of this voice channel!", ephemeral=False)

    @discord.ui.button(label="ℹ️ Info", style=discord.ButtonStyle.secondary, custom_id="vm_info")
    async def info_channel(self, interaction: discord.Interaction):
        channel, owner_id = await self.get_user_channel_and_verify(interaction)
        if not channel:
            return

        owner = interaction.guild.get_member(owner_id)
        embed = discord.Embed(title="VoiceMaster Info", color=discord.Color.blue())
        embed.add_field(name="Owner", value=f"{owner.mention if owner else f'<@{owner_id}>'}", inline=True)
        embed.add_field(name="Bitrate", value=f"{channel.bitrate // 1000}kbps", inline=True)
        embed.add_field(name="Limit", value=f"{channel.user_limit or 'None'}", inline=True)
        embed.add_field(name="Member Count", value=f"{len(channel.members)}", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

class VoiceMaster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        cfg = await getxoxoxoxvoicemasterxoxoxoxconfig(member.guild.id)
        if not cfg:
            return
        categoryxoxoxoxid, creatorxoxoxoxchannelxoxoxoxid, template, deletexoxoxoxempty = cfg

        if after.channel and after.channel.id == creatorxoxoxoxchannelxoxoxoxid:
            guild = member.guild
            category = guild.get_channel(categoryxoxoxoxid)
            if category:
                channel_name = template.replace("{owner}", member.name).replace("{count}", str(len(category.voice_channels)))

                try:
                    tempxoxoxoxchannel = await guild.create_voice_channel(
                        name=channel_name,
                        category=category,
                        reason=f"VoiceMaster - Create temp channel for {member}"
                    )
                    await addxoxoxoxvoicemasterxoxoxoxchannel(tempxoxoxoxchannel.id, member.id, guild.id)

                    await tempxoxoxoxchannel.set_permissions(member, connect=True, speak=True, mute_members=True, move_members=True)

                    await member.move_to(tempxoxoxoxchannel)
                except Exception as e:
                    print(f"Failed to create temp channel or move member: {e}")

        if before.channel and before.channel.id != creatorxoxoxoxchannelxoxoxoxid:
            channel_info = await getxoxoxoxvoicemasterxoxoxoxchannel(before.channel.id)
            if channel_info:
                if len(before.channel.members) == 0 and deletexoxoxoxempty:
                    try:
                        await before.channel.delete(reason="VoiceMaster - Channel empty")
                        await removexoxoxoxvoicemasterxoxoxoxchannel(before.channel.id)
                    except Exception as e:
                        print(f"Failed to delete empty VoiceMaster channel: {e}")

    @commands.group(name="voicemaster", invoke_without_command=True)
    async def voicemaster_group(self, ctx):
        await ctx.send("ℹ️ Use `,voicemaster setup` to configure, or permit/reject commands to manage users.")

    @voicemaster_group.command(name="setup")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    async def voicemaster_setup(self, ctx):
        guild = ctx.guild
        await ctx.send("⚙️ Setting up VoiceMaster systems...")

        try:
            category = await guild.create_category(name="VoiceMaster", reason="VoiceMaster Setup")

            creator_vc = await guild.create_voice_channel(
                name="Join to Create",
                category=category,
                reason="VoiceMaster Setup"
            )

            controls_txt = await guild.create_text_channel(
                name="interface",
                category=category,
                reason="VoiceMaster Setup"
            )

            await setxoxoxoxvoicemasterxoxoxoxconfig(guild.id, category.id, creator_vc.id)

            embed = discord.Embed(
                title="VoiceMaster Interface",
                description="Click the buttons below to configure your voice channel properties dynamically while inside your channel.",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            view = VoiceMasterControls(self)
            await controls_txt.send(embed=embed, view=view)

            await ctx.send("🎉 **VoiceMaster has been configured successfully!** Check the new Category and Interface channel.")
        except Exception as e:
            await ctx.send(f"❌ Failed to setup VoiceMaster: {e}")

    @voicemaster_group.command(name="template")
    @commands.has_permissions(administrator=True)
    async def voicemaster_template(self, ctx, *, template: str):
        await setxoxoxoxvoicemasterxoxoxoxtemplate(ctx.guild.id, template)
        await ctx.send(f"✅ VoiceMaster channel template set to: `{template}`")

    @voicemaster_group.command(name="temporary")
    @commands.has_permissions(administrator=True)
    async def voicemaster_temporary(self, ctx):
        cfg = await getxoxoxoxvoicemasterxoxoxoxconfig(ctx.guild.id)
        if not cfg:
            await ctx.send("❌ VoiceMaster is not setup. Run `,voicemaster setup`.")
            return

        deletexoxoxoxempty = 0 if cfg[3] else 1
        await setxoxoxoxvoicemasterxoxoxoxtemporary(ctx.guild.id, deletexoxoxoxempty)
        await ctx.send(f"✅ VoiceMaster automatic deletion of empty channels is now **{'ENABLED' if deletexoxoxoxempty else 'DISABLED'}**.")

    async def get_user_channel_as_owner(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be inside your temporary voice channel.")
            return None

        channel = ctx.author.voice.channel
        info = await getxoxoxoxvoicemasterxoxoxoxchannel(channel.id)
        if not info or info[0] != ctx.author.id:
            await ctx.send("❌ You are not the owner of the voice channel you are currently in.")
            return None
        return channel

    @voicemaster_group.command(name="permit")
    async def voicemaster_permit(self, ctx, member: discord.Member):
        channel = await self.get_user_channel_as_owner(ctx)
        if not channel:
            return

        await channel.set_permissions(member, connect=True)
        await ctx.send(f"✅ Allowed {member.mention} to join your voice channel.")

    @voicemaster_group.command(name="reject")
    async def voicemaster_reject(self, ctx, member: discord.Member):
        channel = await self.get_user_channel_as_owner(ctx)
        if not channel:
            return

        await channel.set_permissions(member, connect=False)
        await ctx.send(f"✅ Denied {member.mention} from joining your voice channel.")

        if member.voice and member.voice.channel and member.voice.channel.id == channel.id:
            try:
                await member.move_to(None, reason="VoiceMaster - Owner rejected user")
            except:
                pass

    @voicemaster_group.command(name="drag")
    @commands.bot_has_permissions(move_members=True)
    async def voicemaster_drag(self, ctx, member: discord.Member):
        channel = await self.get_user_channel_as_owner(ctx)
        if not channel:
            return

        if not member.voice or not member.voice.channel:
            await ctx.send(f"❌ {member} is not in a voice channel.")
            return

        try:
            await member.move_to(channel, reason="VoiceMaster - Owner dragged user")
            await ctx.send(f"✅ Dragged {member.mention} into your channel.")
        except Exception as e:
            await ctx.send(f"❌ Failed to drag user: {e}")

async def setup(bot):
    cog = VoiceMaster(bot)
    await bot.add_cog(cog)
    bot.add_view(VoiceMasterControls(cog))