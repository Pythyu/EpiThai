# Work with Python 3.6
import discord
import datetime
import time
usleep = lambda x: time.sleep(x/1000000.0)
import os

# Update discord.py : py -3 -m pip install -U discord.py

# TOKEN = 'SECRET'
TOKEN = os.getenv('DISCORD_TOKEN', "SECRET")

EQ = {'Uni_Mahidol':"Mahidol",'Uni_Kingmongkut':"KMUTT",'Uni_Chula':"Chulalongkorn"}
promo_emojis = {"2022": "2022", "2023": "2023", "2024": "2024"}
waitingSubscriptionRole = "En attente d'inscription"
adminIDs = {"248459095512842241": "Antoine", "328484154444480513": "Charles", "368792646350667789": "Tao"}

class Logs:
    def __init__(self, file=None):
        self.file = file
       
    def write(self, s):
        print(s, end="")

    def close(self):
        return 0

DEBUG_MODE = True #Ajout d'un debug mode
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

def user_is_ready_to_access_discord(user):
    # choosen = {"univ": False, "promo": False}
    # for e, role in EQ.items():
    #     if(discord.utils.get(user.roles, name=role)):
    #         choosen["univ"] = True
    #         break
    # for e, role in promo_emojis.items():
    #     if(discord.utils.get(user.roles, name=role)):
    #         choosen["promo"] = True
    #         break
    # return choosen["univ"] and choosen["promo"]
    return userHasAlreadyChoosenUniv(user) and userHasAlreadyChoosenPromo(user)

def user_is_admin(user):
    return str(user.id) in adminIDs

def rolesListToSTRList(list, sep):
    s = ""
    if(len(list) < 1):
        return []
    s = list[0].name
    for i in range(1, len(list)):
        s += sep + list[i].name
    return s

def userHasAlreadyChoosenUniv(user, role=None, result={}):
    alreadyChoosen = False
    for em, role_name in EQ.items():
        if discord.utils.get(user.roles, name=role_name) and (not role or role != role_name):
            alreadyChoosen = True
            result["univ"] = role_name
            break
    return alreadyChoosen

def userHasAlreadyChoosenPromo(user, role=None, result={}):
    alreadyChoosen = False
    for em, role_name in promo_emojis.items():
        if discord.utils.get(user.roles, name=role_name) and (not role or role != role_name):
            alreadyChoosen = True
            result["promo"] = role_name
            break
    return alreadyChoosen

async def sendDM(user, msg):
    chn = user.dm_channel if user.dm_channel else await user.create_dm()
    await chn.send(msg)

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('||ping_bot') and user_is_admin(message.author):
        msg = 'Pong ! {0.author.mention}'.format(message)
        return await message.channel.send(msg)
    elif message.content.startswith('||bot_shutdown') or message.content.startswith("/") and user_is_admin(message.author):
        channel = discord.utils.get(client.get_all_channels(), name='inscriptions')
        await channel.purge(limit=1000, check=absolute)
        msg = 'As {0.author.mention} told me, I am shutting down...'.format(message)
        await message.channel.send(msg)
        return await client.logout()
    elif message.content.startswith("!clean_user_roles") and user_is_admin(message.author):
        if len(message.mentions) == 0:
            return
        for mention in message.mentions:
            roles = mention.roles
            # dpName = mention.display_name
            msg = mention.mention + " avait pour rôles ```" + rolesListToSTRList(roles, ", ") + "```Ils ont tous été supprimés."
            roles = [discord.utils.get(mention.guild.roles, name=waitingSubscriptionRole)]
            await mention.edit(roles=roles, reason="Command for auto-deleting all roles")
            return await message.channel.send(msg)
    elif message.channel.name == "inscriptions":
        return await message.delete()

    elif message.content.startswith("!"):
        spl = message.content.split(" ")
        cmd = spl[0][1:]
        args = spl[1:]


@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=waitingSubscriptionRole)
    Log.write(format_time()+" >>> User "+str(member.nick)+" join the server, he gain the role : En attente d'inscription\n")
    await member.add_roles(role)


@client.event
async def on_reaction_add(reaction, user):

    if user == client.user: #On ne veux pas que le bot réagisse à ses propres réactions
        return
    
    try:
        if user_is_ready_to_access_discord(user):
            return await reaction.message.remove_reaction(reaction, user)

        val = reaction.message.channel.name
        em = reaction.emoji if type(reaction.emoji) is str else reaction.emoji.name.encode('utf-8').decode('utf-8') #can crash for non-custom emoji c'est la raison du try except
        if val  == "inscriptions":
            if em in EQ: # Univ emoji
                univ = EQ[em]

                result = {}
                if(userHasAlreadyChoosenUniv(user, univ, result)):
                    await sendDM(user, "======== EPITA - Thaïlande ========\nVous ne pouvez pas choisir plus d'une université ! Vous avez déjà choisi l'université suivante :```" + result["univ"] + "```\nPour modifier votre choix, contactez un administrateur.")
                    return await reaction.message.remove_reaction(reaction, user)

                role = discord.utils.get(reaction.message.guild.roles, name=univ)
                Log.write(format_time()+" >>> User "+str(user.name)+" choosed university "+univ+" \n")
            elif em in promo_emojis:
                promo = promo_emojis[em]

                result = {}
                if(userHasAlreadyChoosenPromo(user, promo, result)):
                    await sendDM(user, "======== EPITA - Thaïlande ========\nVous ne pouvez pas vous attribuer plusieurs promotions ! Vous avez déjà choisi la promotion suivante :```" + result["promo"] + "```\nPour modifier votre choix, contactez un administrateur.")
                    return await reaction.message.remove_reaction(reaction, user)

                role = discord.utils.get(reaction.message.guild.roles, name=promo)
                Log.write(format_time()+" >>> User "+str(user.name)+" choosed promo "+promo+" \n")
            else:
                return await reaction.message.remove_reaction(reaction, user)
            # await reaction.message.remove_reaction(reaction, user)

            await user.add_roles(role)
            await sendDM(user, "======== EPITA - Thaïlande ========\nVous avez reçu le rôle```" + role.name + "```")
            usleep(50)

            if user_is_ready_to_access_discord(user):
                await sendDM(user, "======== EPITA - Thaïlande ========\n```Vous avez désormais accès à l'ensemble du serveur !```")
                # Remove temp role
                await user.remove_roles(discord.utils.get(reaction.message.guild.roles, name=waitingSubscriptionRole))
                # Remove all reactions on initial post from this user
                await reaction.message.remove_reaction(reaction, user)
                for _reac in reaction.message.reactions:
                    async for _user in _reac.users():
                        if _user == user: await reaction.message.remove_reaction(_reac, _user)
            """
            try:
                # univ = EQ[em.decode('utf-8')]
                # role = discord.utils.get(reaction.message.guild.roles, name=univ)
                # Log.write(format_time()+" >>> User "+str(user.name)+" choosed university "+univ+" \n")
                # await user.add_roles(role)

                # if user_is_ready_to_access_discord(user):
                    # await user.remove_roles(discord.utils.get(reaction.message.guild.roles, name=waitingSubscriptionRole))
            except Exception as e:  # if it crash for some reason
                if DEBUG_MODE:
                    Log.write(format_time()+" >>> [ERROR] EXCEPTION into inscriptions channel : "+str(e)+"\n")
                else:
                    pass
            """
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
    Log.write(format_time() + " >>> STARTED !\n")

    channel = discord.utils.get(client.get_all_channels(), name='inscriptions')
    deleted = await channel.purge(limit=1000, check=absolute)
    # Pour l'instant message écris en dur, dès que j'ai un peu de temps j'applique l'idée de Charle || /!\ Ne pas supprimer la valeur en string des emoji, chiante à retrouver ||
    msg = """Choisir son Université >=\n"""
    for em_name, em_dp_name in EQ.items():
        msg += "\n   <:" + em_name + ":" + str(discord.utils.get(client.emojis, name=em_name).id) + ">   => " + em_dp_name + "\n"

    msg += "\n\nChoisir sa promotion >=\n"
    for em_name, em_dp_name in promo_emojis.items():
        msg += "\n   <:" + em_name + ":" + str(discord.utils.get(client.emojis, name=em_name).id) + ">   => " + em_dp_name + "\n"
    
    initialMessage = await channel.send(msg)

    for emoji_name in EQ:
        emoji = discord.utils.get(client.emojis, name=emoji_name)
        await initialMessage.add_reaction(emoji)

    for emoji_name in promo_emojis:
        emoji = discord.utils.get(client.emojis, name=emoji_name)
        await initialMessage.add_reaction(emoji)

client.run(TOKEN)