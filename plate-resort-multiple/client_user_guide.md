# Plate Resort REST API Client User Guide

This guide shows you how to control the Plate Resort from your computer using the REST API. The Raspberry Pi hardware is already set up - you just need to install the client software.

## Step 1: Get the API Key from the Pi

SSH into the Raspberry Pi to get your access key:

```bash
ssh your_username@pi_ip_address
cd ~/plate-RESORT/plate-resort-multiple
```

Check if the server is running:
```bash
plate-resort-rest-server
```

You'll see something like:
```
🔑 API Key: Xp9mK3vR8qL2nBw7cF4jY1eH6sD0zM5t
```

**Copy this key** - you'll need it later. Press `Ctrl+C` to stop.

## Step 2: Install Client Software

On your computer, install the software:

```bash
git clone https://github.com/AccelerationConsortium/plate-RESORT.git
cd plate-RESORT/plate-resort-multiple
pip install -e .
```

## Step 3: Configure Your Connection

Set your connection details:

**Windows:**
```cmd
set PLATE_RESORT_API_KEY=Xp9mK3vR8qL2nBw7cF4jY1eH6sD0zM5t
set PLATE_RESORT_URL=http://sdl3-pi5-plate-resort.tail6a1dd7.ts.net:8000
```

**Mac/Linux:**
```bash
export PLATE_RESORT_API_KEY="Xp9mK3vR8qL2nBw7cF4jY1eH6sD0zM5t"
export PLATE_RESORT_URL="http://sdl3-pi5-plate-resort:8000"
```

Replace the hostname with your Pi's actual hostname or IP address.

## Step 4: Start the Pi Server

SSH back to the Pi and start the server:
```bash
plate-resort-rest-server
```
Leave this running while you use the system.

## Control Commands

Now you can control the Plate Resort from your computer:

| Command | Purpose | Example |
|---------|---------|---------|
| `connect` | Connect to the motor | `plate-resort-rest-client connect` |
| `status` | Check if everything is working | `plate-resort-rest-client status` |
| `position` | Get current position | `plate-resort-rest-client position` |
| `activate` | Move to hotel A, B, C, or D | `plate-resort-rest-client activate A` |
| `move` | Move to specific angle | `plate-resort-rest-client move 90.0` |
| `home` | Return to home position | `plate-resort-rest-client home` |
| `stop` | Emergency stop | `plate-resort-rest-client stop` |
| `health` | Check motor health | `plate-resort-rest-client health` |
| `disconnect` | Disconnect from motor | `plate-resort-rest-client disconnect` |



## Troubleshooting

**401 Authentication Error:** Check your API key is correct and matches exactly

**500 Server Error:** Hardware fault detected - SSH to Pi and run `python tests/soft_reset.py`

**Can't connect:** Check that Pi and client are both on the same network and online

**Motor configuration adjustments:** Edit `plate_resort/config/defaults.yaml` file on the Pi for motor control settings