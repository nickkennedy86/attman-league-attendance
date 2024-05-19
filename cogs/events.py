from discord.ext import commands
from discord.ui.item import Item
from datetime import datetime
from include.config import *
import discord
import logging

logger = logging.getLogger('attman_logger')

class eventView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label='Participating',row=4,style=discord.ButtonStyle.green,emoji="👍",custom_id='racing')
    async def yes_callback(self,button,interaction):
        user = interaction.user.global_name
        roles = interaction.user.roles
        embed = interaction.message.embeds[0].to_dict()
        logger.info(f"{user} selected participating!")
        
        # add users roles to a list
        role_list = []
        for role in roles:
            role_list.append(role.name)
            
        # remove existing responses from user
        for field in embed['fields']:
            if user in field['value']:
                field['value'] = str(field['value']).replace(user,'')
                if len(str(field['value'])) == 0:
                    field['value'] = '-'
                break
            
        # add user if they have the right role
        for field in embed['fields']:
            if field['name'] in role_list:
                if field['value'] == '-':
                    field['value'] = user
                    break
                else:
                    field['value'] = '\n'.join([field['value'],user])
                    break
                
        # replace duplicate new lines
        for field in embed['fields']:
            while '\n\n' in field['value']:
                field['value'] = str(field['value']).replace('\n\n','\n')
        
        embed = discord.Embed.from_dict(embed)
        await interaction.response.edit_message(view=self,embed=embed)
        
    @discord.ui.button(label='Not Participating',row=4,style=discord.ButtonStyle.red,emoji="👎",custom_id='notracing')
    async def no_callback(self,button,interaction):
        user = interaction.user.global_name
        embed = interaction.message.embeds[0].to_dict()
        logger.info(f"{user} selected not participating!")
            
        # remove existing responses from user
        for field in embed['fields']:
            print(field)
            if user in field['value']:
                field['value'] = str(field['value']).replace(user,'')
                if len(str(field['value'])) == 0:
                    field['value'] = '-'
                break
            
        # add user to not participating
        for field in embed['fields']:
            if field['name'] == 'Not Participating':
                if field['value'] == '-':
                    field['value'] = user
                    break
                else:
                    field['value'] = '\n'.join([field['value'],user])
                    break
                
        # replace duplicate new lines
        for field in embed['fields']:
            while '\n\n' in field['value']:
                field['value'] = str(field['value']).replace('\n\n','\n')
        
        embed = discord.Embed.from_dict(embed)
        await interaction.response.edit_message(view=self,embed=embed)
   
class leagueAMPM(discord.ui.View):
    @discord.ui.select(
        placeholder='AM/PM',
        max_values=1,
        options=[
            discord.SelectOption(label='AM'),
            discord.SelectOption(label='PM'),
        ]
    )
    async def select_callback(self,select,interaction):
        edit_stored_values('am_pm',f'{select.values[0]}')
        cron = generate_cron()
        league = read_config_file('stored_values')['str']
        add_schedule(interaction.guild.id,league,cron)
        clear_stored_values()
        await interaction.response.send_message(f'{league} has been configured!',ephemeral=True)

class leagueMinute(discord.ui.View):
    @discord.ui.select(
        placeholder='Minute',
        max_values=1,
        options=[
            discord.SelectOption(label='0'),
            discord.SelectOption(label='5'),
            discord.SelectOption(label='10'),
            discord.SelectOption(label='15'),
            discord.SelectOption(label='20'),
            discord.SelectOption(label='25'),
            discord.SelectOption(label='30'),
            discord.SelectOption(label='35'),
            discord.SelectOption(label='40'),
            discord.SelectOption(label='45'),
            discord.SelectOption(label='50'),
            discord.SelectOption(label='55'),
        ]
    )
    async def select_callback(self,select,interaction):
        edit_stored_values('minute',f'{select.values[0]}')
        await interaction.response.send_message(f'Select AM or PM!',ephemeral=True,view=leagueAMPM())

class leagueHour(discord.ui.View):
    @discord.ui.select(
        placeholder='Hour',
        max_values=1,
        options=[
            discord.SelectOption(label='1'),
            discord.SelectOption(label='2'),
            discord.SelectOption(label='3'),
            discord.SelectOption(label='4'),
            discord.SelectOption(label='5'),
            discord.SelectOption(label='6'),
            discord.SelectOption(label='7'),
            discord.SelectOption(label='8'),
            discord.SelectOption(label='9'),
            discord.SelectOption(label='10'),
            discord.SelectOption(label='11'),
            discord.SelectOption(label='12'),
        ]
    )
    async def select_callback(self,select,interaction):
        edit_stored_values('hour',f'{select.values[0]}')
        await interaction.response.send_message(f'Select the start minute of your event!',ephemeral=True,view=leagueMinute())

class leagueDay(discord.ui.View):
    @discord.ui.select(
        placeholder='Select a day!',
        max_values=1,
        options=[
            discord.SelectOption(label='Monday'),
            discord.SelectOption(label='Tuesday'),
            discord.SelectOption(label='Wednesday'),
            discord.SelectOption(label='Thursday'),
            discord.SelectOption(label='Friday'),
            discord.SelectOption(label='Saturday'),
            discord.SelectOption(label='Sunday'),
        ]
    )
    async def select_callback(self,select,interaction):
        edit_stored_values('day',f'{select.values[0]}')
        await interaction.response.send_message(f'Select the start hour of your event!',ephemeral=True,view=leagueHour())

class leagueFrequency(discord.ui.View):
    @discord.ui.button(label='Daily',style=discord.ButtonStyle.green)
    async def daily_btn_callback(self,button,interaction):
        edit_stored_values('frequency','daily')
        await interaction.response.send_message('Select the day of your event!',ephemeral=True,view=leagueDay())
    @discord.ui.button(label='Weekly',style=discord.ButtonStyle.green)
    async def weekly_btn_callback(self,button,interaction):
        edit_stored_values('frequency','weekly')
        await interaction.response.send_message('Select the day of your event!',ephemeral=True,view=leagueDay())
    @discord.ui.button(label='Monthly',style=discord.ButtonStyle.green)
    async def monthly_btn_callback(self,button,interaction):
        edit_stored_values('frequency','monthly')
        await interaction.response.send_message('Select the day of your event!',ephemeral=True,view=leagueDay())

class leagueTeams(discord.ui.View):
    @discord.ui.select(
        select_type=discord.ComponentType.role_select,
        min_values=1,
        max_values=25
    )    
    async def select_callback(self,select,interaction):
        selected_roles = select.values
        server_id = interaction.guild.id
        role_list = []
        for i in range(len(selected_roles)):
            new_role = {
                "roleId":selected_roles[i].id,
                "roleName":selected_roles[i].name
            }
            role_list.append(new_role)
        league = read_config_file('stored_values')['str']
        add_league_teams(serverId=server_id,league=league,data=role_list)
        await interaction.response.send_message(f'Select the frequency of this league!',ephemeral=True,view=leagueFrequency())

class leagueRoles(discord.ui.View):               
    @discord.ui.select(
        select_type=discord.ComponentType.role_select,
        min_values=1,
        max_values=25
    )  
    async def select_callback(self,select,interaction):
        selected_roles = select.values
        server_id = interaction.guild.id
        role_list = []
        for i in range(len(selected_roles)):
            new_role = {
                "roleId":selected_roles[i].id,
                "roleName":selected_roles[i].name
            }
            role_list.append(new_role)
        league = read_config_file('stored_values')['str']
        add_league_roles(serverId=server_id,league=league,data=role_list)
            
        await interaction.response.send_message(f'Select the roles required to respond to your event!',ephemeral=True,view=leagueTeams())

# TO DO - Allow user to select channel to post attendance in
# class leagueChannel(discord.ui.View):
#    @discord.ui.select(
#        select_type=discord.ComponentType.channel_select,
#        max_values=1,
#    )
#     async def select_callback(self,select,interaction):
#         print(select.values)
#         selected_channel = select.values[0].id
#         server_id = interaction.guild.id
#         league = read_config_file('stored_values')['str']
#         add_channel(serverId=server_id,leagueName=league,channelName=selected_channel)
#         await interaction.response.send_message(f'Select the main league roles',ephemeral=True,view=leagueRoles())

class Events(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        @bot.event
        async def on_ready():
            bot.add_view(eventView())

        
    async def get_leagues(self, ctx: discord.AutocompleteContext):
        config = read_config_file('servers')
        leagues = [x for x in config['servers'] if x['serverId'] == ctx.interaction.guild.id][0]['leaguesAdded']
        leagues = [x['leagueName'] for x in leagues]
        return leagues
    
    async def get_tracks(ctx: discord.AutocompleteContext):
        tracks = read_config_file('tracks')['tracks']
        return sorted(list(tracks))

    @commands.slash_command(name='add_league',description="the name of the league you want to setup")
    async def league_setup(self,ctx,league_name:discord.Option(str)):
        logger.info(f'{ctx.user.global_name} used /add_league')
        # check server exists
        server_exists = server_check(ctx.guild.id)
        if server_exists:
            # check league exists
            league_exists = league_check(ctx.guild.id,league_name)
            if not league_exists:
                add_league(ctx.guild.id,league_name,ctx.user.global_name,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                message = f"{league_name} add to your server!"
            else:
                message = f"{league_name} is already configured!"
        await ctx.interaction.response.send_message(content=message,ephemeral=True)  
    
    @commands.slash_command(name='configure_league',description="add roles and teams to your leagues")
    async def configure_league(self,ctx,league:discord.Option(str,autocomplete=get_leagues)):
        logger.info(f'{ctx.user.global_name} used /configure_league')
        edit_stored_values('str',league)
        # channel = await self.bot.wait_for('message',check=ctx.author==discord.Message.author,timeout=30)
        await ctx.interaction.response.send_message('Select the roles to tag in your event!',ephemeral=True,view=leagueRoles())
        
    @commands.slash_command(name='add_event',description='create an event for a league!')
    async def add_event(self,ctx,league:discord.Option(str,autocomplete=get_leagues),track:discord.Option(str,autocomplete=get_tracks)):
        logger.info(f'{ctx.user.global_name} used /add_event')
        embed_create = create_embed(leagueName=league,serverId=ctx.guild.id,track=track)
        embed = embed_create[0]
        tags = embed_create[1]
        tags = sorted(tags)
        for i in range(len(tags)):
            tags[i] = f'<@&{tags[i]}>'
        tags = ' '.join(tags)
        await ctx.interaction.response.send_message(f'Attendance please {tags}!',ephemeral=False,embed=embed,view=eventView())
              
def setup(bot):
    bot.add_cog(Events(bot))

    
