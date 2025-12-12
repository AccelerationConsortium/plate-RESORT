# Plate Resort Client User Guide

This guide shows you how to control the Plate Resort from your computer. The Raspberry Pi hardware is already set up - you just need to install the client software.

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
set PLATE_RESORT_URL=http://192.168.1.100:8000
```

**Mac/Linux:**
```bash
export PLATE_RESORT_API_KEY="Xp9mK3vR8qL2nBw7cF4jY1eH6sD0zM5t"
export PLATE_RESORT_URL="http://192.168.1.100:8000"
```

Replace the IP address with your Pi's actual IP address.

## Step 4: Start the Pi Server

SSH back to the Pi and start the server:
```bash
plate-resort-rest-server
```
Leave this running while you use the system.

## Control Commands

Now you can control the Plate Resort from your computer:

**Check if everything is working:**
```bash
plate-resort-rest-client status
```

**Move to a specific hotel position:**
```bash
plate-resort-rest-client activate A
plate-resort-rest-client activate B
plate-resort-rest-client activate C
plate-resort-rest-client activate D
```

**Return to home position:**
```bash
plate-resort-rest-client home
```

**Emergency stop:**
```bash
plate-resort-rest-client stop
```

**Check motor health:**
```bash
plate-resort-rest-client health
```

## Building Your Own Interface

These commands return simple JSON responses that you can use in any programming language to build a custom interface:

- **Python**: Use tkinter, PyQt, or Streamlit
- **Web**: HTML/JavaScript 
- **LabVIEW**: HTTP request functions
- **MATLAB**: webread/webwrite functions

Each command sends an HTTP request to the Pi and gets back a JSON response with the results.

## Troubleshooting

**Can't connect:** Make sure the Pi server is running and you're using the correct IP address

**Authentication error:** Double-check your API key matches exactly

**Motor issues:** SSH to the Pi and run `python tests/soft_reset.py`