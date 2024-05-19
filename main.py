from include.logger import setup_logger
import discord
import dotenv

env = dotenv.dotenv_values('./resources/.env')
logger = setup_logger(env['LOG_LEVEL'])
bot = discord.Bot()

cog_list = [
    'registration',
    'events'
]
for cog in cog_list:
    bot.load_extension(f'cogs.{cog}')

if __name__ == '__main__':
    logger.info('bot is running')
    bot.run(env['BOT_TOKEN'])
    logger.info('bot is stopped')