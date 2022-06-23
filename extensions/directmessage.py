import hikari

import lightbulb

import time

plugin = lightbulb.Plugin("DirectMessage","Commands To Send The DirectMessage Through Bot")

@plugin.command()
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR|hikari.Permissions.MODERATE_MEMBERS|hikari.Permissions.MANAGE_CHANNELS|hikari.Permissions.MANAGE_GUILD))
@lightbulb.option('message','write the message to send in dm',type=str,required=True,modifier=lightbulb.OptionModifier.CONSUME_REST,default="This Message Is Sent Via DM")
@lightbulb.option('user','mention the user to dm them',type=hikari.Member,required=True)
@lightbulb.command('dm','Sends DM To The Server Member',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def dm(ctx:lightbulb.Context) -> None:
    embed = hikari.Embed(title="Direct Message",color=(0,255,255))
    message = ctx.options.message
    await ctx.options.user.send('{} : {}'.format(ctx.author,message))
    embed.add_field(name=f"DM Sent To {ctx.options.user}",value="\u200b")
    await ctx.respond(embed=embed)
    
@plugin.command()
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR|hikari.Permissions.MODERATE_MEMBERS|hikari.Permissions.MANAGE_CHANNELS|hikari.Permissions.MANAGE_GUILD|hikari.Permissions.MANAGE_ROLES))
@lightbulb.option('message','write the message to send in dm',type=str,required=True,modifier=lightbulb.OptionModifier.CONSUME_REST,default="This Message Is Sent Via DM")
@lightbulb.option('role','mention the role to send the message to the members with that role',type=hikari.Role,required=True)
@lightbulb.command('announce','Sends DM To The Multiple User',auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand,lightbulb.SlashCommand)
async def announce(ctx:lightbulb.Context) -> None:
    members = [m for m in ctx.get_guild().get_members().values() if ctx.options.role.id in m.role_ids if m.is_bot == False]
    n = 100
    sent,unsent=0,0
    message = ctx.options.message
    members_final = [members[i*n:(i+1)*n] for i in range((len(members)+n-1)//n)]
    embed = hikari.Embed(title="Direct Message",color=(0,255,255))
    for x in range(len(members_final)):
        for a in members_final[x]:
            try:
                await a.send('{} : {}'.format(ctx.author,message))
                sent+=1
            except:
                unsent+=1
        time.sleep(10)
    embed.add_field(name=f"DM Sent To {sent} Users And Not Sent To {unsent} Users",value="\u200b")
    await ctx.respond(embed=embed)
def load(lucario:lightbulb.BotApp):
    lucario.add_plugin(plugin)
    
def unload(lucario:lightbulb.BotApp):
    lucario.remove_plugin(plugin)