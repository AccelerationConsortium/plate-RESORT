# Plate Resort – Prefect Workflow Control

Minimal Prefect-based orchestration for the Plate Resort device. REST & keygen paths were removed; all actions are discrete Prefect flows.

---

## 1. Overview
Single‑purpose flows (connect, activate_hotel, move_to_angle, etc.) run on a Raspberry Pi worker while clients (any machine) submit them via Prefect Cloud. Motor torque stays engaged between flows until an explicit disconnect.

## 2. Quick Start

### 2.1 Raspberry Pi (Worker Host)
```bash
export PREFECT_API_URL="https://api.prefect.cloud/api/accounts/<account-id>/workspaces/<workspace-id>"
export PREFECT_API_KEY="pnu_XXXXXXXXXXXXXXXX"

python3 -m venv plate-resort-env
source plate-resort-env/bin/activate
pip install -e .
plate-resort-deploy              # registers deployments
prefect worker start --pool ${PLATE_RESORT_POOL:-plate-resort-pool}
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

### 2.2 Client Machine
Two supported approaches:
1. Interactive CLI (`plate-resort-interactive --remote`)
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
python -c "from plate_resort.workflows import orchestrator; print(orchestrator.connect())"
```

## 3. Client Usage

### 3.1 Interactive CLI
```bash
plate-resort-interactive --remote
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
from plate_resort.workflows import orchestrator
run = orchestrator.activate_hotel("A")
state = orchestrator.wait(run)
print(state.type)
```

## 4. Deployments & Redeploy
Run on Pi whenever code changes:
```bash
plate-resort-deploy
```
This re-registers function-based flows with Prefect Cloud using the current working tree (Git storage reference if configured).

Pinning / ensuring correct source:

Option A (branch ref):
```bash
export PLATE_RESORT_GIT_REF=copilot/replace-rest-api-with-prefect
plate-resort-deploy
```
Option B (commit hash, reproducible) – recommended; resolved prior path issues during testing:
```bash
export PLATE_RESORT_GIT_COMMIT=$(git rev-parse HEAD)
plate-resort-deploy
```
Commit pin (Option B) takes precedence over branch ref and guarantees the worker loads the exact code you just validated.

## 5. Available Flows
All in `plate_resort/workflows/flows.py`:
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
| ModuleNotFoundError (dynamixel_sdk) | Missing dependency in worker venv | Activate worker venv, install package: `pip install dynamixel-sdk` |
| CLI exits immediately | Entry point cannot import (stale install) | Reinstall editable or upgrade to latest version |
| Permission error on serial | User lacks dialout/tty group | Add user to relevant group, re-login |

## 10. Development
Editable install on Pi:
```bash
pip install -e .
```
Redeploy after changes:
```bash
plate-resort-deploy
```

## 11. Versioning
See `CHANGELOG.md` for semantic version increments. Deployment uses whichever version you installed/published; Git commit pinning handled via environment (if implemented for storage).

## 12. License
MIT (see project metadata).

---
*Lean Prefect flow orchestration for Plate Resort.*