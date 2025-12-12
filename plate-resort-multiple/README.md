# Plate Resort - Quick Setup Guide

Control laboratory plate handling hardware from your computer.

## Setup Steps

### 1. Get the API Key
SSH into the Pi and get the key:
```bash
ssh your_username@pi_ip_address
cd ~/plate-RESORT/plate-resort-multiple
plate-resort-rest-server
```
Copy the API key shown, then press `Ctrl+C`.

### 2. Install on Your Computer
```bash
git clone https://github.com/AccelerationConsortium/plate-RESORT.git
cd plate-RESORT/plate-resort-multiple
pip install -e .
```

### 3. Set Connection Info
**Windows:**
```cmd
set PLATE_RESORT_API_KEY=your-api-key-here
set PLATE_RESORT_URL=http://pi-ip-address:8000
```

**Mac/Linux:**
```bash
export PLATE_RESORT_API_KEY="your-api-key-here"
export PLATE_RESORT_URL="http://pi-ip-address:8000"
```

### 4. Start the Pi Server
SSH back to Pi:
```bash
plate-resort-rest-server
```
Keep this running.

## Commands

**Check status:**
```bash
plate-resort-rest-client status
```

**Move to hotel:**
```bash
plate-resort-rest-client activate A  # or B, C, D
```

**Go home:**
```bash
plate-resort-rest-client home
```

**Emergency stop:**
```bash
plate-resort-rest-client stop
```

## Troubleshooting

- **Connection refused:** Check Pi server is running and IP address is correct
- **Authentication failed:** Double-check your API key  
- **Motor issues:** SSH to Pi and run `python tests/soft_reset.py`

## For GUI Development

All commands return JSON responses. Use any programming language to build your interface:
- Python (tkinter, PyQt, Streamlit)
- Web (HTML/JavaScript) 
- LabVIEW, MATLAB, etc.

Choose your interface mode based on your needs. Both modes can run on the same Raspberry Pi if needed.

## 2A. Prefect Interface Setup (Recommended)

### 2A.1 Raspberry Pi (Worker Host)
```bash
export PREFECT_API_URL="https://api.prefect.cloud/api/accounts/<account-id>/workspaces/<workspace-id>"
export PREFECT_API_KEY="pnu_XXXXXXXXXXXXXXXX"

python3 -m venv plate-resort-env
source plate-resort-env/bin/activate
pip install -e .
plate-resort-prefect-deploy     # registers deployments
plate-resort-prefect-worker    # starts Prefect worker
```
Optional systemd (adjust path/username):
```bash
sudo cp deployment/plate-resort.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now plate-resort.service
```
Environment file (example): `/home/<user>/plate-RESORT/secrets.local.env`
```
PREFECT_API_URL=...
PREFECT_API_KEY=...
PLATE_RESORT_POOL=plate-resort-pool
```

### 2A.2 Client Machine
Two supported approaches:
1. Interactive CLI (`plate-resort-prefect-interactive --remote`)
2. Minimal script (`plate_resort/client/example_prefect_client.py` pattern)

Install only what’s needed:
```bash
python -m venv plate-resort-client
source plate-resort-client/bin/activate
pip install -r client-requirements.txt
```
Export credentials (or source `plate_resort/client/env.sh` after editing IDs):
```bash
source plate_resort/client/env.sh   # edit placeholders first
```
Verify a deployment submission:
```bash
python -c "from plate_resort.interfaces.prefect import orchestrator; print(orchestrator.connect())"
```

## 2B. REST API Interface Setup (Traditional)

### 2B.1 Raspberry Pi (Server Host)
```bash
python3 -m venv plate-resort-env
source plate-resort-env/bin/activate
pip install -e .
plate-resort-keygen                 # generate API key
plate-resort-rest-server           # start FastAPI server
```
The server runs on port 8000 by default. API documentation available at `http://<pi-ip>:8000/docs`

### 2B.2 Client Machine  
```bash
python -m venv plate-resort-client
source plate-resort-client/bin/activate
pip install -e .
export PLATE_RESORT_BASE_URL="http://<pi-ip>:8000"
export PLATE_RESORT_API_KEY="<generated-key>"
plate-resort-rest-client --help    # see available commands
```

Example REST usage:
```bash
# Connect and activate hotel
plate-resort-rest-client connect
plate-resort-rest-client activate A
plate-resort-rest-client position
plate-resort-rest-client disconnect
```

## 3. Client Usage (Prefect Interface)

### 3.1 Interactive CLI
```bash
plate-resort-prefect-interactive --remote
```
Commands:
```
connect | activate <A|B|C|D> | position | stop | disconnect | help | exit
```

### 3.2 Example Script (A -> D)
```bash
python plate_resort/client/example_prefect_client.py
```
That script: activates hotel A, waits, then activates hotel D with state checks.

### 3.3 Direct Orchestrator Calls
```python
from plate_resort.interfaces.prefect import orchestrator
run = orchestrator.activate_hotel("A")
state = orchestrator.wait(run)
print(state.type)
```

## 4. Deployments & Redeploy (Prefect Interface)
Run on Pi whenever code changes:
```bash
plate-resort-prefect-deploy
```
This re-registers function-based flows with Prefect Cloud using the current working tree (Git storage reference if configured).

Pinning / ensuring correct source:

Option A (branch ref):
```bash
export PLATE_RESORT_GIT_REF=copilot/replace-rest-api-with-prefect
plate-resort-prefect-deploy
```
Option B (commit hash, reproducible) – recommended; resolved prior path issues during testing:
```bash
export PLATE_RESORT_GIT_COMMIT=$(git rev-parse HEAD)
plate-resort-prefect-deploy
```
Commit pin (Option B) takes precedence over branch ref and guarantees the worker loads the exact code you just validated.

## 5. Available Flows
All in `plate_resort/interfaces/prefect/flows.py`:
```
connect, disconnect, activate_hotel, move_to_angle,
get_current_position, get_motor_health, go_home,
emergency_stop, set_speed
```
Remote submission uses deployment names of form `flow-name/flow-name` (e.g. `activate-hotel/activate-hotel`).

## 6. Behavior Notes
* Motor connection is re-established per flow if needed and left active afterward (persistent torque).
* Use `disconnect` flow to deliberately release torque/close port.
* `orchestrator.wait()` polls Prefect for a final state.

## 7. Configuration
Search path includes packaged defaults plus optional override directory: `~/plate-resort-config/`.

`defaults.yaml` (excerpt):
```yaml
resort:
  device: "/dev/ttyUSB0"
  hotels: ["A", "B", "C", "D"]
prefect:
  work_pool_name: "plate-resort-pool"  # Overridden by PLATE_RESORT_POOL
```

To override: create `~/plate-resort-config/defaults.yaml` with keys you want to change; unspecified values fall back to packaged defaults.

## 8. Minimal Client Assets
* `client-requirements.txt` – pins `prefect` + `pyyaml` (add `dynamixel-sdk` only if talking directly to hardware from client).
* `plate_resort/client/env.sh` – template for exporting Prefect API variables.
* `plate_resort/client/example_prefect_client.py` – sequential A -> D example.

## 9. Troubleshooting
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Flow run stays SCHEDULED | Worker not running or wrong pool | Start worker; confirm pool name or set PLATE_RESORT_POOL |
