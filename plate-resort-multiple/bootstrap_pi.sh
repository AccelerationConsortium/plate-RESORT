#!/usr/bin/env bash
set -euo pipefail

# Minimal bootstrap for a fresh Raspberry Pi image to run Plate Resort with Prefect Cloud.
# Assumptions:
# - User cloned repo to ~/plate-resort/plate-resort-multiple OR will clone now.
# - Work pool 'plate-resort-pool' already exists in Prefect Cloud.
# - PREFECT_API_KEY and PREFECT_API_URL provided via environment or arguments.
#
# Usage:
#   ./bootstrap_pi.sh --api-key YOUR_KEY \
#       --api-url https://api.prefect.cloud/api/accounts/<acct>/workspaces/<ws> \
#       [--device /dev/ttyUSB0 --baud 57600 --motor 1]
#
# The script will:
#   1. Ensure required packages (git, python3, venv) exist.
#   2. Clone or update the repository.
#   3. Create a virtual environment and install the package editable.
#   4. Export Prefect environment variables.
#   5. Deploy function-based flows.
#   6. Start a Prefect process worker (background tmux session if available).
#   7. Optionally run a quick verification.

DEVICE=""
BAUD=""
MOTOR_ID=""
API_KEY="${PREFECT_API_KEY:-}"
API_URL="${PREFECT_API_URL:-}"
REPO_URL="https://github.com/AccelerationConsortium/plate-RESORT.git"
WORK_POOL="plate-resort-pool"
VENV_DIR="plate-resort-env"
RUN_VERIFY=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api-key) API_KEY="$2"; shift 2;;
    --api-url) API_URL="$2"; shift 2;;
    --device) DEVICE="$2"; shift 2;;
    --baud) BAUD="$2"; shift 2;;
    --motor) MOTOR_ID="$2"; shift 2;;
    --no-verify) RUN_VERIFY=0; shift;;
    --repo) REPO_URL="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$API_KEY" || -z "$API_URL" ]]; then
  echo "ERROR: --api-key and --api-url (or PREFECT_API_KEY/PREFECT_API_URL) required." >&2
  exit 1
fi

echo "[1/7] Checking base system packages" 
command -v git >/dev/null || sudo apt-get update && sudo apt-get install -y git
command -v python3 >/dev/null || { echo "python3 missing"; exit 1; }
python3 -m venv --help >/dev/null || sudo apt-get install -y python3-venv

echo "[2/7] Clone or update repository"
if [[ ! -d plate-RESORT ]]; then
  git clone "$REPO_URL" plate-RESORT
fi
cd plate-RESORT || { echo "Repo directory missing"; exit 1; }
git fetch --quiet
git checkout copilot/replace-rest-api-with-prefect || git checkout main
git pull --ff-only
cd plate_resort || true
cd ..

echo "[3/7] Create / activate virtual environment"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip wheel setuptools
echo "Installing project (editable)"
pip install -e .

echo "[4/7] Export Prefect Cloud environment variables"
export PREFECT_API_KEY="$API_KEY"
export PREFECT_API_URL="$API_URL"
echo "PREFECT_API_URL=$PREFECT_API_URL"

echo "[5/7] Deploy flows to work pool '$WORK_POOL'"
plate-resort-deploy || { echo "Deployment failed"; exit 1; }

echo "[6/7] Start worker (background)"
if command -v tmux >/dev/null; then
  tmux new-session -d -s plate_resort_worker "prefect worker start --pool $WORK_POOL"
  echo "Worker started in tmux session 'plate_resort_worker'"
else
  echo "(Consider installing tmux for background management)"
  prefect worker start --pool "$WORK_POOL" &
fi

if [[ $RUN_VERIFY -eq 1 ]]; then
  echo "[7/7] Verification"
  python verify_prefect.py || echo "Verification script encountered an issue" >&2
fi

echo "Bootstrap complete." 
echo "Next: Run 'plate-resort-interactive --remote' from a workstation to submit flows." 
if [[ -n "$DEVICE" && -n "$BAUD" && -n "$MOTOR_ID" ]]; then
  echo "Example connect: plate-resort-interactive --remote --connect --device $DEVICE --baudrate $BAUD --motor-id $MOTOR_ID"
fi
