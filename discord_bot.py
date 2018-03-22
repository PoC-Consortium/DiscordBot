import sys
import discord
import utils
import requests
import aiohttp
import asyncio
import async_timeout
import sys
import pickle
import codecs
import messages as msg
import config_loader as config
from discord.ext import commands
from utils import *
import perm_check
import pool_communication as pcom

# Initialize Bot
bot = commands.Bot(command_prefix='!', description=msg.poc_bot_description)
# Remove predefined help function
bot.remove_command('help')


@bot.event
async def on_ready():
    print('=====================')
    print('Logged in as')
    print(bot.user.name)
    print('=====================')
    print('Connected Servers:')
    for server in bot.servers:
        print(server.name)
        for channel in server.channels:
            try:
                print('|- ' + channel.name)
            except UnicodeEncodeError:
                # TODO: Handle UTF-8 channel names
                pass
    print('=====================')


@bot.event
async def on_message(message):
    try:
        message_touple = (message.timestamp, message.author, message.content)
        print("%s User %s: %s" % message_touple)
    except Exception as e:
        print(e)
    # Answer only to specified allowed channels and private messages to bot
    if message.channel.name in config.CHANNEL_NAMES or message.channel.is_private:
        await bot.process_commands(message)
    else:
        return


@bot.event
async def on_error(error, r):
    """Prints occured error while running bot"""
    print(error)


# ======Bot Commands======
@bot.command()
async def status():
    """Displays Status of Bot"""
    await bot.say('PoCC-Bot observing channels:')
    for channel_name in config.CHANNEL_NAMES:
        await bot.say("|- %s" % channel_name)


@bot.command(pass_context=True)
async def block(ctx):
    """Shows current Block"""
    channel = ctx.message.channel
    miner_name, pool_name, block_height, block_id = get_block_winner()
    embed = get_embed_winner(miner_name, pool_name, block_id, config.POOL_NAMES)
    embed.title = "THE LAST GENERATED BLOCK"
    await bot.send_message(channel,  embed=embed)


@bot.command(pass_context=True)
async def payouts(ctx):
    """Shows last block"""
    channel = ctx.message.channel
    if not(ctx.message.content == '!payouts'):
        burst_id = ctx.message.content.split(' ')[1]
    else:
        await bot.say("TODO")
        return
    transactions = get_account_transactions(burst_id)
    if transactions:
        payouts_ = []
        for transaction in transactions:
            if get_miner_name(transaction['sender']) in config.POOL_NAMES:
                payouts_.append({'pool':get_miner_name(transaction['sender']),
                                'amount':transaction['amount'],
                                'acc_id':transaction['acc_id'],
                                'timestamp':transaction['timestamp']})
        if payouts_:
            embed = get_embed_payouts(get_miner_name(burst_id), payouts_)
            await bot.send_message(channel,  embed=embed)
            return
    await bot.say("Account **%s** was not found or has no payouts!" % burst_id)


@bot.command(pass_context=True)
async def price(ctx):
    """Shows Exchangerates and Stats on defined coin. Example: !price Burst"""
    try:
        if len(ctx.message.content) == len("!price"):
            coin = "burst"
        else:
            coin = ctx.message.content.lower()
            coin = coin.split(' ')[1]
            print(coin)
        response_eur = await fetch("https://api.coinmarketcap.com/v1/ticker/{}/?convert=EUR".format(coin))
        response_usd = await fetch("https://api.coinmarketcap.com/v1/ticker/{}/?convert=USD".format(coin))
        response_eur = json.loads(response_eur)[0]
        response_usd = json.loads(response_usd)[0]
        channel = ctx.message.channel
        embed = get_currency_stats(response_eur, response_usd, coin=coin)
        await bot.send_message(channel,  embed=embed)
    except Exception as e:
        response_message = "Retrieving price failed :tired_face: \n\nSorry...\n\nTry: !price Burst"
        print(e)
        await bot.say(response_message)


@bot.command(pass_context=True)
async def pool(ctx):
    """Shows Statis about pool, example: !pool 0-100"""
    try:
        if len(ctx.message.content) == len("!pool"):
            pool = config.POOL_URL['50-50']
        else:
            pool = ctx.message.content.lower()
            pool = pool.split(' ')[1]
            if pool in config.POOL_URL.keys():
                pool = config.POOL_URL[pool]
        channel = ctx.message.channel
        embed = get_pool_stats_embed(pool)
        await bot.send_message(channel,  embed=embed)
    except Exception as e:
        response_message = "Retrival of Pool Stats failed :tired_face: \n\nSorry...\n\nTry: !pool 50-50"
        print(e)
        await bot.say(response_message)


@bot.command(pass_context=True)
async def miner(ctx):
    """Shows Statis about miner, example: !miner numeric_id"""
    try:
        if len(ctx.message.content) < len("!miner "):
            response_message = "No miner specified, try: !miner numeric_id"
            await bot.say(response_message)
            return 0
        else:
            miner_id = ctx.message.content.lower()
            miner_id = miner_id.split(' ')[1]
        channel = ctx.message.channel
        embed = get_miner_stats_embed(miner_id)
        if type(embed) == type('str'):
            await bot.say(embed)
        else:
            await bot.send_message(channel,  embed=embed)
    except Exception as e:
        response_message = "Retrival of Miner Stats failed :tired_face: \n\nSorry...\n\nTry: !miner numeric_id"
        print(e)
        await bot.say(response_message)


@bot.command(pass_context=True)
async def subscribe(ctx):
    try:
        account_id = ctx.message.content.split(' ')[1]
        subscribe_ = ctx.message.content.split(' ')[2]
        discord_acc = ctx.message.author
        if not(subscribe_ in ['payouts', 'blocks-by-us', 'blocks-by-me']):
            raise
    except Exception as e:
        print(e)
        await bot.say("This was not a valid subscription!\nTry ***!subscribe BURST-XXXX-XXXX-XXXX-XXX payouts***")
        return
    acc_nick = get_miner_name(account_id)
    if not(discord_acc in SUBSCRIBERS):
        print(discord_acc)
        SUBSCRIBERS[discord_acc] = {'discord_acc': discord_acc,
                                    'sub_mod': [subscribe_],
                                    'burst_id': account_id,
                                    'last_payout': None
                                    }
    else:
        if not(subscribe_ in SUBSCRIBERS[discord_acc]['sub_mod']):
            SUBSCRIBERS[discord_acc]['sub_mod'].append(subscribe_)
        else:
            await bot.say("You have this service already subscribed!")
            return

    print(SUBSCRIBERS)
    with open('subscriber.p', 'wb') as p_file:
        pickle.dump((SUBSCRIBERS), p_file)
    response = msg.subscribe % (subscribe_, acc_nick, subscribe_)
    await bot.send_message(discord_acc, response)


@bot.command(pass_context=True)
async def unsubscribe(ctx):
    try:
        subscribe_ = ctx.message.content.split(' ')[1]
        discord_acc = ctx.message.author
        if not(subscribe_ in ['payouts', 'blocks-by-us', 'blocks-by-me', 'all']):
            raise
    except Exception as e:
        print(e)
        await bot.say("This was not a valid unsubscription!\nTry ***!unsubscribe payout***")
        return
    if subscribe_ == "all":
        print("Removing ", subscribe_)
        SUBSCRIBERS[discord_acc]['sub_mod'] = []
    if subscribe_ in SUBSCRIBERS[discord_acc]['sub_mod']:
        print("Removing ", subscribe_)
        SUBSCRIBERS[discord_acc]['sub_mod'].remove(subscribe_)
    await bot.send_message(discord_acc, 'Unsubscribed %s!' % subscribe_)


@bot.command()
async def help():
    """Displays commands on this bots"""
    msg_ = msg.help_response
    await bot.say(msg_)


# Admin related
@bot.command(pass_context=True, no_pm=True)
@perm_check.mod_or_permissions(manage_server=True)
async def shutdown(ctx):
    """Bot Shutdown"""
    print("User requests shutdown:")
    print(ctx.message.author)
    try:
        print("bot shutdown by super user %s" % ctx.message.author)
        await bot.say('Bye Bye')
        bot.logout()
        sys.exit()
    # TODO: Exit Bot nicely
    except CancelledError:
        sys.exit(1)
    finally:
        sys.exit()


@bot.command()
@perm_check.mod_or_permissions(manage_server=True)
async def toggle_block_mode():
    """Toggles the mode, where the bot displays the winner of the current block"""
    if config.BLOCK_MODE == 'All':
        config.BLOCK_MODE = 'PoCC-Only'
    elif config.BLOCK_MODE == 'PoCC-Only':
        config.BLOCK_MODE = 'All'
    else:
        await bot.say('Unknown BlockMode in Config, changing to **All**')
        return
    await bot.say('Changed BlockMode to %s' % config.BLOCK_MODE)
    print("Changed to %s" % config.BLOCK_MODE)


async def _show_winner(channels, miner_name, pool_name, block_id, sub_mode=False):
    """displays current block winner"""
    for channel in channels:
        if config.BLOCK_MODE == 'All' and not(sub_mode):
            embed = get_embed_winner(miner_name, pool_name, block_id, config.POOL_NAMES)
            await bot.send_message(channel,  embed=embed)
            return
        elif pool_name in config.POOL_NAMES:
            embed = get_embed_winner(miner_name, pool_name, block_id, config.POOL_NAMES)
            await bot.send_message(channel,  embed=embed)


async def fetch(url):
    """Retrieves response from http session"""
    with async_timeout.timeout(10):
        r = requests.get(url)
        return r.text


def _last_payout(burst_id):
    """Shows last payout"""
    transactions = get_account_transactions(burst_id)
    if transactions:
        payouts_ = []
        for transaction in transactions:
            if get_miner_name(transaction['sender']) in config.POOL_NAMES:
                payouts_.append(
                    {'pool':get_miner_name(transaction['sender']),
                    'amount':transaction['amount'],
                    'acc_id':transaction['acc_id'],
                    'timestamp':transaction['timestamp']})
        return payouts_[0]
    else:
        return None


async def process_subscribers(miner_name, pool_name, block_id):
    """Gets last payout of each subscriber and notify them if a payout was done"""
    for account, data in SUBSCRIBERS.items():
        try:
            if 'payouts' in data['sub_mod']:
                payouts_ = _last_payout(data['burst_id'])
                if payouts_:
                    if not(data['last_payout'] == payouts_['timestamp']) and  payouts_['pool'] in config.POOL_NAMES:
                        msg_ = "Received payout of %s BURST from %s" % (payouts_['amount'], payouts_['pool'])
                        SUBSCRIBERS[account]['last_payout'] = payouts_['timestamp']
                        await bot.send_message(account,  msg_)
            if 'blocks-by-us' in data['sub_mod']:
                await _show_winner([account], miner_name, pool_name, block_id, sub_mode=True)
            if 'blocks-by-me' in data['sub_mod']:
                if miner_name == get_miner_name(data['burst_id']):
                    await _show_winner([account], miner_name, pool_name, block_id, sub_mode=True)
        except Exception as e:
            print("ERROR in process_subscribers: ",e)

    with open('subscriber.p', 'wb') as p_file:
        pickle.dump((SUBSCRIBERS), p_file)
    with open('subscriber_backup.p', 'wb') as p_file:
        pickle.dump((SUBSCRIBERS), p_file)


async def bot_loop():
    """A Loop, where the bot updates block mining status and processes subscribers"""
    await bot.wait_until_ready()

    loop = asyncio.get_event_loop()
    old_height = None

    channels = get_channels_by_names(bot, config.CHANNEL_NAMES)
    if len(channels) == 0:
        exit("No channels found")

    # Loop retrieving block winner
    while not bot.is_closed:
        try:
            miner_name, pool_name, block_height, block_id = get_block_winner()
            # Seperate blocks by height
            if not(block_height == old_height) and miner_name:
                old_height = block_height
                await _show_winner(channels, miner_name, pool_name, block_id)
                await process_subscribers(miner_name, pool_name, block_id)
            await asyncio.sleep(config.SLEEP_TIME)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # Try to load pickled subscriber data
    try:
        SUBSCRIBERS = pickle.load(open('subscriber.p', 'rb'))
    except Exception as e:
        # Create new file, if an error occured
        print(e)
        SUBSCRIBERS = {}
        with open('subscriber.p', 'wb') as f:
            pickle.dump(SUBSCRIBERS, f)

    bot.loop.create_task(bot_loop())
    bot.run(config.DISCORD_TOKEN)
