# Discord Bot
This is the Discord bot used in the channel <https://discord.gg/7Hqqt5G>

## Features
* Posts a message into the chat when a new block is found
* Has a subscription-service, where you will get private messages from the bot, if you win blocks or get payouts

```
Bot Commands:
    !block - displays the winner of the last block
    !price [coin] - displays coin market information, default: burst
    !payouts [account-id] - shows the last payouts from the PoCC-pools to this account
    !status - shows channels, where the bot is broadcasting

Subscription:
    !subscribe [account-id] [payouts/blocks-by-us/blocks-by-me] - sends private messages to your account
    !unsubscribe [all/payouts/blocks-by-us/blocks-by-me] - stops subscription of service

Admin Commands:
    !shutdown - disables bot process
    !toggle_block_mode - toggle, if the bot should displays only PoCC pools wins or all
```
