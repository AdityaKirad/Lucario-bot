import hikari

import lightbulb

from lightbulb.ext import tasks

import logging

import os

from dotenv import load_dotenv

import aiosqlite

import asyncio

load_dotenv()

TOKEN = os.getenv("TOKEN")

async def get_prefix(lucario,message):
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cursor:
           await cursor.execute(f"SELECT Server_Prefix FROM SERVERINFORMATION WHERE Server_Id = {message.guild_id}")
           prefix = await cursor.fetchone()
           if len(prefix) == 0:
               prefix = '?'
           else:
               prefix =prefix[0]
    return prefix 

lucario = lightbulb.BotApp(token=TOKEN,prefix=get_prefix,case_insensitive_prefix_commands=True,intents=hikari.Intents.ALL,help_class=None)

@lucario.listen(hikari.StartedEvent)
async def on_start(event):
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS SERVERINFORMATION(
        Server_Name Text,
        Server_Id INTEGER PRIMARY KEY,
        Server_Prefix TEXT,
        Welcome_channel INTEGER,
        Leave_channel INTEGER
        )''')
        await db.commit()
    print('Lucario Bot Has Started')
    
@lucario.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    embed = hikari.Embed(title="Command Invocation Error",color=(0,255,255))
    if isinstance(event.exception,lightbulb.CommandInvocationError):
        embed.add_field(name=f"Something Went During Invocation Of Command `{event.context.command.name}`.",value="\u200b")
        await event.context.respond(embed=embed)
        raise event.exception
    
    exception = event.exception.__cause__ or event.exception
    
    if isinstance(exception,lightbulb.MissingRequiredPermission):
        embed.add_field(name="You Do Not Have The Required Permission To Use This Command",value="\u200b")
        await event.context.respond(embed=embed)
    else:
        raise exception

@lucario.command
@lightbulb.command('hello',"Says Hey I'm The Lucario Bot")
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def hello(ctx:lightbulb.Context):
    print(ctx.guild_id)
    embed = hikari.Embed(title="Hello",color=(0,255,255))
    embed.add_field(name="Hey I'm The Lucario Bot",value="\u200b")
    embed.set_thumbnail(ctx.author.display_avatar_url)
    await ctx.respond(embed)
    await ctx.respond()
    
@lucario.listen(hikari.GuildMessageCreateEvent)
async def on_message(event:hikari.GuildMessageCreateEvent) -> None:
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cursor:
           await cursor.execute(f"SELECT Server_Prefix FROM SERVERINFORMATION WHERE Server_Id = {event.guild_id}")
           prefix = await cursor.fetchone()
           if len(prefix) == 0:
               prefix = '?'
           else:
               prefix =prefix[0]
    if event.message.content == "<@961965367767470171>":
        embed = hikari.Embed(title="\u200b",color=(0,255,255))
        embed.add_field(name=f"Hey How You Doing My Prefix For Your Server Is {prefix}\nlatency : {lucario.heartbeat_latency * 1_000:,.0f} ms.",value="\u200b")
        await event.app.rest.create_message(event.channel_id,embed=embed)
    
@lucario.command
@lightbulb.command("help","Gets Help For Bot Commands")
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def help(ctx:lightbulb.Context) -> None:
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cursor:
           await cursor.execute(f"SELECT Server_Prefix FROM SERVERINFORMATION WHERE Server_Id = {ctx.guild_id}")
           prefix = await cursor.fetchone()
           if len(prefix) == 0:
               prefix = '?'
           else:
               prefix =prefix[0]
    embed = hikari.Embed(title="Help",color=(0,255,255))
    embed.add_field(name="Lucario Plugin Commands",value="\u200b")
    selections = ["Welcome And Leave","Moderation","DirectMessage"]
    select_menu = (
        lucario.rest.build_action_row()
        .add_select_menu("Help Command")
        .set_placeholder("Make An Selection")
        )
    for selection in selections:
        select_menu.add_option(selection,selection.lower()).add_to_menu()
    resp = await ctx.respond(embed=embed,component=select_menu.add_to_container(),)
    msg = await resp.message()
    try:
        event = await lucario.wait_for(
            hikari.InteractionCreateEvent,
            timeout=60,
            predicate=lambda e:
                isinstance(e.interaction,hikari.ComponentInteraction)
                and e.interaction.user.id == ctx.author.id
                and e.interaction.message.id == msg.id
                and e.interaction.component_type == hikari.ComponentType.SELECT_MENU
                )
    except asyncio.TimeoutError:
        await msg.edit("the Menu Timed Out :c",components=[])
    else:
        if event.interaction.values[0] == "welcome and leave":
            embed.edit_field(0,f"```{prefix}setwelcomechannel [channel]```\n```/setwelcomechannel [channel]```","Sets The Welcome Channel For Guild")
            embed.add_field(name=f"```{prefix}setleavechannel [channel]```\n```/setleavechannel [channel]```",value="Sets The Leave Channel For Guild")
            await msg.edit(f"Here Is The Help Command For {event.interaction.values[0]}",embed=embed,components=[])
        elif event.interaction.values[0] == "moderation":
            embed.edit_field(0,f"```{prefix}kick [member] (optional reason)```\n```/kick [member] (optional reason)```","Kick A Member From The Server")
            embed.add_field(name=f"```{prefix}ban [member] (optional reason)```\n```/ban [member] (optional reason)```",value="Ban A Member From The Server")
            embed.add_field(name=f"```{prefix}unban [member] (optional reason)```\n```/unban [member] (optional reason)```",value="UnBan A Member From The Server")
            embed.add_field(name=f"```{prefix}mute [member] (optional reason)```\n```/mute [member] (optional reason)```",value="Mute A Member In The Server")
            embed.add_field(name=f"```{prefix}unmute [member] (optional reason)```\n```/unmute [member] (optional reason)```",value="UnMute A Member In The Server")
            embed.add_field(name=f"```{prefix}warn [member] (optional reason)```\n```/warn [member] (optional reason)```",value="Warn A Member In The Server")
            embed.add_field(name=f"```{prefix}clear_infractions [member]```\n```/clear_infractions [member]```",value="Clears All Infractions Of Member In The Server")
            embed.add_field(name=f"```{prefix}infractions [member]```\n```/infractions [member]```",value="Shows Infractions For A Member In The Server")
            embed.add_field(name=f"```{prefix}setprefix [prefix]```\n```/setprefix [prefix]```",value="Sets Prefix For The Server")
            embed.add_field(name=f"```{prefix}user_info [member]```\n```/user_info [member]```",value="Gets Member Information")
            embed.add_field(name=f"```{prefix}server_info```\n```/server_info```",value="Gets Information About The Server")
            embed.add_field(name=f"```{prefix}role_info [role]```\n```/role_info [role]```",value="Gets Information About A Role")
            embed.add_field(name=f"```{prefix}slowmode (timeout [Hour:Minute:Second] or state [off])```\n```/slowmode (timeout [Hour:Minute:Second] or state [off])```",value="Enable/Disable Slowmode In The Channel")
            embed.add_field(name=f"```{prefix}clear [amount] (optional member)```\n```/clear [amount] (optional member)```",value="Delets Channel Messages")
            embed.add_field(name=f"```{prefix}members [role]```\n```/members [role]```",value="Gets The List Of Member With Specified Role")
            embed.add_field(name=f"```{prefix}deafen [member]```\n```/deafen [member]```",value="Deafen The Specified Member")
            embed.add_field(name=f"```{prefix}undeafen [member]```\n```/undeafen [member]```",value="Undeafen The Specified Member")
            embed.add_field(name=f"```{prefix}tempmute [member] [duration]```\n```/tempmute [member] [duration]```",value="Temporarily Mutes The Specified Member")
            embed.add_field(name=f"```{prefix}tempban [member] [duration] (optional reason)```\n```/tempban [member] [duration] (optional reason)```",value="Temporarily Bans Specified Member")
            await msg.edit(f"Here Is The Help Command For {event.interaction.values[0]}",embed=embed,components=[])
        elif event.interaction.values[0] == "directmessage":
            embed.edit_field(0,f"```{prefix}dm [member] [message]```\n```/dm [member] [message]```","Sends A Direct Message To The Specified User")
            embed.add_field(name=f"```{prefix}announce [role] [message]```\n```/announce [role] [message]```",value="Sends The Direct Message To The Members With Specified Role")
            await msg.edit(f"Here Is The Help Command For {event.interaction.values[0]}",embed=embed,components=[])

tasks.load(lucario)

lucario.load_extensions_from("./extensions")

@tasks.task(m=2,auto_start=True)
async def extension_reload() -> None:        
    for filename in os.listdir("./extensions"):
        if filename.endswith('.py'):
            lucario.reload_extensions(f'extensions.{filename[:-3]}')

lucario.run(asyncio_debug=True,
            coroutine_tracking_depth=20,
            propagate_interrupts=True)