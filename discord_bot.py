import discord
import requests
import asyncio
import re
import json
import pickle
import datetime
import math
import aiohttp
import async_timeout
import configparser

# read config
config = configparser.ConfigParser()
config.read('config.ini')

JS_LOGTAIL_ADDRESS = config["Pool"]["JsLogtailAddress"]
SLEEP_TIME = config["Pool"].getint("SleepTime")
CHANNEL_NAMES = config["Discord"]["ChannelNames"].split(",")
BOT_TOKEN = config["Discord"]["BotToken"]

POOL_BURST_ADDRESS = config["Pool"]["BurstAddress"]

WALLET_ADDRESS = config["Burst"]["WalletAddress"]
POOL_ADDRESS = config["Pool"]["PoolAddress"]

BLOCK_EXPLORER_ACCOUNT_ADDRESS = config["Burst"]["BlockExplorerAccountAddress"]
BLOCK_EXPLORER_BLOCK_ADDRESS = config["Burst"]["BlockExplorerBlockAddress"]

TIME_OFFSET = config["Burst"].getint("TimeOffset")  # offset for blockchain timestamps
GENESIS_BASE_TARGET = config["Burst"].getint("GenesisBaseTarget")

# Create client
client = discord.Client()
try:
    users = pickle.load(open("users.p", "rb"))
    print("loaded users")
except:
    users = {}
    print("not loaded users")

http_session = None


async def fetch(url):
    with async_timeout.timeout(10):
        async with http_session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                raise Exception("invalid respone")


@client.event
async def on_message(message):
    if not (message.channel.name in CHANNEL_NAMES or message.channel.is_private):
        return

    response_message = None
    embed = None

    # TODO: split up into individual functions
    if message.content.startswith('!last'):

        number_of_payments = 1
        account_id = None

        # legacy commands
        if len(message.content) > len("!last") and message.content[len("!last")] != " ":
            message.content = message.content[:len("!last") - 1] + " " + message.content[len("!last"):]

        params = message.content.split(" ")

        if len(params) > 1:
            try:
                number_of_payments = abs(int(params[1]))
                number_of_payments = min(number_of_payments, 25)
            except:
                number_of_payments = None

        if len(params) > 2:
            account_id = params[2]

        if account_id is None and message.author in users:
            account_id = users[message.author]

        if account_id is None or number_of_payments is None:
            response_message = "Usage: !last [*#payouts*] [*account-id*]"
        else:
            try:
                response = await fetch(
                    "{}/burst?requestType=getAccountTransactions&account={}&firstIndex=0&lastIndex=100&random=0".format(
                        WALLET_ADDRESS, account_id))
                response = json.loads(response)

                if not "transactions" in response:
                    raise Exception("Unknown account")

                found = 0

                dates = ""
                amounts = ""
                blocks = ""
                total_amount = 0

                for transaction in response["transactions"]:
                    if transaction["senderRS"] == POOL_BURST_ADDRESS:
                        found += 1
                        date = datetime.datetime.fromtimestamp(int(transaction["timestamp"]) + TIME_OFFSET).strftime(
                            '%d.%m.%Y %H:%M:%S')

                        # responseMessage += "{:6.2f} BURST @ {} (Block {})\n".format(
                        #   float(transaction["amountNQT"]) / 100000000,
                        #    date,
                        #    transaction["height"])
                        dates += "{}\n".format(date)
                        blocks += "{}\n".format(transaction["height"])

                        amount = float(transaction["amountNQT"]) / 100000000
                        amounts += "{:.2f} BURST\n".format(amount)

                        total_amount += amount

                        if found >= number_of_payments:
                            break

                if found == 0:
                    response_message = "No payment in last transactions"
                else:
                    embed = discord.Embed(title="" if number_of_payments == 1 else "Last Payouts".upper())
                    embed.add_field(name="Amount", value=amounts)
                    embed.add_field(name="Date", value=dates)
                    embed.add_field(name="Block", value=blocks)

                    if number_of_payments > 1:
                        embed.add_field(name="Total", value="{:.2f} BURST".format(total_amount))

            except BaseException as e:
                print(e)
                response_message = "Error :tired_face:"
    if message.content.startswith("!reg"):
        account_id = message.content[len("!reg "):]

        if account_id == "" or not account_id.isdigit():
            response_message = "Usage: `!reg <numeric-account-id>`"
        else:
            users[message.author] = account_id
            pickle.dump(users, open("users.p", "wb"))
            response_message = "updated BURST account id"
    if message.content == "!userinfo":
        if message.author in users:
            response_message = "Your BURST account id is {}".format(users[message.author])
        else:
            response_message = "I don't know you :stuck_out_tongue: Use the `!reg` command"
    if message.content == "!status":
        try:
            # balance
            response = await fetch(
                "{}/burst?requestType=getAccount&account={}&random=0".format(WALLET_ADDRESS, POOL_BURST_ADDRESS))
            response = json.loads(response)
            pool_balance = int(response["unconfirmedBalanceNQT"]) / 100000000

            # number of miners
            response = await fetch(
                "{}/burst?requestType=getAccountsWithRewardRecipient&account={}&random=0".format(WALLET_ADDRESS,
                                                                                                 POOL_BURST_ADDRESS))
            response = json.loads(response)
            miners = response["accounts"]
            number_of_miners = len(miners)

            # last block
            response = await fetch("{}/burst?requestType=getBlock".format(WALLET_ADDRESS))
            response = json.loads(response)
            highest_block = response

            net_diff = GENESIS_BASE_TARGET / int(highest_block["baseTarget"])

            embed = discord.Embed(title="Pool Status".upper())
            embed.add_field(name="Balance", value="{:.2f} BURST".format(pool_balance))
            embed.add_field(name="Assigned Miners", value=number_of_miners)

            online = False
            try:
                await fetch(POOL_ADDRESS)
                online = True
            except Exception as e:
                print(e)

            embed.add_field(name="Status", value="Online" if online else "OFFLINE!")

            # last mined block
            blocks_per_page = 100
            last_block = None

            for page in range(100):
                response = await fetch(
                    "{}/burst?requestType=getBlocks&includeTransactions=false&firstIndex={}&lastIndex={}".format(
                        WALLET_ADDRESS, page * blocks_per_page, (page + 1) * blocks_per_page - 1))
                response = json.loads(response)

                for block in response["blocks"]:
                    # todo use hashmap
                    if block["generator"] in miners:
                        last_block = block

                        break

                if last_block is not None:
                    break

            if last_block is not None:
                date = datetime.datetime.fromtimestamp(int(last_block["timestamp"]) + TIME_OFFSET).strftime(
                    '%d.%m.%Y %H:%M:%S')

                embed.add_field(name="Last Won Block", value=last_block["height"])
                embed.add_field(name="Date", value=date)
                embed.add_field(name="Winner", value=last_block["generatorRS"].replace("BURST-", ""))

                block_link = BLOCK_EXPLORER_BLOCK_ADDRESS.format(last_block["block"])
                embed.add_field(name="Link To Last Won Block", value=block_link)

            embed.add_field(name="Current Block", value=int(highest_block["height"]) + 1)
            date = datetime.datetime.fromtimestamp(int(highest_block["timestamp"]) + TIME_OFFSET)
            now = datetime.datetime.now()
            date_diff = str(now - date)
            date_diff = date_diff[:date_diff.find(".")]

            embed.add_field(name="Time Spent", value=date_diff)
            embed.add_field(name="Network Difficulty", value="{:.2f}".format(net_diff))

        except Exception as e:
            print(e)
            response_message = "Accessing pool wallet failed :tired_face:"

    if message.content.startswith("!price"):
        coin = message.content[len("!price "):]

        if coin == "":
            coin = "burst"
        else:
            coin = coin.lower()
        try:
            response = await fetch("https://api.coinmarketcap.com/v1/ticker/{}/?convert=EUR".format(coin))
            response = json.loads(response)
            response = response[0]

            embed = discord.Embed(title="{} Market Information".format(coin).upper())
            embed.add_field(name="Bitcoin Value", value="{} BTC".format(response["price_btc"]))
            embed.add_field(name="Euro Value", value="{:.2f} EUR".format(float(response["price_eur"])))
            embed.add_field(name="Market Cap", value="{:,} EUR".format(float(response["market_cap_eur"])))
            embed.add_field(name="1hr Change", value="{0:+.1f}%".format(float(response["percent_change_1h"])))
            embed.add_field(name="24hr Change", value="{0:+.1f}%".format(float(response["percent_change_24h"])))
            embed.add_field(name="7d Change", value="{0:+.1f}%".format(float(response["percent_change_7d"])))
        except Exception as e:
            print(e)
            response_message = "Retrieving price failed :tired_face:"
    if message.content.startswith("!tb"):
        tmp = await client.send_message(message.channel,
                                        '{}: Stand by, this might take a while.'.format(message.author.mention),
                                        embed=embed)

        try:
            # todo remove code duplication w.r.t. !status
            number_of_blocks = 1000
            if message.content.find(" ") > 0:
                blocks = message.content[message.content.find(" ") + 1:]
                if blocks.isdigit():
                    number_of_blocks = min(10000, int(blocks))

            blocks_per_page = 100
            number_of_blocks = math.ceil(number_of_blocks / blocks_per_page) * blocks_per_page

            # get miners
            response = await fetch(
                "{}/burst?requestType=getAccountsWithRewardRecipient&account={}&random=0".format(WALLET_ADDRESS,
                                                                                                 POOL_BURST_ADDRESS))
            response = json.loads(response)
            miners = response["accounts"]

            cumulative_difficulty = 0
            found_blocks = 0

            for page in range(math.ceil(number_of_blocks / blocks_per_page)):
                # print(cumulativeDifficulty, foundBlocks)
                response = await fetch(
                    "{}/burst?requestType=getBlocks&includeTransactions=false&firstIndex={}&lastIndex={}".format(
                        WALLET_ADDRESS, page * blocks_per_page, (page + 1) * blocks_per_page - 1))
                response = json.loads(response)

                for block in response["blocks"]:
                    net_diff = GENESIS_BASE_TARGET / int(block["baseTarget"])
                    cumulative_difficulty += net_diff
                    # todo use hashmap
                    if block["generator"] in miners:
                        found_blocks += 1

            average_diff = cumulative_difficulty / number_of_blocks

            approx_pool_size = (found_blocks / number_of_blocks) * average_diff

            embed = discord.Embed(title="Approximate Pool Size".upper())
            embed.add_field(name="# Incorporated Blocks", value=number_of_blocks)
            embed.add_field(name="Won By Pool", value=found_blocks)
            embed.add_field(name="Average Network Difficulty", value="{:.2f}".format(average_diff))
            embed.add_field(name="(Very) Roughly Estimated Pool Size", value="{:.2f} TB".format(approx_pool_size))

            await client.edit_message(tmp, '{}:'.format(message.author.mention), embed=embed)

            embed = None

        except Exception as e:
            print(e)
            await client.edit_message(tmp, '{}: {}'.format(message.author.mention, "Error :tired_face:"))

            embed = None
    if message.content == "!help":
        response_message = """
**__Bot Commands__**:
**!help** - shows this message
**!last [*#payouts*] [*account-id*]** - shows the last *#payouts* payouts of the pool to the given account. If account id is omitted, your last payouts are shown (register first with !reg)
**!last1**-**!last9** - shows the last n payouts analogue to !last
**!price [*coin*]** - displays coin market information, default: burst
**!reg *numeric-account-id* ** - registers your account id for the !last command
**!status** - shows the current status of the pool
**!tb [*number-of-blocks*]** - shows the estimated pool size in TB. Per default it considers the last 1000 blocks.
**!userinfo** - shows your registered account id
"""

    if response_message is not None or embed is not None:
        if response_message is None:
            response_message = "";
        try:
            await client.send_message(message.channel, '{}: {}'.format(message.author.mention, response_message),
                                      embed=embed)
        except Exception as e:
            print("could not send", e)


async def build_message(line):
    try:
        m = re.search("- ?([0-9]+) ?- *(BURST[A-Z0-9\-]+)", line)
        block = m.group(1)
        winner = m.group(2)

        try:
            response = await fetch("{}/burst?requestType=getAccount&account={}&random=0".format(WALLET_ADDRESS, winner))
            response = json.loads(response)

            numeric_account_id = response["account"]

            response = await fetch(
                "{}/burst?requestType=getAccountBlockIds&account={}&random=0".format(WALLET_ADDRESS, numeric_account_id))
            response = json.loads(response)

            block_id = response["blockIds"][0]

            account_link = BLOCK_EXPLORER_ACCOUNT_ADDRESS.format(numeric_account_id)
            block_link = BLOCK_EXPLORER_BLOCK_ADDRESS.format(block_id)

            message = "We Won Block {}! :money_mouth: Winner: {}\nWinner: {}\nBlock: {}".format(block, winner,
                                                                                                account_link, block_link)
        except Exception as e:
            print(e)
            message = "We Won Block {}! :money_mouth: Winner: {}".format(block, winner)

    except Exception as e:
        print(e)
        message = line
    return message


async def process_log_lines(lines, channels):
    global client
    for line in lines.split("\n"):

        # print("line: " + line + ":: " + str(line.find("We Lost") >= 0))
        if line.find("We Won") >= 0:
            message = await build_message(line)
            for channel in channels:
                await client.send_message(channel, message)


def get_channels_by_names(client, names):
    channels = client.get_all_channels()
    result = []
    for channel in channels:
        for name in names:
            if channel.name == name:
                result.append(channel)
    return result


async def poolLogReader():
    await client.wait_until_ready()

    loop = asyncio.get_event_loop()

    global http_session
    http_session = aiohttp.ClientSession(loop=loop)

    print("logreader startet")

    # get channel
    channels = get_channels_by_names(client, CHANNEL_NAMES)
    if len(channels) == 0:
        exit("No channels found")

    # await client.send_message(channel, "beep")

    initial_request_length = 500

    result = requests.get(JS_LOGTAIL_ADDRESS, headers={"Range": "bytes=-{}".format(initial_request_length)})
    content_range = result.headers["Content-Range"]
    byte_offset = int(content_range[content_range.find("-") + 1:content_range.find("/")])

    while not client.is_closed:
        # await client.send_message(channel, "beep")
        result = requests.get(JS_LOGTAIL_ADDRESS, headers={"Range": "bytes={}-".format(byte_offset)})

        length = int(result.headers["Content-Length"])
        if length > 1:
            response = result.text.strip()
            # print(response)

            await process_log_lines(response, channels)

            byte_offset += length - 1

        await asyncio.sleep(SLEEP_TIME)

    print("logReader exit")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_error(e):
    print(e)


# start the client
client.loop.create_task(poolLogReader())
client.run(BOT_TOKEN)
