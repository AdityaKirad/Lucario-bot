import hikari

import lightbulb

import aiosqlite

plugin = lightbulb.Plugin("Welcome_Leave")

@plugin.listener(hikari.GuildJoinEvent)
async def on_guild_join(event:hikari.GuildJoinEvent):
    id = event.guild_id
    name = str(event.guild)
    name_a = str(name)[0]+str(id)
    welcome_channel = event.guild.get_channels()
    j = 0
    for i in dict(welcome_channel):
        if j==2:
            welcome_channel = i
        j+=1

    leave_channel = welcome_channel
    sqla = "INSERT INTO SERVERINFORMATION(Server_Name,Server_Id,Server_Prefix,Welcome_channel,Leave_channel) VALUES(?,?,?,?,?)"
    VAL = (name,id,"?",welcome_channel,leave_channel)
    members = event.guild.get_members()
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {name_a}(Member_name TEXT,Member_id INTEGER PRIMARY KEY,Member_Discriminiator INTEGER,Warns INTEGER)")
            await cursor.execute(sqla,VAL)
            for i in dict(members).values():
                if i.is_bot==False:
                    sql = f"INSERT INTO {name_a}(Member_name,Member_id,Member_Discriminiator,Warns) VALUES(?,?,?,?)"
                    val = (i.display_name,i.id,i.discriminator,0)
                    await cursor.execute(sql,val)
        await db.commit()

@plugin.listener(hikari.GuildLeaveEvent)
async def on_guild_leave(event:hikari.GuildLeaveEvent):
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        cur = await db.execute(f"SELECT Server_Name FROM SERVERINFORMATION WHERE Server_Id = {event.guild_id}")
        name = await  cur.fetchone()
        name = name[0]
        name = name[0]
        table_name = str(name)+str(event.guild_id)
        await db.execute(f"DROP TABLE {table_name}")
        await db.execute(f"DELETE FROM SERVERINFORMATION WHERE Server_Id = {event.guild_id}")
        await db.commit()

@plugin.command()
@lightbulb.option("channel","mention the channel for setting the welcome channel",type = hikari.TextableGuildChannel)
@lightbulb.command('setwelcomechannel','Sets Welcome Channel')
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def setwelcomechannel(ctx: lightbulb.Context) -> None:
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        await db.execute(f"UPDATE SERVERINFORMATION SET Welcome_channel = {ctx.options.channel.id} WHERE Server_Id = {ctx.guild_id}")
        await db.commit()
    await ctx.respond(f"{ctx.options.channel.name} has been set as welcome channel")

@plugin.command()
@lightbulb.option("channel","mention the channel for setting the leave channel",type = hikari.TextableGuildChannel)
@lightbulb.command('setleavechannel','Sets Leave Channel')
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def setleavechannel(ctx: lightbulb.Context) -> None:
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        await db.execute(f"UPDATE SERVERINFORMATION SET Leave_channel = {ctx.options.channel.id} WHERE Server_Id = {ctx.guild_id}")
        await db.commit()
    await ctx.respond(f"{ctx.options.channel.name} has been set as leave channel")

@plugin.listener(hikari.MemberCreateEvent)
async def on_member_join(event:hikari.MemberCreateEvent):
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cursor:
            a = await cursor.execute(f"SELECT Server_Name,Welcome_channel FROM SERVERINFORMATION WHERE Server_Id = {event.guild_id}")
            a = await cursor.fetchone()
            server_name = str(a[0])
            server_name = str(server_name)[0]+str(event.member.guild_id)
            sql = f"INSERT INTO {server_name}(Member_name,Member_id,Member_Discriminiator,Warns) VALUES(?,?,?,?)"
            val = (event.member.display_name,event.member.id,event.member.discriminator,0)
            await cursor.execute(sql,val)
            await event.app.rest.create_message(a[1],f"Welcome To The Server {event.member.mention}")
            await event.member.send(f"Welcome {event.member.display_name} to the {event.member.get_guild().name}")
        await db.commit()

@plugin.listener(hikari.MemberDeleteEvent)
async def on_member_leave(event:hikari.MemberDeleteEvent):
    async with aiosqlite.connect('lucariobotdb.sqlite') as db:
        async with db.cursor() as cursor:
            a = await cursor.execute(f"SELECT Server_Name,Leave_channel FROM SERVERINFORMATION WHERE Server_Id = {event.guild_id}")
            a = await cursor.fetchone()
            server_name = str(a[0])
            server_name = str(server_name)[0]+str(event.guild_id)
            await event.app.rest.create_message(a[1],f"{event.user} Just Left The Server")
            await cursor.execute(f"DELETE FROM {server_name} WHERE Member_id = {event.user_id}")
        await db.commit()
                

def load(lucario:lightbulb.BotApp):
    lucario.add_plugin(plugin)
    
def unload(lucario:lightbulb.BotApp):
    lucario.remove_plugin(plugin)



