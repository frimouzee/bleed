import discord
import re
import datetime

def replacexoxoxoxvariables(text: str, context: dict) -> str:
    if not text:
        return text

    user = context.get('user')
    guild = context.get('guild')
    channel = context.get('channel')
    reason = context.get('reason') or context.get('custom.reason')
    level = context.get('level')
    xp = context.get('xp')
    prize = context.get('prize')
    winners = context.get('winners')
    ends = context.get('ends')

    replacementsxoxoxox = {}

    if user:
        replacementsxoxoxox['{user}'] = str(user)
        replacementsxoxoxox['{user.mention}'] = user.mention
        replacementsxoxoxox['{user.name}'] = user.name
        replacementsxoxoxox['{user.tag}'] = f"#{user.discriminator}" if (hasattr(user, 'discriminator') and user.discriminator != '0') else ""
        avatarxoxoxoxurl = user.display_avatar.url if hasattr(user, 'display_avatar') else ""
        replacementsxoxoxox['{user.avatar}'] = avatarxoxoxoxurl
        replacementsxoxoxox['{user.display_avatar}'] = avatarxoxoxoxurl
        replacementsxoxoxox['{user.id}'] = str(user.id)
        if hasattr(user, 'created_at') and user.created_at:
            replacementsxoxoxox['{user.created_at}'] = f"<t:{int(user.created_at.timestamp())}:F>"
            replacementsxoxoxox['{user.created_at_timestamp}'] = str(int(user.created_at.timestamp()))
        replacementsxoxoxox['{user.display_name}'] = user.display_name
        replacementsxoxoxox['{user.bot}'] = "Yes" if getattr(user, 'bot', False) else "No"

        if hasattr(user, 'joined_at') and user.joined_at:
            replacementsxoxoxox['{user.joined_at}'] = f"<t:{int(user.joined_at.timestamp())}:F>"
            replacementsxoxoxox['{user.joined_at_timestamp}'] = str(int(user.joined_at.timestamp()))
        if hasattr(user, 'top_role') and user.top_role:
            replacementsxoxoxox['{user.top_role}'] = user.top_role.mention
            replacementsxoxoxox['{user.rolexoxoxoxlist}'] = ", ".join([r.name for r in user.roles if r.name != "@everyone"])
            replacementsxoxoxox['{user.rolexoxoxoxtextxoxoxoxlist}'] = ", ".join([r.mention for r in user.roles if r.name != "@everyone"])

    if guild:
        replacementsxoxoxox['{guild.name}'] = guild.name
        replacementsxoxoxox['{guild.id}'] = str(guild.id)
        replacementsxoxoxox['{guild.count}'] = str(guild.member_count)
        replacementsxoxoxox['{guild.icon}'] = guild.icon.url if guild.icon else ""
        replacementsxoxoxox['{guild.banner}'] = guild.banner.url if guild.banner else ""
        replacementsxoxoxox['{guild.boost_count}'] = str(guild.premium_subscription_count)
        replacementsxoxoxox['{guild.boost_tier}'] = f"Level {guild.premium_tier}"
        replacementsxoxoxox['{guild.channels_count}'] = str(len(guild.channels))
        replacementsxoxoxox['{guild.role_count}'] = str(len(guild.roles))
        if guild.owner:
            replacementsxoxoxox['{guild.owner_id}'] = str(guild.owner_id)

    if channel:
        replacementsxoxoxox['{channel.name}'] = channel.name
        replacementsxoxoxox['{channel.id}'] = str(channel.id)
        replacementsxoxoxox['{channel.mention}'] = channel.mention
        replacementsxoxoxox['{channel.type}'] = str(channel.type)

    if reason:
        replacementsxoxoxox['{custom.reason}'] = str(reason)
        replacementsxoxoxox['{reason}'] = str(reason)
    if level is not None:
        replacementsxoxoxox['{level}'] = str(level)
    if xp is not None:
        replacementsxoxoxox['{xp}'] = str(xp)
    if prize:
        replacementsxoxoxox['{prize}'] = str(prize)
    if winners:
        replacementsxoxoxox['{winners}'] = str(winners)
    if ends:
        replacementsxoxoxox['{ends}'] = str(ends)

    for key in sorted(replacementsxoxoxox.keys(), key=len, reverse=True):
        if replacementsxoxoxox[key] is not None:
            text = text.replace(key, replacementsxoxoxox[key])

    return text

class ScriptButton(discord.ui.Button):
    def __init__(self, label, url=None, style=discord.ButtonStyle.link, custom_id=None, emoji=None, disabled=False):
        kwargs = {
            "label": label,
            "style": style,
            "disabled": disabled
        }
        if emoji:
            kwargs["emoji"] = emoji
        if style == discord.ButtonStyle.link:
            kwargs["url"] = url
        else:
            kwargs["custom_id"] = custom_id or f"script_btn_{label}_{url}"

        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
        except:
            pass

def parsexoxoxoxscript(script_text: str, context: dict):
    """
    Parses a Root template script and returns:
    (contentxoxoxoxstr, embed_object, view_object, stickerxoxoxoxname)
    """
    if not script_text:
        return None, None, None, None

    contentxoxoxoxstr = None
    hasxoxoxoxembed = False
    embedxoxoxoxcolor = discord.Color.default()
    embedxoxoxoxtitle = None
    embedxoxoxoxdesc = None
    embedxoxoxoxthumbnail = None
    embedxoxoxoximage = None
    embedxoxoxoxfooterxoxoxoxtext = None
    embedxoxoxoxfooterxoxoxoxicon = None
    embedxoxoxoxauthorxoxoxoxname = None
    embedxoxoxoxauthorxoxoxoxicon = None
    embedxoxoxoxauthorxoxoxoxurl = None
    embedxoxoxoxfields = []

    buttons = []
    stickerxoxoxoxname = None

    lines = script_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line == "{embed}":
            hasxoxoxoxembed = True
            continue

        contentxoxoxoxmatch = re.match(r"^\{content:\s*(.*)\}$", line, re.IGNORECASE)
        if contentxoxoxoxmatch:
            contentxoxoxoxstr = replacexoxoxoxvariables(contentxoxoxoxmatch.group(1).strip(), context)
            continue

        colorxoxoxoxmatch = re.match(r"^\{color:\s*(.*)\}$", line, re.IGNORECASE)
        if colorxoxoxoxmatch:
            colorxoxoxoxval = replacexoxoxoxvariables(colorxoxoxoxmatch.group(1).strip(), context)
            if colorxoxoxoxval.startswith("#"):
                colorxoxoxoxval = colorxoxoxoxval[1:]
            try:
                embedxoxoxoxcolor = discord.Color(int(colorxoxoxoxval, 16))
            except ValueError:
                try:
                    embedxoxoxoxcolor = discord.Color(int(colorxoxoxoxval))
                except ValueError:
                    pass
            continue

        titlexoxoxoxmatch = re.match(r"^\{title:\s*(.*)\}$", line, re.IGNORECASE)
        if titlexoxoxoxmatch:
            embedxoxoxoxtitle = replacexoxoxoxvariables(titlexoxoxoxmatch.group(1).strip(), context)
            continue

        descxoxoxoxmatch = re.match(r"^\{description:\s*(.*)\}$", line, re.IGNORECASE)
        if descxoxoxoxmatch:
            embedxoxoxoxdesc = replacexoxoxoxvariables(descxoxoxoxmatch.group(1).strip(), context)
            continue

        thumbxoxoxoxmatch = re.match(r"^\{thumbnail:\s*(.*)\}$", line, re.IGNORECASE)
        if thumbxoxoxoxmatch:
            embedxoxoxoxthumbnail = replacexoxoxoxvariables(thumbxoxoxoxmatch.group(1).strip(), context)
            continue

        imgxoxoxoxmatch = re.match(r"^\{image:\s*(.*)\}$", line, re.IGNORECASE)
        if imgxoxoxoxmatch:
            embedxoxoxoximage = replacexoxoxoxvariables(imgxoxoxoxmatch.group(1).strip(), context)
            continue

        footerxoxoxoxmatch = re.match(r"^\{footer:\s*(.*)\}$", line, re.IGNORECASE)
        if footerxoxoxoxmatch:
            footerxoxoxoxcontent = replacexoxoxoxvariables(footerxoxoxoxmatch.group(1).strip(), context)
            parts = footerxoxoxoxcontent.split("&&")
            embedxoxoxoxfooterxoxoxoxtext = parts[0].strip()
            if len(parts) > 1:
                embedxoxoxoxfooterxoxoxoxicon = parts[1].strip()
            continue

        authorxoxoxoxmatch = re.match(r"^\{author:\s*(.*)\}$", line, re.IGNORECASE)
        if authorxoxoxoxmatch:
            authorxoxoxoxcontent = replacexoxoxoxvariables(authorxoxoxoxmatch.group(1).strip(), context)
            parts = authorxoxoxoxcontent.split("&&")
            for part in parts:
                part = part.strip()
                if part.lower().startswith("name:"):
                    embedxoxoxoxauthorxoxoxoxname = part[5:].strip()
                elif part.lower().startswith("icon:"):
                    embedxoxoxoxauthorxoxoxoxicon = part[5:].strip()
                elif part.lower().startswith("url:"):
                    embedxoxoxoxauthorxoxoxoxurl = part[4:].strip()
            continue

        fieldxoxoxoxmatch = re.match(r"^\{field:\s*(.*)\}$", line, re.IGNORECASE)
        if fieldxoxoxoxmatch:
            fieldxoxoxoxcontent = replacexoxoxoxvariables(fieldxoxoxoxmatch.group(1).strip(), context)
            parts = fieldxoxoxoxcontent.split("&&")
            if len(parts) >= 2:
                fxoxoxoxname = parts[0].strip()
                fxoxoxoxval = parts[1].strip()
                fxoxoxoxinline = False
                if len(parts) > 2 and parts[2].strip().lower() == "inline":
                    fxoxoxoxinline = True
                embedxoxoxoxfields.append((fxoxoxoxname, fxoxoxoxval, fxoxoxoxinline))
            continue

        buttonxoxoxoxmatch = re.match(r"^\{button:\s*(.*)\}$", line, re.IGNORECASE)
        if buttonxoxoxoxmatch:
            btnxoxoxoxcontent = replacexoxoxoxvariables(buttonxoxoxoxmatch.group(1).strip(), context)
            parts = btnxoxoxoxcontent.split("&&")
            btnxoxoxoxlabel = "Click"
            btnxoxoxoxurl = None
            btnxoxoxoxcustomxoxoxoxid = None
            btnxoxoxoxemoji = None
            btnxoxoxoxstyle = discord.ButtonStyle.link
            btnxoxoxoxdisabled = False

            for part in parts:
                part = part.strip()
                if part.lower().startswith("label:"):
                    btnxoxoxoxlabel = part[6:].strip()
                elif part.lower().startswith("url:"):
                    btnxoxoxoxurl = part[4:].strip()
                elif part.lower().startswith("custom_id:"):
                    btnxoxoxoxcustomxoxoxoxid = part[10:].strip()
                elif part.lower().startswith("emoji:"):
                    btnxoxoxoxemoji = part[6:].strip()
                elif part.lower().startswith("style:"):
                    stylexoxoxoxstr = part[6:].strip().lower()
                    if stylexoxoxoxstr == "primary":
                        btnxoxoxoxstyle = discord.ButtonStyle.primary
                    elif stylexoxoxoxstr == "secondary":
                        btnxoxoxoxstyle = discord.ButtonStyle.secondary
                    elif stylexoxoxoxstr == "success":
                        btnxoxoxoxstyle = discord.ButtonStyle.success
                    elif stylexoxoxoxstr == "danger":
                        btnxoxoxoxstyle = discord.ButtonStyle.danger
                    elif stylexoxoxoxstr == "link":
                        btnxoxoxoxstyle = discord.ButtonStyle.link
                elif part.lower() == "disabled":
                    btnxoxoxoxdisabled = True

            if btnxoxoxoxstyle != discord.ButtonStyle.link and not btnxoxoxoxcustomxoxoxoxid:
                btnxoxoxoxcustomxoxoxoxid = f"custom_btn_{len(buttons)}_{btnxoxoxoxlabel}"

            buttons.append(ScriptButton(btnxoxoxoxlabel, btnxoxoxoxurl, btnxoxoxoxstyle, btnxoxoxoxcustomxoxoxoxid, btnxoxoxoxemoji, btnxoxoxoxdisabled))
            continue

        stickerxoxoxoxmatch = re.match(r"^\{sticker:\s*(.*)\}$", line, re.IGNORECASE)
        if stickerxoxoxoxmatch:
            stickerxoxoxoxname = replacexoxoxoxvariables(stickerxoxoxoxmatch.group(1).strip(), context)
            continue

    embed = None
    if hasxoxoxoxembed:
        embed = discord.Embed(color=embedxoxoxoxcolor)
        if embedxoxoxoxtitle:
            embed.title = embedxoxoxoxtitle
        if embedxoxoxoxdesc:
            embed.description = embedxoxoxoxdesc
        if embedxoxoxoxthumbnail:
            embed.set_thumbnail(url=embedxoxoxoxthumbnail)
        if embedxoxoxoximage:
            embed.set_image(url=embedxoxoxoximage)
        if embedxoxoxoxfooterxoxoxoxtext:
            embed.set_footer(text=embedxoxoxoxfooterxoxoxoxtext, icon_url=embedxoxoxoxfooterxoxoxoxicon)
        if embedxoxoxoxauthorxoxoxoxname:
            embed.set_author(name=embedxoxoxoxauthorxoxoxoxname, icon_url=embedxoxoxoxauthorxoxoxoxicon, url=embedxoxoxoxauthorxoxoxoxurl)
        for fxoxoxoxname, fxoxoxoxval, fxoxoxoxinline in embedxoxoxoxfields:
            embed.add_field(name=fxoxoxoxname, value=fxoxoxoxval, inline=fxoxoxoxinline)

    view = None
    if buttons:
        view = discord.ui.View(timeout=None)
        for btn in buttons:
            view.add_item(btn)

    return contentxoxoxoxstr, embed, view, stickerxoxoxoxname