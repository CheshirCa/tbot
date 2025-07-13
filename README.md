# tbot
Telegram Bot for MikroTik Management

A Telegram bot for managing MikroTik routers via SSH with secure key-based authentication.

=== Table of Contents ===
1. Telegram Setup
2. Installation
   - Linux
   - Windows
3. SSH Key Setup
4. Configuration
5. Running the Bot
6. Troubleshooting

=== 1. Telegram Setup ===

• Create a New Bot:
  1. Open Telegram and find @BotFather
  2. Send /newbot command
  3. Follow instructions to:
     - Set bot name (e.g., "MikroTik Manager")
     - Set bot username (must end with 'bot')
  4. Save your bot token (format: 123456789:ABCdefGHIJKlmNoPQRsTUVwxyZ-abcdef123)

• Configure Bot Settings:
  /setprivacy - Disable for command access
  /setdescription - Add bot description
  /setcommands - Add supported commands

=== 2. Installation ===

• Linux Installation:
  
  Install Dependencies:
  sudo apt update && sudo apt upgrade -y
  sudo apt install python3 python3-pip python3-venv libffi-dev libssl-dev -y

  Setup Virtual Environment:
  mkdir ~/mikrotik_bot && cd ~/mikrotik_bot
  python3 -m venv venv
  source venv/bin/activate
  pip install python-telegram-bot paramiko cryptography

  Systemd Service (Auto-start):
  Create /etc/systemd/system/mikrotik-bot.service:

  ```[Unit]
  Description=MikroTik Telegram Bot
  After=network.target

  [Service]
  User=ubuntu
  WorkingDirectory=/home/ubuntu/mikrotik_bot
  ExecStart=/home/ubuntu/mikrotik_bot/venv/bin/python3 /home/ubuntu/mikrotik_bot/tbot.py
  Restart=always

  [Install]
  WantedBy=multi-user.target```

  Enable service:
 ``` sudo systemctl daemon-reload
  sudo systemctl enable mikrotik-bot
  sudo systemctl start mikrotik-bot```

• Windows Installation:
  1. Install Python 3.10+ from python.org
  2. Install dependencies:
     pip install python-telegram-bot paramiko cryptography
  3. Create startup script (start_bot.bat):
     ```@echo off
     cd C:\mikrotik_bot
     python tbot.py```

=== 3. SSH Key Setup ===

• Generate SSH Keys:
  ssh-keygen -t rsa -b 4096 -f ~/.ssh/mikrotik_bot_key

• Configure MikroTik:
  /user add name=tbot group=full disabled=no
  /user ssh-keys import public-key-file=bot_key.pub user=tbot
  /ip service set ssh disabled=no port=22 address=192.168.0.0/24

• Test Connection:
  ssh -i ~/.ssh/mikrotik_bot_key tbot@192.168.0.1

=== 4. Configuration ===

Edit tbot.py with your settings:
```TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
MIKROTIK_IP = "192.168.0.1"
MIKROTIK_USER = "tbot"
SSH_KEY_PATH = "/path/to/your/private_key"
REBOOT_PASSWORD = "secure_password_here"
ALLOWED_USERS = {
    111111111: "Admin",
    "username": "Operator"
}```

=== 5. Running the Bot ===

• Linux:
  sudo systemctl start mikrotik-bot  # Start
  sudo systemctl stop mikrotik-bot   # Stop
  tail -f logs/bot.log              # View logs

• Windows:
  python tbot.py  # Run manually

=== 6. Troubleshooting ===

• Telegram connection issues: Verify token, check internet connection
• SSH authentication failed: Verify key path, check MikroTik user permissions
• Module not found: Run pip install -r requirements.txt
• Command not working: Check RouterOS version compatibility

IMPORTANT: Always change the default reboot password after setup!
