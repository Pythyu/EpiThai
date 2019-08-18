# Work with Python 3.6
import discord

TOKEN = 'NjExNTk5NjQxNzI0NTgzOTU2.XVinlw.5LTcYwPwLI2biZHDGxkjNzbGUsY'

EQ = {'Uni_Mahidol':"Mahidol",'Uni_Kingmongkut':"KMUTT",'Uni_Chula':"Chulalongkorn"}

DEBUG_MODE = False #Ajout d'un debug mode

client = discord.Client()

def absolute(m):
    return True

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('||ping_bot'):
        msg = 'Pong ! {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
    elif message.channel.name == "inscriptions":
        await message.delete()

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="En attente d'inscription")
    await member.add_roles(role)



@client.event
async def on_reaction_add(reaction, user):
    
    try:
        val = reaction.message.channel.name
        em = reaction.emoji.name.encode('utf-8') #can crash for non-custom emoji c'est la raison du try except
        if val  == "inscriptions":
            try:
                role = discord.utils.get(reaction.message.guild.roles, name=EQ[em.decode('utf-8')])
                await user.add_roles(role)
            except Exception as e:  # if it crash for some reason
                if DEBUG_MODE:
                    print(e)
                else:
                    pass
    except Exception as e:
        if DEBUG_MODE:
            print(e)
        else:
            pass
    

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
    
    
    channel = discord.utils.get(client.get_all_channels(), name='inscriptions')
    deleted = await channel.purge(limit=1000, check=absolute)
    # Pour l'instant message écris en dur, dès que j'ai un peu de temps j'applique l'idée de Charle || /!\ Ne pas supprimer la valeur en string des emoji, chiante à retrouver ||
    msg = """Choisir son Université =>\n
        <:Uni_Mahidol:611611594199400468>   => Mahidol\n
        <:Uni_Kingmongkut:611611513404522507>  => KMUTT\n
        <:Uni_Chula:611611315345293312>  => Chulalongkorn"""
    await channel.send(msg)

client.run(TOKEN)
