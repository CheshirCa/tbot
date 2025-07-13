# tbot
A Telegram bot for managing MikroTik routers via SSH with secure key-based authentication.

## Table of Contents
1. [Telegram Setup](#telegram-setup)
2. [Installation](#installation)
   - [Linux](#linux-installation)
   - [Windows](#windows-installation)
3. [SSH Key Setup](#ssh-key-setup)
4. [Configuration](#configuration)
5. [Running the Bot](#running-the-bot)
6. [Troubleshooting](#troubleshooting)

## Telegram Setup <a name="telegram-setup"></a>

### Create a New Bot
1. Open Telegram and find `@BotFather`
2. Send `/newbot` command
3. Follow instructions to:
   - Set bot name (e.g., "MikroTik Manager")
   - Set bot username (must end with `bot`, e.g., "MikroTikManagerBot")
4. Save your bot token (format: `123456789:ABCdefGHIJKlmNoPQRsTUVwxyZ-abcdef123`)

### Configure Bot Settings
```bash
/setprivacy - Disable for command access
/setdescription - Add bot description
/setcommands - Add supported commands
