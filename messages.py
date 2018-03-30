# Provides often displayed messages
unknown_cmd = "was not recognized. Use !help to display all valid commands."

poc_bot_description = "I am the PoC-Bot, your little helper in daily burst life."

hello = "Hello!"

help_response = """
**__Bot Commands__**:
    **!block** - displays the winner of the last block
    **!price [*coin*]** - displays coin market information, default: burst
    **!payouts [*account-id*]** - shows the last payouts from the PoCC-pools to defined account
    **!status** - shows the channels, where the bot is broadcasting
    **!pool [*pool_name*]** - shows some interesting information about specified pool
    **!miner [*miner_numeric_id*]** - shows some interesting information about specified miner

**__Subscription__**:
    **!subscribe [*payouts/blocks-by-us/blocks-by-me*] [*account-id*]** - sends private messages to your account
    **!unsubscribe [*all/payouts/blocks-by-us/blocks-by-me*] [*account-id*]** - stops subscription of service

**__Admin Commands__**:
    **!shutdown** - disables bot process
    **!toggle_block_mode** - toggles, if the bot should display only PoCC pools wins or all


***If you need help with the bot, contact @Heos#1985***
"""

subscribe ="""
You subscribed ***%s*** for ***%s***!\n
If you want to unsubscribe write ***!unsubscribe %s %s***
"""
