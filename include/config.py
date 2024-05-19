from datetime import datetime
import croniter
import discord
import requests
import dotenv
import time
import json
import re

env = dotenv.dotenv_values('./resources/.env')

def generate_cron():
    schedule_data = read_config_file('stored_values')
    frequency = schedule_data['frequency']
    day = schedule_data['day']
    day = time.strptime(day.lower(),'%A').tm_wday + 1
    hour = schedule_data['hour']
    minute = schedule_data['minute']
    am_pm = schedule_data['am_pm']
    if str(am_pm.upper()) == 'PM':
        hour = int(hour) + 12
    cron = f'{str(minute)} {str(hour)} * * {str(day)}'
    return cron

def edit_stored_values(item,value):
    config = read_config_file('stored_values')
    config[item] = value
    write_config_file('stored_values',config)
    
def clear_stored_values():
    config = read_config_file('stored_values')
    for key,value in config.items():
        config[key] = ''
    write_config_file('stored_values',config)

def read_config_file(name):
    return json.loads(open(f'./config/{name}.json').read())

def write_config_file(name,data):
    with open(f'./config/{name}.json','w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

def server_check(guild_id):
    config = read_config_file('servers')
    server_check = [x for x in config['servers'] if x['serverId'] == guild_id]
    if len(server_check) == 0:
        return False
    else:
        return True
    
def add_server(serverId,serverName,registeredBy,dateRegistered):
    config = read_config_file('servers')
    entry = {
        "serverId":serverId,
        "serverName":serverName,
        "registeredBy":registeredBy,
        "dateRegistered":dateRegistered,
        "leaguesAdded":[]
    }
    config['servers'].append(entry)
    write_config_file('servers',config)

def remove_server(serverId):
    config = read_config_file('servers')
    ix = 0
    for i in config['servers']:
        if i['serverId'] == serverId:
            del config['servers'][ix]
            break
        else:
            ix += 1
            continue
    write_config_file('servers',config)
    
def league_check(serverId,name):
    config = read_config_file('servers')
    server_record = [x for x,item in enumerate(config['servers']) if item['serverId'] == serverId]
    league_record = [x for x in config['servers'][server_record[0]]['leaguesAdded'] if x['leagueName'] == name]
    if len(league_record) == 0:
        return False
    else:
        return True

def add_league(serverId,leagueName,addedBy,dateAdded):
    config = read_config_file('servers')
    server_record = [x for x,item in enumerate(config['servers']) if item['serverId'] == serverId]
    entry = {
        "leagueName":leagueName,
        "channel":"",
        "addedBy":addedBy,
        "dateAdded":dateAdded,
        "tierRoles":[],
        "teamRoles":[],
        "schedule":""
    }
    config['servers'][server_record[0]]['leaguesAdded'].append(entry)
    write_config_file('servers',config)

def add_channel(serverId,leagueName,channelName):
    config = read_config_file('servers')
    server_record = [x for x,item in enumerate(config['servers']) if item['serverId'] == serverId]
    league_record = [x for x,item in enumerate(config['servers'][server_record[0]]['leaguesAdded']) if item['leagueName'] == leagueName]
    config['servers'][server_record[0]]['leaguesAdded'][league_record[0]]['channel'] = channelName
    write_config_file('servers',config)

def add_schedule(serverId,league,data):
    config = read_config_file('servers')
    server_record = [x for x,item in enumerate(config['servers']) if item['serverId'] == serverId]
    league_record = [x for x,item in enumerate(config['servers'][server_record[0]]['leaguesAdded']) if item['leagueName'] == league]
    config['servers'][server_record[0]]['leaguesAdded'][league_record[0]]['schedule'] = data
    write_config_file('servers',config)

def add_league_roles(serverId,league,data):
    config = read_config_file('servers')
    server_record = [x for x,item in enumerate(config['servers']) if item['serverId'] == serverId]
    league_record = [x for x,item in enumerate(config['servers'][server_record[0]]['leaguesAdded']) if item['leagueName'] == league]
    config['servers'][server_record[0]]['leaguesAdded'][league_record[0]]['tierRoles'] = data
    write_config_file('servers',config)
    
def add_league_teams(serverId,league,data):
    config = read_config_file('servers')
    server_record = [x for x,item in enumerate(config['servers']) if item['serverId'] == serverId]
    league_record = [x for x,item in enumerate(config['servers'][server_record[0]]['leaguesAdded']) if item['leagueName'] == league]
    config['servers'][server_record[0]]['leaguesAdded'][league_record[0]]['teamRoles'] = data
    write_config_file('servers',config)

def get_track_description(track):
    api_key = "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"
    api_url = f"{env['OPEN_API_URL']}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {env['OPEN_API_KEY']}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": f"briefly describe the track layout for the {track} formula one grand prix track"
            }
        ]
    }

    response = requests.post(api_url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']
  
def create_embed(leagueName,serverId,track):
    embed = discord.Embed(color=discord.Colour.blurple(),)
    config = read_config_file('servers')
    server_config = [x for x in config['servers'] if x['serverId'] == serverId][0]
    league_config = [x for x in server_config['leaguesAdded'] if x['leagueName'] == leagueName][0]
    tags = [x['roleId'] for x in league_config['tierRoles']]
    teams = [x['roleName'] for x in league_config['teamRoles']]
    schedule = league_config['schedule']
    next_race = croniter.croniter(schedule,datetime.now())
    next_race = next_race.get_next(datetime)
    next_race = next_race.strftime('%d %B %Y at %H:%M')
    embed.add_field(name='**When**',value=next_race,inline=False)
    embed.add_field(name='**Where**',value=track,inline=False)
    try:
        description = get_track_description(track)
        embed.add_field(name='**Description**',value=description,inline=False)
    except Exception as e:
        pass
    
    # check if reserve, comms etc are in team name so they can be added to the bottom       
    for team in teams:
        if not re.search('reserve|comms|commentary',str(team).lower()):
            embed.add_field(name=f'{team}',value='-',inline=True)
    
    # add reserve role
    for team in teams:
        if re.search('reserve',str(team).lower()):
            embed.add_field(name=f'{team}',value='-',inline=False)
    
    # add not participating field
    embed.add_field(name='Not Participating',value='-',inline=False)
            
    # add comms role
    for team in teams:
        if re.search('comms|commentary',str(team).lower()):
            embed.add_field(name=f'{team}',value='-',inline=False)
    
    
    return embed,tags
    


# create_embed(leagueName='Lauda',serverId=1236964028690071562)
    