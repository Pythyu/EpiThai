# Work with Python 3.6
import discord
import datetime
import os

# TOKEN = 'SECRET'
TOKEN = os.getenv('DISCORD_TOKEN', "SECRET")

EQ = {'Uni_Mahidol':"Mahidol",'Uni_Kingmongkut':"KMUTT",'Uni_Chula':"Chulalongkorn"}
waitingSubscriptionRole = "En attente d'inscription"

class Logs:
    def __init__(self, file=None):
        self.file = file
       
    def write(self, s):
        print(s, end="")

DEBUG_MODE = False #Ajout d'un debug mode
# Log = open("log.txt","a") #Log file
Log = Logs()

client = discord.Client()
initialMessage = None;

def absolute(m):
    return True

def format_time():
    t = datetime.datetime.now()
    s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
    return s[:-7]

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('||ping_bot'):
        msg = 'Pong ! {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
    elif message.content.startswith('||bot_shutdown'):
        await client.logout()
    elif message.channel.name == "inscriptions":
        await message.delete()

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=waitingSubscriptionRole)
    Log.write(format_time()+" >>> User "+str(member.nick)+" join the server, he gain the role : En attente d'inscription\n")
    await member.add_roles(role)

def user_is_ready_to_access_discord(user):
    return True

@client.event
async def on_reaction_add(reaction, user):

    if user == client.user: #On ne veux pas que le bot réagisse à ses propres réactions
        return
    
    try:
        val = reaction.message.channel.name
        em = reaction.emoji.name.encode('utf-8') #can crash for non-custom emoji c'est la raison du try except
        if val  == "inscriptions":
            try:
                univ = EQ[em.decode('utf-8')]
                role = discord.utils.get(reaction.message.guild.roles, name=univ)
                Log.write(format_time()+" >>> User "+str(user.name)+" choosed university "+univ+" \n")
                await user.add_roles(role)
                if user_is_ready_to_access_discord(user):
                    user.remove_roles(discord.utils.get(reaction.message.guild.roles, name=waitingSubscriptionRole))
            except Exception as e:  # if it crash for some reason
                if DEBUG_MODE:
                    Log.write(format_time()+" >>> [ERROR] EXCEPTION into inscriptions channel : "+str(e)+"\n")
                else:
                    pass
    except Exception as e:
        if DEBUG_MODE:
            Log.write(format_time()+" >>> [ERROR] EXCEPTION : "+str(e)+"\n")
        else:
            pass

@client.event
async def on_disconnect():
    Log.write("=========== Shuting down ... ===========\n")
    Log.close()
    

@client.event
async def on_ready():
    Log.write("=========== Starting ... ===========\n")
    print('Logged in as')
    # print(client.user)
    print(client.user.name.encode('utf-8'))
    print(client.user.id)
    print('------')
    Log.write(format_time()+" >>> STARTED !")

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
