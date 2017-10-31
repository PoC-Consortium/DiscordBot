# Discord Bot
This is the Discord bot used in the channel <https://discord.gg/7Hqqt5G>

## Features
* Posts a message into the chat when a new block is found
* Supports several commands

#### Bot commands
```
!help - shows this message
!last [#payouts] [account-id] - shows the last #payouts payouts of the pool to the given account. If account id is omitted, your last payouts are shown (register first with !reg)
!last1-!last9 - shows the last n payouts analogue to !last
!price [coin] - displays coin market information, default: burst
!reg numeric-account-id  - registers your account id for the !last command
!status - shows the current status of the pool
!tb [number-of-blocks] - shows the estimated pool size in TB. Per default it considers the last 1000 blocks.
!userinfo - shows your registered account id
```
