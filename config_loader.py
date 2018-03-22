import configparser

# Read config.ini
config = configparser.ConfigParser()
config.read('config.ini')

try:
    BLOCK_INFO_SITE = config['Burst']['BlockInfoAdress']

    DISCORD_TOKEN = config['Discord']['DiscordToken']
    CHANNEL_NAMES = config['Discord']['ChannelNames'].split(',')

    SLEEP_TIME = int(config['Bot']['RequestPeriodTime'])
    BOT_ICON_URL = config['Bot']['BotIconUrl']
    BLOCK_MODE = config['Bot']['BlockMode']

    POOL_NAMES = config['Pool']['PoolNames'].split(',')
    POOL_URL = config['Pool']['PoolUrl'].split(',')
    POOL_PICTURES_URL = config['Pool']['PoolPicturesUrl'].split(',')
    OTHER_POOL_PICTURE = config['Pool']['OtherPoolPicture']
    # Create Dict of URLs
    keys = POOL_NAMES
    values = POOL_PICTURES_URL
    POOL_PICTURES_URL = {k:v for k, v in zip(keys, values)}
    values = POOL_URL
    POOL_URL = {k[11:]:v for k, v in zip(keys, values)}
except Exception as e:
    print("Config File invalid!")
    print(e)
    raise
