from bs4 import BeautifulSoup
import requests
import discord
import sys
import string
import datetime
import config_loader as config
from web_wallet_communication import *


def get_block_winner():
    """retrieves winning block information"""
    height = get_mining_info()
    miner_id, block_id = get_block(height)
    if miner_id:
        reward_recipient = get_reward_recipient(miner_id)
        miner_name = get_miner_name(miner_id)
        return miner_name, reward_recipient, height, block_id
    else:
        return None, None, height, None


def get_channels_by_names(bot, names):
    """returns server channels by name"""
    channels = bot.get_all_channels()
    result = []
    for channel in channels:
        for name in names:
            if channel.name == name:
                result.append(channel)
    return result


def get_embed_winner(winner, pool_name, block_id, pocc_pool_names):
    """creates an embed to display a fancy message to the world"""
    account_id, _ = get_block(get_mining_info())
    winner_linked = "[%s](https://explore.burst.cryptoguru.org/account/%s)" % (winner,account_id)
    message_body = ":trophy: " + winner_linked + " has won the block :trophy:\n\n"
    if pool_name and not(pool_name == winner):
        message_body_pool = "Pool: " + pool_name
    else:
        message_body_pool = "Miner is mining solo! :scream:"
    embed = discord.Embed(
        title="NEW BLOCK WAS GENERATED",
        description=message_body + message_body_pool,
        url="https://explore.burst.cryptoguru.org/block/%s" % block_id,
        color=16777215,
        timestamp=datetime.datetime.now())
    embed.set_footer(text="PoCC-Bot")
    embed.set_author(
        name="PoCC-Bot",
        url="https://explore.burst.cryptoguru.org/",
        icon_url=config.BOT_ICON_URL)
    if pool_name in pocc_pool_names:
        # Show PoCC-Pool winning picture
        embed.set_thumbnail(url=config.POOL_PICTURES_URL[pool_name])
    else:
        # Show the others winning picture
        embed.set_thumbnail(url=config.OTHER_POOL_PICTURE)
    return embed


def get_embed_payouts(account_name, payouts):
    """creates a fancy embed to create a nice message about payouts"""
    account_id, _ = get_block(get_mining_info())
    message_body = '\n'
    for payout in payouts:
        payout_msg = "Payout of %s BURST from %s\n\n" % (payout['amount'], payout['pool'])
        message_body = message_body + payout_msg

    embed = discord.Embed(
        title="***Mining-Payouts of %s***" % account_name,
        description=message_body,
        url="https://explore.burst.cryptoguru.org/account/%s" % payouts[0]['acc_id'],
        color=16777215,
        timestamp=datetime.datetime.now())
    embed.set_footer(text="PoCC-Bot")
    embed.set_author(
        name="PoCC-Bot",
        url="https://explore.burst.cryptoguru.org/",
        icon_url=config.BOT_ICON_URL)
    # Show PoCC-Pool winning picture
    embed.set_thumbnail(url=config.POOL_PICTURES_URL[payouts[0]['pool']])
    return embed


def get_currency_stats(response, response_usd, coin="Burst"):
    """gets current crypto currency informations inside an embed"""
    try:
        embed = discord.Embed(
            title="{} Market Information".format(coin).upper(),
            color=16777215)
        embed.add_field(name="Bitcoin Value", value="{} BTC".format(response["price_btc"]))
        embed.add_field(name="Euro Value", value="{:.4f} €".format(float(response["price_eur"])))
        embed.add_field(name="US-Dollar Value", value="{:.4f} $".format(float(response_usd["price_usd"])))
        embed.add_field(name="Currency Rank", value="{:.4f}".format(float(response["rank"])))
        embed.add_field(name="Market Cap €", value="{:,} €".format(float(response["market_cap_eur"])))
        embed.add_field(name="Market Cap $", value="{:,} $".format(float(response_usd["market_cap_usd"])))
        embed.add_field(name="1hr Change", value="{0:+.2f}%".format(float(response["percent_change_1h"])))
        embed.add_field(name="24hr Change", value="{0:+.2f}%".format(float(response["percent_change_24h"])))
        embed.add_field(name="7d Change", value="{0:+.2f}%".format(float(response["percent_change_7d"])))
    except Exception as e:
        print(e)
        response_message = "Retrieving price failed :tired_face:"
    return embed


if __name__ == "__main__":
    print(get_block_winner())
