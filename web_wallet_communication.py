import requests
import json
from time import sleep

# define request strings
requestType = 'https://wallet.burst.cryptoguru.org:8125/burst?requestType='
getBlockHeight = requestType + 'getBlock&height='
getMiningInfo = requestType + 'getMiningInfo'
getAccount = requestType + 'getAccount&account='
getRewardRecipient = requestType + 'getRewardRecipient&account='
getAccountTransactions = requestType + 'getAccountTransactions&account='


def get_block(height):
    """returns block id and block finder burst address"""
    r = requests.get(getBlockHeight + str(int(height)))
    if r.status_code != requests.codes.ok:
        return
    try:
        miner_id = r.json()['generator']
        block_id = r.json()['block']
    except KeyError:
        miner_id = None
        block_id = None

    return miner_id, block_id


def get_mining_info():
    """returns last mined block"""
    r = requests.get(getMiningInfo)
    if r.status_code != requests.codes.ok:
        return
    block_height = int(r.json()['height'])
    return str(block_height-1)


def get_miner_name(miner_id):
    """returns nick of a burst id, returns BURST-XXX if not set"""
    r = requests.get(getAccount + '%s' % miner_id)
    if r.status_code != requests.codes.ok:
        return
    msg = r.json()
    try:
        miner_name = msg['name']
    # if miner has no name
    except KeyError:
        miner_name = msg['accountRS']
    return miner_name


def get_reward_recipient(burst_id):
    """gets pool name/ name of reward recipient"""
    r = requests.get(getRewardRecipient + '%s' % burst_id)
    if r.status_code != requests.codes.ok:
        return
    msg = r.json()
    try:
        recipient_name = get_miner_name(msg['rewardRecipient'])
    # if miner is alone
    except KeyError:
        recipient_name = None
    return recipient_name


def get_account_transactions(burst_id):
    """gets last three transactions of a burst account"""
    r = requests.get(getAccountTransactions + '%s' % burst_id + '&firstIndex=0&lastIndex=3')
    if r.status_code != requests.codes.ok:
        return
    msg = r.json()
    try:
        transactions_list = []
        transactions = msg['transactions']
        for transaction in transactions:
            transactions_list.append({'sender':transaction['senderRS'],
                                      'amount':float(transaction['amountNQT'])/100000000,
                                      'acc_id':transaction['recipient'],
                                      'timestamp':transaction['timestamp']})
    # if no transactions are there
    except KeyError:
        transactions_list = None
    return transactions_list
