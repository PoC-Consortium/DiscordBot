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

**__Subscription__**:
    **!subscribe [*account-id*] [*payouts/blocks-by-us/blocks-by-me*]** - sends private messages to your account
    **!unsubscribe [*all/payouts/blocks-by-us/blocks-by-me*]** - stops subscription of service

**__Admin Commands__**:
    **!shutdown** - disables bot process
    **!toggle_block_mode** - toggles, if the bot should display only PoCC pools wins or all
"""

subscribe ="""
You subscribed ***%s*** for ***%s***!\n
If you want to unsubscribe write ***!unsubscribe %s***
"""
