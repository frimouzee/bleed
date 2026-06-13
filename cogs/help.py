import discord
from discord.ext import commands

class HelpxoxoxoxDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Home", description="Go back to the main menu"),
            discord.SelectOption(label="Moderation", description="Kick, ban, warn, jail, mute, and setup logs"),
            discord.SelectOption(label="AntiNuke", description="Server security, trust lists, and recovery thresholds"),
            discord.SelectOption(label="AutoMod", description="Spam, links, invites, caps, and bad words filters"),
            discord.SelectOption(label="Giveaway", description="Manage giveaways, requirements, and blacklists"),
            discord.SelectOption(label="VoiceMaster", description="Join-to-create voice channels and permissions"),
            discord.SelectOption(label="Tickets", description="Ticket panel setup, support roles, and ticketing"),
            discord.SelectOption(label="Levels", description="XP leveling settings, rank profiles, leaderboards"),
            discord.SelectOption(label="Config", description="Welcomes, autopfp, bump reminders, and responders"),
            discord.SelectOption(label="Utility", description="AFK system, snipes, confessions, and sticky messages")
        ]
        super().__init__(placeholder="Select a category...", min_values=1, max_values=1, options=options, custom_id="help_select")

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        guild = interaction.guild
        prefix = await self.bot.getxoxoxoxprefix(interaction.message)
        if isinstance(prefix, list):
            prefix = prefix[-1]  

        embed = discord.Embed(color=0x2b2d31)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        if category == "Home":
            embed.title = "Root Bot - Help Menu"
            embed.description = (
                "Welcome to the **Root Bot** Help Menu!\n\n"
                "Use the dropdown selector below to browse through the command modules. "
                "You can also query specific commands using `,help <command>`."
            )
            embed.add_field(name="Useful Links", value="[Support Server](https://discord.gg/btWVjHm58) | [Website](https://axionbotz.vercel.app/)", inline=False)
            embed.set_footer(text=f"Prefix for this server is: {prefix}")

        elif category == "Moderation":
            embed.title = "Moderation Commands"
            embed.description = "Core commands to moderate server members."
            embed.add_field(name=f"`{prefix}setup`", value="Initializes the moderation category, jail role, and `#jail` / `#moderation-log` channels.", inline=False)
            embed.add_field(name=f"`{prefix}kick <member> [reason]`", value="Kicks a member from the server.", inline=False)
            embed.add_field(name=f"`{prefix}ban <member> [reason]`", value="Bans a member from the server.", inline=False)
            embed.add_field(name=f"`{prefix}unban <userxoxoxoxid> [reason]`", value="Unbans a user from the server.", inline=False)
            embed.add_field(name=f"`{prefix}jail <member> [reason]`", value="Locks a user in jail, stripping all roles.", inline=False)
            embed.add_field(name=f"`{prefix}unjail <member> [reason]`", value="Restores original roles to a jailed user.", inline=False)
            embed.add_field(name=f"`{prefix}mute <member> <duration> [reason]`", value="Mutes (timeouts) a user. Duration format e.g. `10m`, `1h`, `1d`.", inline=False)
            embed.add_field(name=f"`{prefix}unmute <member> [reason]`", value="Unmutes (untimeouts) a user.", inline=False)
            embed.add_field(name=f"`{prefix}warn <member> [reason]`", value="Warns a member.", inline=False)
            embed.add_field(name=f"`{prefix}warns <member>`", value="Lists all active warnings for a member.", inline=False)

        elif category == "AntiNuke":
            embed.title = "AntiNuke Commands"
            embed.description = "Set up server defense parameters."
            embed.add_field(name=f"`{prefix}antinuke toggle [on/off]`", value="Enables/disables overall AntiNuke protection.", inline=False)
            embed.add_field(name=f"`{prefix}antinuke settings`", value="View configured AntiNuke settings and active module overrides.", inline=False)
            embed.add_field(name=f"`{prefix}antinuke trust <member>`", value="Bypasses AntiNuke checks for a trusted moderator.", inline=False)
            embed.add_field(name=f"`{prefix}antinuke untrust <member>`", value="Removes a member from the trusted list.", inline=False)
            embed.add_field(name=f"`{prefix}antinuke whitelist <member>`", value="Bypasses all checks entirely.", inline=False)
            embed.add_field(name=f"`{prefix}antinuke threshold <module> <limit>`", value="Sets threshold triggers. Available modules: `bot_add`, `channel_delete`, `role_delete`, `ban`, `kick`, `webhooks`, `emoji_create`, etc.", inline=False)
            embed.add_field(name=f"`{prefix}antinuke <module> [on/off] [--threshold N] [--do ban/kick/strip]`", value="Configure settings for a specific module.", inline=False)
            embed.add_field(name=f"`{prefix}antinuke all [on/off]`", value="Toggles all modules on/off at once.", inline=False)

        elif category == "AutoMod":
            embed.title = "AutoMod / Filter Commands"
            embed.description = "Configurable filters to protect your chat."
            embed.add_field(name=f"`{prefix}filter setup`", value="Initializes and enables AutoMod triggers.", inline=False)
            embed.add_field(name=f"`{prefix}filter timeout <duration>`", value="Sets AutoMod mute duration (e.g. `60s`, `5m`).", inline=False)
            embed.add_field(name=f"`{prefix}filter add <word>`", value="Adds a word to the bad words list.", inline=False)
            embed.add_field(name=f"`{prefix}filter remove <word>`", value="Removes a word from the list.", inline=False)
            embed.add_field(name=f"`{prefix}filter list` / `clear`", value="Lists or clears all banned words.", inline=False)
            embed.add_field(name=f"`{prefix}filter punishment <timeout/kick/ban/jail>`", value="Sets AutoMod trigger punishment.", inline=False)
            embed.add_field(name=f"`{prefix}filter <rule> <on/off> [--threshold N]`", value="Configure filters. Rules: `links`, `invites`, `spoilers`, `caps`, `spam`, `emojis`, `massmention`.", inline=False)
            embed.add_field(name=f"`{prefix}filter whitelist <target> [--events rules] [--reason explanation]`", value="Whitelist user, channel or role from specific rules.", inline=False)

        elif category == "Giveaway":
            embed.title = "Giveaway Commands"
            embed.description = "Manage giveaways."
            embed.add_field(name=f"`{prefix}giveaway start <time> <winners> <prize> [--role Role]`", value="Starts a giveaway with optional role requirement (e.g. `,giveaway start 1h 1 Nitro --role VIP`).", inline=False)
            embed.add_field(name=f"`{prefix}giveaway end <messagexoxoxoxid>`", value="Ends an active giveaway early.", inline=False)
            embed.add_field(name=f"`{prefix}giveaway reroll <messagexoxoxoxid>`", value="Rerolls winners of a finished giveaway.", inline=False)
            embed.add_field(name=f"`{prefix}giveaway blacklist <role>`", value="Blacklist a role from entering giveaways.", inline=False)
            embed.add_field(name=f"`{prefix}giveaway setmax <maxxoxoxoxentries> <role>`", value="Sets max entries per role.", inline=False)

        elif category == "VoiceMaster":
            embed.title = "VoiceMaster Commands"
            embed.description = "Manage join-to-create temporary voice channels."
            embed.add_field(name=f"`{prefix}voicemaster setup`", value="Creates the VoiceMaster category, controls interface channel, and the Join-to-Create voice channel.", inline=False)
            embed.add_field(name=f"`{prefix}voicemaster template <format>`", value="Sets voice channel name template. Variables: `{owner}`, `{count}`.", inline=False)
            embed.add_field(name=f"`{prefix}voicemaster temporary`", value="Toggles deletion of empty temporary voice channels.", inline=False)
            embed.add_field(name=f"`{prefix}voicemaster permit <member>`", value="Allows a member to connect to your temporary channel.", inline=False)
            embed.add_field(name=f"`{prefix}voicemaster reject <member>`", value="Blocks and disconnects a member from your channel.", inline=False)
            embed.add_field(name=f"`{prefix}voicemaster drag <member>`", value="Drags a member into your voice channel.", inline=False)

        elif category == "Tickets":
            embed.title = "Ticket Commands"
            embed.description = "Configurable buttons and panel for support ticketing."
            embed.add_field(name=f"`{prefix}ticket setup #channel`", value="Generates the support ticket panel.", inline=False)
            embed.add_field(name=f"`{prefix}ticket setup #channel --code script`", value="Generates support ticket panel using a custom embed script.", inline=False)
            embed.add_field(name=f"`{prefix}ticket support <role>`", value="Sets the support role allowed to see created ticket channels.", inline=False)
            embed.add_field(name=f"`{prefix}ticket close`", value="Closes and deletes the current ticket channel after 5 seconds.", inline=False)

        elif category == "Levels":
            embed.title = "Leveling Commands"
            embed.description = "XP leveling profile systems."
            embed.add_field(name=f"`{prefix}levels setup` / `disable`", value="Enables/disables the leveling XP gains.", inline=False)
            embed.add_field(name=f"`{prefix}levels channel [#channel]`", value="Configures where level-up alerts are posted.", inline=False)
            embed.add_field(name=f"`{prefix}levels message <messagexoxoxoxtemplate>`", value="Custom scriptable level-up template. Variables: `{user.mention}`, `{level}`, etc.", inline=False)
            embed.add_field(name=f"`{prefix}rank [member]`", value="Displays user level, XP progress, progress bar, and server rank.", inline=False)
            embed.add_field(name=f"`{prefix}leaderboard`", value="View the server's top 10 users.", inline=False)

        elif category == "Config":
            embed.title = "Server Configurations"
            embed.description = "Welcomes, auto-pfps, bump reminders, responders."
            embed.add_field(name=f"`{prefix}prefix <symbol>`", value="Changes the bot prefix for the current server.", inline=False)
            embed.add_field(name=f"`{prefix}welcome setup` / `channel` / `message`", value="Set up welcoming scripts. E.g. `,welcome message Hello {user.mention}! --autoxoxoxoxdelete 15`.", inline=False)
            embed.add_field(name=f"`{prefix}leave setup` / `channel` / `message`", value="Set up leave announcements.", inline=False)
            embed.add_field(name=f"`{prefix}pingonjoin enable #channel`", value="Pings joined members in welcome channel.", inline=False)
            embed.add_field(name=f"`{prefix}autopfp add #channel <category>`", value="Periodically posts profile pictures to channel.", inline=False)
            embed.add_field(name=f"`{prefix}bumpreminder enable` / `disable` / `thankyou`", value="Reminds members to bump 2 hours after last bump.", inline=False)
            embed.add_field(name=f"`{prefix}alias add <alias> <command>`", value="Maps a command alias (e.g. `,alias add stats rank`).", inline=False)
            embed.add_field(name=f"`{prefix}autoresponder add <trigger> <reply>`", value="Auto-replies to user triggers.", inline=False)
            embed.add_field(name=f"`{prefix}autoreaction add <trigger> <emoji>`", value="Auto-reacts to triggers.", inline=False)

        elif category == "Utility":
            embed.title = "Utility Commands"
            embed.description = "AFK status, snipes, sticky messages."
            embed.add_field(name=f"`{prefix}afk [status]`", value="Sets your status to away. Clears on next message.", inline=False)
            embed.add_field(name=f"`{prefix}snipe [index]`", value="Snipes recently deleted messages in the channel.", inline=False)
            embed.add_field(name=f"`{prefix}editsnipe [index]`", value="Snipes recently edited messages.", inline=False)
            embed.add_field(name=f"`{prefix}reactionsnipe [index]`", value="Snipes recently removed message reactions.", inline=False)
            embed.add_field(name=f"`{prefix}clearsnipe`", value="Clears snipe caches for the channel.", inline=False)
            embed.add_field(name=f"`{prefix}stickymessage add #channel <message>`", value="Forces a message to stick to the bottom of a channel.", inline=False)
            embed.add_field(name=f"`{prefix}confessions add #channel` / `remove`", value="Configure confessions output channel. Post confessions using `/confess`.", inline=False)

        await interaction.response.edit_message(embed=embed)

class HelpxoxoxoxView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.add_item(HelpxoxoxoxDropdown(bot))

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def helpxoxoxoxcommand(self, ctx, *, commandxoxoxoxname: str = None):
        prefix = ctx.prefix
        if isinstance(prefix, list):
            prefix = prefix[-1]

        if not commandxoxoxoxname:
            embed = discord.Embed(
                title="Root Bot - Help Menu",
                description=(
                    "Welcome to the **Root Bot** Help Menu!\n\n"
                    "Use the dropdown selector below to browse through the command modules. "
                    "You can also query specific commands using `,help <command>`."
                ),
                color=0x2b2d31
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(name="Useful Links", value="[Support Server](https://discord.gg/btWVjHm58) | [Website](https://axionbotz.vercel.app/)", inline=False)
            embed.set_footer(text=f"Prefix for this server is: {prefix}")

            view = HelpxoxoxoxView(self.bot)
            await ctx.send(embed=embed, view=view)
            return

        cmdxoxoxoxclean = commandxoxoxoxname.lower().strip()
        cmd = self.bot.get_command(cmdxoxoxoxclean)

        if not cmd:
            await ctx.send(f"Command `{commandxoxoxoxname}` not found.")
            return

        embed = discord.Embed(
            title=f"Command Info: {prefix}{cmd.qualified_name}",
            description=cmd.help or "No description provided.",
            color=0x2b2d31
        )
        if cmd.aliases:
            embed.add_field(name="Aliases", value=", ".join([f"`{a}`" for a in cmd.aliases]), inline=True)

        usage = f"`{prefix}{cmd.qualified_name} {cmd.signature}`" if cmd.signature else f"`{prefix}{cmd.qualified_name}`"
        embed.add_field(name="Usage", value=usage, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))