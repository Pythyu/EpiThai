# Work with Python 3.6
import discord
import os

# TOKEN = 'SECRET'
TOKEN = os.getenv('DISCORD_TOKEN', "SECRET")

EQ = {'Uni_Mahidol':"Mahidol",'Uni_Kingmongkut':"KMUTT",'Uni_Chula':"Chulalongkorn"}

DEBUG_MODE = False #Ajout d'un debug mode

client = discord.Client()
initialMessage = None;

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

    if user == client.user: #On ne veux pas que le bot réagisse à ses propres réactions
        return
    
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
    # print(client.user)
    print(client.user.name.encode('utf-8'))
    print(client.user.id)
    print('------')


    channel = discord.utils.get(client.get_all_channels(), name='inscriptions')
    deleted = await channel.purge(limit=1000, check=absolute)
    # Pour l'instant message écris en dur, dès que j'ai un peu de temps j'applique l'idée de Charle || /!\ Ne pas supprimer la valeur en string des emoji, chiante à retrouver ||
    msg = """Choisir son Université >=\n"""
    for em_name, em_dp_name in EQ.items():
        msg += "\n   <:" + em_name + ":" + str(discord.utils.get(client.emojis, name=em_name).id) + ">   => " + em_dp_name + "\n"
    initialMessage = await channel.send(msg)

    for emoji_name in EQ:
        emoji = discord.utils.get(client.emojis, name=emoji_name)
        await initialMessage.add_reaction(emoji)

client.run(TOKEN)
