from datetime import datetime,timedelta,timezone

from dateutil.tz import tzutc,tzlocal

import asyncio

import hikari

import lightbulb

from lightbulb.ext import tasks

import aiosqlite

import webcolors as col

import csv

plugin = lightbulb.Plugin("Moderation","Moderation Commands For The Bot")


plugin.add_checks(lightbulb.guild_only, lightbulb.has_guild_permissions(hikari.Permissions.KICK_MEMBERS or hikari.Permissions.BAN_MEMBERS or hikari.Permissions.MUTE_MEMBERS or hikari.Permissions.MODERATE_MEMBERS or hikari.Permissions.MANAGE_GUILD or hikari.Permissions.MANAGE_ROLES or hikari.Permissions.MANAGE_CHANNELS or hikari.Permissions.MANAGE_MESSAGES or hikari.Permissions.DEAFEN_MEMBERS))

@plugin.command()
@lightbulb.option('reason','reason for kicking the user',required=False)
@lightbulb.option('user','mention the user to kick from guild',type=hikari.Member)
@lightbulb.command('kick','Kicks Member From The Guild')
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def kick(ctx:lightbulb.Context):
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cursor:
            server_name = str(ctx.get_guild().name)[0] + str(ctx.guild_id)
            embed = hikari.Embed(title="Kick User",color=(0,255,255))
            embed.add_field(name=f"{ctx.options.user.username} has been kicked from the server for {ctx.options.reason}",value="\u200b")
            await ctx.respond(embed=embed)
            await ctx.options.user.send(embed=embed)
            await cursor.execute(f"DELETE FROM {server_name} WHERE Member_id = {ctx.options.user.id}")
        await db.commit()
    await ctx.app.rest.kick_user(ctx.guild_id,ctx.options.user.id,reason=str(ctx.options.reason))

@plugin.command()
@lightbulb.option('reason','reason for banning the user',required=False)
@lightbulb.option('user','mention the user to ban from guild',type=hikari.Member)
@lightbulb.command('ban','Bans Member From The Guild')
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def ban(ctx:lightbulb.Context):
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cursor:
           server_name = str(ctx.get_guild().name)[0] + str(ctx.guild_id)
           embed = hikari.Embed(title="Ban User",color=(0,255,255))
           embed.add_field(name=f"{ctx.options.user.username} has been banned from the server for {ctx.options.reason}",value="\u200b")
           await ctx.respond(embed=embed)
           embed.edit_field(0,f"{ctx.options.user.username} you have been banned from the {ctx.get_guild().name}","\u200b")
           await ctx.options.user.send(embed=embed)
           await cursor.execute(f"DELETE FROM {server_name} WHERE Member_id = {ctx.options.user.id}")
        await db.commit()
    await ctx.app.rest.ban_user(ctx.guild_id,ctx.options.user.id,reason=str(ctx.options.reason))

@plugin.command()
@lightbulb.option('reason','reason for unbanning the user',required=False)
@lightbulb.option('member','type username with its discriminator also # between them',required=True)
@lightbulb.command('unban','Unban Member From The Guild')
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def unban(ctx:lightbulb.Context):
    banned_users = await ctx.app.rest.fetch_bans(ctx.guild_id)
    member_name,member_discriminator = ctx.options.member.split('#')
    
    for ban_entry in banned_users:
        user_name,user_discriminator,user_id = ban_entry.user.username,ban_entry.user.discriminator,ban_entry.user.id

        if(user_name,user_discriminator) == (member_name,member_discriminator):
            await ctx.app.rest.unban_user(ctx.guild_id,user_id,reason=str(ctx.options.reason))
            embed = hikari.Embed(title="UnBan User",color=(0,255,255))
            embed.add_field(name=f"{ctx.options.member} has been unbanned from the server",value="\u200b") 
            await ctx.respond(embed=embed)
    '''with open('tempban.csv','r') as f:
        ban = json.load(f)
        ban = dict(ban)
        del ban[str(member_name)+str(ctx.guild_id)[:8:]+str(ctx.options.member.id)[:8:]]'''

@plugin.command()
@lightbulb.option('reason','reason for muting the user',required=False,modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.option('member','mention the user for muting them',type=hikari.Member,required=True)
@lightbulb.command('mute','Mute Member From The Guild',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def mute(ctx:lightbulb.Context) -> None:
    muteRole = ""
    Role =  await ctx.app.rest.fetch_roles(ctx.guild_id)
    for i in Role:
        if i.name.lower() == 'mute':
            muteRole = i
    if not muteRole:
        muteRole = await ctx.app.rest.create_role(ctx.guild_id,name="Mute",permissions=hikari.Permissions.VIEW_CHANNEL,color=(255,0,0))
    channels = [channel for channel in ctx.get_guild().get_channels().values() if str(channel.type) == "GUILD_TEXT"]
    for channel in channels:
        await ctx.app.rest.edit_permission_overwrites(channel=channel,target=muteRole,allow=hikari.Permissions.VIEW_CHANNEL,deny=hikari.Permissions.SEND_MESSAGES)
    embed = hikari.Embed(title="Mute User",color=(0,255,255))
    embed.add_field(name=f"You Were Muted In {ctx.get_guild().name} For {ctx.options.reason}",value="\u200b")
    await ctx.app.rest.add_role_to_member(ctx.guild_id,ctx.options.member,muteRole,reason=str(ctx.options.reason))
    await ctx.options.member.send(embed=embed)
    embed.edit_field(0,f"Muted {ctx.options.member.username} for {ctx.options.reason}","\u200b")
    await ctx.respond(embed=embed)    

@plugin.command()
@lightbulb.option('member','mention the user for unmuting them',type=hikari.Member,required=True)
@lightbulb.command('unmute','Unmute Member From The Guild',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def unmute(ctx:lightbulb.Context) -> None:
    muteRole = ""
    Role = await ctx.app.rest.fetch_roles(ctx.guild_id)
    for i in Role:
        if i.name.lower() == 'mute':
            muteRole = i.id
    await ctx.app.rest.remove_role_from_member(ctx.guild_id,ctx.options.member,role=muteRole)
    embed = hikari.Embed(title="Unmute User",color=(0,255,255))
    embed.add_field(name=f"You Were Unmuted In {ctx.get_guild().name}",value="\u200b")
    await ctx.options.member.send(embed=embed)
    embed.edit_field(0,f"Unmuted {ctx.options.member.username}","\u200b")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option('reason','reason for warning the user',required=False,modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.option('member','mention the user to warn them',type=hikari.Member,required=True)
@lightbulb.command('warn','Warns The User',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def warn(ctx:lightbulb.Context) -> None:
    server_name = str(ctx.get_guild().name)[0] + str(ctx.guild_id)
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        cur = await db.execute(f"SELECT Warns FROM {server_name} WHERE Member_id = {ctx.options.member.id}")
        warn = await cur.fetchone()
        warn = warn[0]
        warn += 1
        await db.execute(f"UPDATE {server_name} SET Warns = {warn} WHERE Member_id = {ctx.options.member.id}")
        await db.commit()
    embed = hikari.Embed(title="Warn User",color=(0,255,255))
    embed.add_field(name=f"You have been warned for {ctx.options.reason} \n You Now have total {warn} warns in the {ctx.get_guild().name}",value="\u200b")
    await ctx.options.member.send(embed=embed)
    embed.edit_field(0,f"{ctx.options.member.username} warned for {ctx.options.reason} \n They now have total {warn} warns","\u200b")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option('member','mention the user to clear thier warns',type=hikari.Member,required=True)
@lightbulb.command('clear_infractions','Warns The User',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def clear_infractions(ctx:lightbulb.Context) -> None:
    server_name = str(ctx.get_guild().name)[0] + str(ctx.guild_id)
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        cur = await db.execute(f"SELECT Warns FROM {server_name} WHERE Member_id = {ctx.options.member.id}")
        warn = await cur.fetchone()
        warn = warn[0]
        warn = 0
        await db.execute(f"UPDATE {server_name} SET Warns = {warn} WHERE Member_id = {ctx.options.member.id}")
        await db.commit()
    embed = hikari.Embed(title="Clear Infractions",color=(0,255,255))
    embed.add_field(name=f"Your all warnings are cleared for {ctx.options.reason} \n You Now have total {warn} warns in the {ctx.get_guild().name}",value="\u200b")
    await ctx.options.member.send(embed=embed)
    embed.edit_field(0,f"{ctx.options.member.username} warning cleared for {ctx.options.reason} \n They now have total {warn} warns","\u200b")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option('member','mention member to display the infractions',type=hikari.Member,required=True)
@lightbulb.command('infractions','Displays Infractions For The Mentioned User',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def infractions(ctx:lightbulb.Context) -> None:
    server_name = str(ctx.get_guild().name)[0] + str(ctx.guild_id)
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        cur = await db.execute(f"SELECT Warns FROM {server_name} WHERE Member_id = {ctx.options.member.id}")
        warn = await cur.fetchone()
        warn = warn[0]
    embed = hikari.Embed(title="Infractions",color=(0,255,255))
    embed.add_field(name=f"{ctx.options.member.username} has {warn} infractions",value="\u200b")
    await ctx.respond(embed=embed)
    print(ctx.options.member.mention)

@plugin.command()
@lightbulb.option('prefix','write the new prefix for guild',required=True)
@lightbulb.command('setprefix','sets new prefix for the guild',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def setprefix(ctx:lightbulb.Context) -> None:
    id = ctx.guild_id
    sql = "UPDATE SERVERINFORMATION SET Server_Prefix = ? WHERE Server_Id = ?"
    val = (ctx.options.prefix,id)
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cur:
            await cur.execute(sql,val)
        await db.commit()
    embed = hikari.Embed(title="Set Prefix",color=(0,255,255))
    embed.add_field(name=f"Prefix Has Been Set To {ctx.options.prefix}",value="\u200b")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option('member','mention the member to the member info',required=True,type=hikari.Member)
@lightbulb.command('user_info','Gets The User Info For Mentioned Member',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def user_info(ctx:lightbulb.Context) -> None:
    date_format = "%a, %b %d, %Y @ %I:%M %p"
    perm = ['ADD_REACTIONS','ADMINISTRATOR','ATTACH_FILES','BAN_MEMBERS','CHANGE_NICKNAME','CONNECT','CREATE_INSTANT_INVITE',
    'CREATE_PRIVATE_THREADS','CREATE_PUBLIC_THREADS','DEAFEN_MEMBERS','EMBED_LINKS','KICK_MEMBERS','MANAGE_CHANNELS','MANAGE_EMOJIS_AND_STICKERS',
    'MANAGE_GUILD','MANAGE_MESSAGES','MANAGE_NICKNAMES','MANAGE_ROLES','MANAGE_THREADS','MANAGE_WEBHOOKS','MENTION_ROLES','MODERATE_MEMBERS','MOVE_MEMBERS',
    'MUTE_MEMBERS','PRIORITY_SPEAKER','READ_MESSAGE_HISTORY','REQUEST_TO_SPEAK','SEND_MESSAGES','SEND_MESSAGES_IN_THREADS','SEND_TTS_MESSAGES','SPEAK',
    'START_EMBEDDED_ACTIVITIES','STREAM','USE_APPLICATION_COMMANDS','USE_EXTERNAL_EMOJIS','USE_EXTERNAL_STICKERS','VIEW_AUDIT_LOG','VIEW_CHANNEL','VIEW_GUILD_INSIGHTS']

    if ctx.options.member.premium_since == None:
        boosting_since = "Not Boosting"
    else:
        boosting_since = ctx.options.member.premium_since.strftime(date_format)

    server_name = str(ctx.get_guild().name)[0] + str(ctx.guild_id)
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        cur = await db.execute(f"SELECT Warns FROM {server_name} WHERE Member_id = {ctx.options.member.id}")
        warn = await cur.fetchall()
        if len(warn) != 0:
            print(warn)
            warn = warn[0]
        else:
            warn = 0  
    memb_perm = []
    for i in lightbulb.utils.permissions_for(member=ctx.options.member):
        memb_perm.append(i.name)

    comm_key_perm = list(set(perm).intersection(memb_perm))
    comm_key_perm = sorted(comm_key_perm, key=lambda x: perm.index(x) if x in perm else 0)
    comm_key_perm = ','.join(map(str,comm_key_perm))
    embed = hikari.Embed(title="User Info",color=(0,255,255))
    embed.add_field(name=f"Userinfo Command for {ctx.options.member.username}#{ctx.options.member.discriminator}",value=f"UserId | {ctx.options.member.id}",inline=True)
    embed.add_field(name="Server Permissions",value=f"{comm_key_perm}",inline=True)
    embed.add_field(name="Server Infractions",value=f"{warn}",inline=True)
    embed.add_field(name="Joined Server At",value=f"{ctx.options.member.joined_at.strftime(date_format)}",inline=True)
    embed.add_field(name="Joined Discord At",value=f"{ctx.options.member.created_at.strftime(date_format)}",inline=True)
    embed.add_field(name="Boosting Since",value=f"{boosting_since}",inline=True)
    embed.set_footer(text=f"Requested By {ctx.options.member.username}#{ctx.options.member.discriminator} | {ctx.options.member.id}")
    await ctx.respond(embed=embed)        

@plugin.command()
@lightbulb.command('server_info','Gets The Server Info',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def server_info(ctx:lightbulb.Context) -> None:
    date_format = "%a, %b %d, %Y @ %I:%M %p"
    VIPerks = ctx.get_guild().premium_tier
    roles = await ctx.get_guild().fetch_roles()
    role_list = []
    for i in roles:
        role_list.append(i.name)
    role_list = ",".join(map(str,role_list))
    channel_list = dict(ctx.get_guild().get_channels())
    member_list = dict(ctx.get_guild().get_members())
    members = str(len(member_list))+" members,\n"
    members = members + str(sum(1 for i in member_list.values() if i.is_bot == True)) + " bots,"
    members = members + str(sum(1 for i in member_list.values() if i.is_bot == False)) + " humans"
    channels = str(len(channel_list))+" total channels:\n"
    channels = channels + str(sum(1 for i in channel_list.values() if str(i.type) == "GUILD_CATEGORY")) + " categories\n"
    channels = channels + str(sum(1 for i in channel_list.values() if str(i.type) == "GUILD_TEXT")) + " text,"
    channels = channels + str(sum(1 for i in channel_list.values() if str(i.type) == "GUILD_VOICE")) + " voice"
    VIPerksCount = ctx.get_guild().premium_subscription_count
    member = await ctx.app.rest.fetch_member(guild=ctx.guild_id,user=ctx.get_guild().owner_id)
    embed = hikari.Embed(title="Server Info",color=(0,255,255))
    embed.add_field(name="Owner",value=f"{member}",inline=True)
    embed.add_field(name="VIP Perks",value=f"{VIPerks}",inline=True)
    embed.add_field(name="Boost Level",value=f"{VIPerksCount}",inline=True)
    embed.add_field(name="Total Roles",value=f"{len(roles)}",inline=True)
    embed.add_field(name="Role List",value=f"{role_list}",inline=True)
    embed.add_field(name="Total Channels",value=f"{channels}",inline=True)
    embed.add_field(name="Members",value=f"{members}",inline=True)
    embed.set_footer(text=f"Server Name:{ctx.get_guild().name} | Server Id:{ctx.guild_id} | Server Created At:{ctx.get_guild().created_at.strftime(date_format)}")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option('role','mention the role to get the role info',required=True,type=hikari.Role)
@lightbulb.command('role_info','Gets The Role Info',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def role_info(ctx:lightbulb.Context) -> None:
    date_format = "%a, %b %d, %Y @ %I:%M %p"
    role_name = ctx.options.role.name
    role_id = ctx.options.role.id
    try:
        role_color = col.hex_to_name(hex_value=str(ctx.options.role.color),spec='css3')
    except:
        role_color = "Name Not Defined For The Color In CSS3\nHexCode For The Color Is "+str(ctx.options.role.color)
    role_mentionable = "Yes" if ctx.options.role.is_mentionable == True else "No"
    role_hoisted = "Yes" if ctx.options.role.is_hoisted == True else "No"
    role_managed = "Yes" if ctx.options.role.is_managed == True else "No"
    role_position = ctx.options.role.position
    role_created_at = ctx.options.role.created_at.strftime(date_format)
    embed = hikari.Embed(title="Role Info",color=(0,255,255))
    embed.add_field(name="Role Name",value=f"{role_name}",inline=True)
    embed.add_field(name="Role Id",value=f"{role_id}",inline=True)
    embed.add_field(name="Role Color",value=f"{role_color}",inline=True)
    embed.add_field(name="Role Mentionable",value=f"{role_mentionable}",inline=True)
    embed.add_field(name="Role Hoisted",value=f"{role_hoisted}",inline=True)
    embed.add_field(name="Role Managed",value=f"{role_managed}",inline=True)
    embed.add_field(name="Role Position",value=f"{role_position}",inline=True)
    embed.set_footer(text=f"Role Created At:{role_created_at}")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.command('slowmode','Enable/Disable Slowmode in channel',inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixCommandGroup,lightbulb.SlashCommandGroup)
async def slowmode(ctx:lightbulb.Context) -> None:
    pass

@slowmode.child
@lightbulb.option('time','Timeout Duration Of The Slowmode (ex :hour:minutes:seconds)',default="0:02:0",required=False,type=str,modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.command('timeout','Timeout Duration Of The Slowmode',inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand,lightbulb.SlashSubCommand)
async def timeout(ctx:lightbulb.Context) -> None:
    second=minute=hour = 0
    format = "%H:%M:%S"
    embed = hikari.Embed(title="Slowmode",color=(0,255,255))
    try:
        datetime_obj = datetime.strptime(ctx.options.time, format)
        time = datetime_obj.time()
        hour = time.hour
        second = time.second
        minute = time.minute
        await ctx.app.rest.edit_channel(ctx.get_channel().id,rate_limit_per_user=timedelta(hours=hour,minutes=minute,seconds=second))
        embed.add_field(name="Slowmode Description",value=f"Slowmode Enabled In The Channel For {hour} Hour {minute} Minutes {second} Seconds")
        await ctx.respond(embed=embed)
    except ValueError:
        embed.add_field(name="Slowmode Description",value="Invalid duration. Please provide a valid timeout in the form Hour:Minute:Second")
        await ctx.respond(embed=embed)

@slowmode.child
@lightbulb.option('state','on by default,Type off to disable slowmode',required=False,type=str)
@lightbulb.command('state','Slowmode state in channel',inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand,lightbulb.SlashSubCommand)
async def state(ctx:lightbulb.Context) -> None:
    embed = hikari.Embed(title="Slowmode",color=(0,255,255))
    if ctx.options.state == "off":
        await ctx.app.rest.edit_channel(ctx.get_channel().id,rate_limit_per_user=0)
        embed.add_field(name="Slowmode Description",value="Slowmode Disabled In The Channel")
        await ctx.respond(embed=embed)
    else:
        pass

@plugin.command()
@lightbulb.option('user','mention the user to delete thier messages in the channel',required=False,type=hikari.Member)
@lightbulb.option('limit','number of message  to delete in the channel',required=True,type=int)
@lightbulb.command('clear','Clears The Message In The Channel',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def clear(ctx:lightbulb.Context) -> None:
    bulk_delete_limit = datetime.now(timezone.utc) - timedelta(days=14)
    if ctx.options.user == None:
        if ctx.options.limit <= 500:
            iterator = (ctx.app.rest.fetch_messages(ctx.channel_id).take_while(lambda message : message.created_at > bulk_delete_limit).limit(ctx.options.limit))
            tasks = []
            async for messages in iterator.chunk(100):
                task = asyncio.create_task(ctx.app.rest.delete_messages(ctx.channel_id, messages))
                tasks.append(task)

            await asyncio.wait(tasks)
        else:
            await ctx.respond("Limit For Deleting The Messages One Time Is 500")
    else:
        if ctx.options.limit <= 500:
            iterator = (ctx.app.rest.fetch_messages(ctx.channel_id).take_while(lambda message : message.created_at > bulk_delete_limit).filter(lambda message : message.author.id == ctx.options.user.id).limit(ctx.options.limit))
            tasks = []
            async for messages in iterator.chunk(100):
                task = asyncio.create_task(ctx.app.rest.delete_messages(ctx.channel_id, messages))
                tasks.append(task)

            await asyncio.wait(tasks)
        else:
            await ctx.respond("Limit For Deleting The Messages One Time Is 500")

@plugin.command()
@lightbulb.option('role','mention the role to get the member list',required=True,type=hikari.Role)
@lightbulb.command('members','Gets the members list for the mentioned role',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def members(ctx:lightbulb.Context) -> None:
    print(dict(ctx.get_guild().get_members()))
    member_list = [member.display_name for member in ctx.get_guild().get_members().values() if ctx.options.role.id in member.role_ids]
    member_list = ",\n".join(member_list)
    embed = hikari.Embed(title=f"Members With {ctx.options.role.name} Are :- ",color=(0,255,255))
    embed.add_field(name="Members",value=f"{member_list}",inline=True)
    await ctx.respond(embed=embed)
    
@plugin.command()
@lightbulb.option('member','mention the member to deafen them',required=True,type=hikari.Member)
@lightbulb.command('deafen','Deafens The Member In The Guild',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def deafen(ctx:lightbulb.Context) -> None:
    await ctx.options.member.edit(mute=True,deaf=True)
    embed = hikari.Embed(title="Deafen",color=(0,255,255))
    embed.add_field(name="\u200b",value=f"{ctx.options.member.username}#{ctx.options.member.discriminator} was deafned")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option('member','mention the member to deafen them',required=True,type=hikari.Member)
@lightbulb.command('undeafen','Deafens The Member In The Guild',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def undeafen(ctx:lightbulb.Context) -> None:
    await ctx.options.member.edit(mute=False,deaf=False)
    embed = hikari.Embed(title="Undeafen",color=(0,255,255))
    embed.add_field(name="\u200b",value=f"{ctx.options.member.username}#{ctx.options.member.discriminator} was undeafned")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option('duration','duration to mute member for in hour:minute:second format',required=True,type=str)
@lightbulb.option('member','mention the member to temporary mute them',required=True,type=hikari.Member)
@lightbulb.command('tempmute','Mutes member temporarily for the speecified duration',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def tempmute(ctx:lightbulb.Context) -> None:
    second=minute=hour= 0
    format = "%H:%M:%S"
    embed = hikari.Embed(title="TempMute",color=(0,255,255))
    try:
        datetime_obj = datetime.strptime(ctx.options.duration, format)
        time = datetime_obj.time()
        hour = int(time.hour)
        second = int(time.second)
        minute = int(time.minute)
        await ctx.options.member.edit(communication_disabled_until=datetime.now(tzutc()).astimezone(tzlocal()) + timedelta(hours=hour,minutes=minute,seconds=second))
        embed.add_field(name="TempMute Description",value=f"Temporarily Muted {ctx.options.member.username}#{ctx.options.member.discriminator} For {ctx.options.duration}")
        row = ctx.app.rest.build_action_row().add_button(hikari.ButtonStyle.DANGER,"unmute").set_label("unmute").add_to_container()
        await ctx.respond(embed=embed,component=row)
    except ValueError:
        embed.add_field(name="TempMute Description",value="Invalid duration. Please provide a valid duration in the form Hour:Minute:Second")
        await ctx.respond(embed=embed)
    event = await ctx.app.wait_for(hikari.InteractionCreateEvent,60,lambda event : event.interaction != hikari.ComponentInteraction)
    if event.interaction.custom_id == "unmute":
        embed.edit_field(0,f"{ctx.options.member.username}#{ctx.options.member.discriminator} is now unmuted","\u200b")
        await ctx.options.member.edit(communication_disabled_until=None)
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,component=None,embed=embed)

@plugin.command()
@lightbulb.option('reason','reason to temporary ban member from the server',type=str,required=False,modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.option('duration','duration to ban member from server in hour:minute:second or in days format',required=True,type=str)
@lightbulb.option('member','mention the member to temporary ban them',required=True,type=hikari.Member)
@lightbulb.command('tempban',"Temporarily Ban Member From The Server",auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def tempban(ctx:lightbulb.Context) -> None:
    duration = 0
    embed = hikari.Embed(title="Temp Ban",color=(0,255,255))
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cursor:
            server_name = str(ctx.get_guild().name)[0] + str(ctx.guild_id)
            try:
                datetime_obj = datetime.strptime(ctx.options.duration, "%H:%M:%S")
                time = datetime_obj.time()
                duration =  int(time.hour*3600)+int(time.minute*60)+int(time.second)
                embed.add_field(name=f"{ctx.options.member.username} has been temporarily banned from the server for {ctx.options.duration} due to {ctx.options.reason}",value="\u200b")
                await ctx.respond(embed=embed)
                embed.edit_field(0,f"{ctx.options.member.username} you have been temporarily banned from the {ctx.get_guild().name} for {ctx.options.duration} due to {ctx.options.reason}","\u200b")
                await ctx.options.member.send(embed=embed)
                await cursor.execute(f"DELETE FROM {server_name} WHERE Member_id = {ctx.options.member.id}")
                row = [ctx.guild_id,ctx.options.member.id,duration]
                with open('tempban.csv','w') as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerow(row)
                await ctx.app.rest.ban_user(ctx.guild_id,ctx.options.member.id,reason=str(ctx.options.reason))
            except:
                try:
                    duration = int(ctx.options.duration)*86400
                    embed.add_field(name=f"{ctx.options.member.username} has been temporarily banned from the server for {ctx.options.duration} day due to {ctx.options.reason}",value="\u200b")
                    await ctx.respond(embed=embed)
                    embed.edit_field(0,f"{ctx.options.member.username} you have been temporarily banned from the {ctx.get_guild().name} for {ctx.options.duration} due to {ctx.options.reason}","\u200b")
                    await ctx.options.member.send(embed=embed)
                    await cursor.execute(f"DELETE FROM {server_name} WHERE Member_id = {ctx.options.member.id}")
                    row = [ctx.guild_id,ctx.options.member.id,duration]
                    with open('tempban.csv','w') as f:
                        csvwriter = csv.writer(f)
                        csvwriter.writerow(row)
                    await ctx.app.rest.ban_user(ctx.guild_id,ctx.options.member.id,reason=str(ctx.options.reason))
                except:
                    await ctx.respond("enter duration in valid format")
        await db.commit()

'''@tasks.task(m=1,auto_start=True)
async def tempunban() -> None:
    with open('tempban.json','r') as f:
       ban = dict(json.load(f))
    if len(ban) != 0:    
        for a in ban.values():
            if a[2] == 0:
                await plugin.app.rest.unban_user(int(a[1]),int(a[0]))
        with open('tempban.json','w') as f:
            for a in ban.keys():
                value=ban.get(a)
                value[2] = int(value[2])-60
                if(value[2]<0):
                    value[2]=0
                    ban[a]=(value)
                    json.dump(ban,f)
                else:
                    ban[a]=(value)
                    json.dump(ban,f)
'''        
def load(lucario:lightbulb.BotApp):
    lucario.add_plugin(plugin)
    
def unload(lucario:lightbulb.BotApp):
    lucario.remove_plugin(plugin)