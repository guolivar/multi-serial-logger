# Deployment Guide (Raspberry Pi / Linux)

This guide covers deployment considerations for running the `multi-serial-logger` on a Raspberry Pi or similar Linux system.

## 1. Prerequisites

### Serial Port Permissions
By default, standard users (like `pi`) do not have permission to access serial ports. You must add your user to the `dialout` group.

```bash
sudo usermod -a -G dialout $USER
```
*You will need to log out and log back in for this to take effect.*

### Device Names
On Raspberry Pi, serial ports usually appear as:
- `/dev/ttyUSB0`, `/dev/ttyUSB1` (USB-to-Serial adapters)
- `/dev/ttyACM0` (some Arduinos/modems)
- `/dev/serial0` (Built-in UART on GPIO)

You can list connected devices with:
```bash
ls -l /dev/ttyUSB* /dev/ttyACM*
```

## 2. Setting Up a Dedicated Service

To ensure the logger runs automatically at boot and restarts if it crashes, use `systemd`.

### Step 1: Install the package
Install the package system-wide or in a virtual environment. We recommend a virtual environment.

```bash
# Create directory
mkdir -p /home/pi/logger_project
cd /home/pi/logger_project

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install the package (assuming you cloned the repo here or installed via pip)
pip install git+https://github.com/guolivar/multi-serial-logger.git
# OR if you have the source locally
pip install .
```

### Step 2: Create Configuration
Create your `settings.txt` in `/home/pi/logger_project/settings.txt` (see README for format).

### Step 3: Create Service File
Create a file named `/etc/systemd/system/multi-serial-logger.service`:

```ini
[Unit]
Description=Multi Serial Logger Service
After=network.target

[Service]
# User to run as (ensure this user is in dialout group)
User=pi
Group=pi

# working directory where settings.txt and logs will operate
WorkingDirectory=/home/pi/logger_project

# Path to the executable within the virtual environment
ExecStart=/home/pi/logger_project/venv/bin/multi-serial-logger --config settings.txt

# Restart options
Restart=always
RestartSec=10

# Capture stdout/stderr in journal
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Step 4: Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable multi-serial-logger
sudo systemctl start multi-serial-logger
```

### Step 5: View Logs
To check the status and see output:
```bash
sudo systemctl status multi-serial-logger
journalctl -u multi-serial-logger -f
```

## 3. Power Management
If you are using USB-to-Serial adapters, ensure that USB power saving is disabled on the Pi to prevent disconnection issues, though this is less common on modern kernels.
