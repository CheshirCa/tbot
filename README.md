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

Installation <a name="installation"></a>
Linux Installation <a name="linux-installation"></a>
Dependencies
bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv libffi-dev libssl-dev -y
Setup Virtual Environment
bash
mkdir ~/mikrotik_bot && cd ~/mikrotik_bot
python3 -m venv venv
source venv/bin/activate
pip install python-telegram-bot paramiko cryptography
Systemd Service (Auto-start)
Create /etc/systemd/system/mikrotik-bot.service:

ini
[Unit]
Description=MikroTik Telegram Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/mikrotik_bot
ExecStart=/home/ubuntu/mikrotik_bot/venv/bin/python3 /home/ubuntu/mikrotik_bot/tbot.py
Restart=always

[Install]
WantedBy=multi-user.target
Enable service:

bash
sudo systemctl daemon-reload
sudo systemctl enable mikrotik-bot
sudo systemctl start mikrotik-bot
Windows Installation <a name="windows-installation"></a>
Install Python 3.10+ from python.org

Check "Add Python to PATH" during installation

Install dependencies:

cmd
pip install python-telegram-bot paramiko cryptography
Create startup script (start_bot.bat):

bat
@echo off
cd C:\mikrotik_bot
python tbot.py
SSH Key Setup <a name="ssh-key-setup"></a>
Generate SSH Keys
bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/mikrotik_bot_key
Configure MikroTik
bash
/user add name=tbot group=full disabled=no
/user ssh-keys import public-key-file=bot_key.pub user=tbot
/ip service set ssh disabled=no port=22 address=192.168.0.0/24
Test Connection
bash
ssh -i ~/.ssh/mikrotik_bot_key tbot@192.168.0.1
Configuration <a name="configuration"></a>
Edit tbot.py with your settings:

python
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
MIKROTIK_IP = "192.168.0.1"
MIKROTIK_USER = "tbot"
SSH_KEY_PATH = "/path/to/your/private_key"
REBOOT_PASSWORD = "secure_password_here"
ALLOWED_USERS = {
    111111111: "Admin",
    "username": "Operator"
}
Running the Bot <a name="running-the-bot"></a>
Linux
bash
sudo systemctl start mikrotik-bot  # Start
sudo systemctl stop mikrotik-bot   # Stop
tail -f logs/bot.log              # View logs
Windows
cmd
python tbot.py  # Run manually
Troubleshooting <a name="troubleshooting"></a>
Error	Solution
Telegram connection issues	Verify token, check internet connection
SSH authentication failed	Verify key path, check MikroTik user permissions
Module not found	Run pip install -r requirements.txt
Command not working	Check RouterOS version compatibility
Important Security Note: Always change the default reboot password after setup!
