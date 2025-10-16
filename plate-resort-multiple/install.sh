#!/usr/bin/env bash
set -euo pipefail

# Plate Resort Installer (Prefect workflows)
# Assumes PREFECT_API_URL and PREFECT_API_KEY already exported by the user.
# Usage:
#   export PREFECT_API_URL=... PREFECT_API_KEY=... && \
#   curl -fsSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/copilot/replace-rest-api-with-prefect/plate-resort-multiple/install.sh | bash
# Optional flags:
#   --no-auto-activate          Skip adding venv auto-activation to ~/.bashrc
#   --editable                  Install package editable (clone + pip install -e .)
#   --pool NAME                 Override work pool name (default: plate-resort-pool)
#   --force-refresh             Remove venv & reinstall (fresh clone of package)
#   --ref <branch|tag|commit>   Override git ref (default: copilot/replace-rest-api-with-prefect)

POOL="plate-resort-pool"
AUTO_ACTIVATE=1
EDITABLE=0
FORCE_REFRESH=0
GIT_REF="copilot/replace-rest-api-with-prefect"

while [[ $# -gt 0 ]]; do
    case "$1" in
    --no-auto-activate) AUTO_ACTIVATE=0; shift;;
    --editable) EDITABLE=1; shift;;
    --pool) POOL="$2"; shift 2;;
    --force-refresh) FORCE_REFRESH=1; shift;;
    --ref) GIT_REF="$2"; shift 2;;
        *) echo "Unknown flag: $1"; exit 1;;
    esac
done

echo "🚀 Plate Resort - Prefect Installer"

# Require Prefect Cloud environment variables before any installation so flows can deploy immediately.
if [[ -z "${PREFECT_API_URL:-}" || -z "${PREFECT_API_KEY:-}" ]]; then
    echo "❌ PREFECT_API_URL and PREFECT_API_KEY must be exported before running this installer." >&2
    echo "   Example: export PREFECT_API_URL=https://api.prefect.cloud/api/accounts/<acct>/workspaces/<ws>" >&2
    echo "            export PREFECT_API_KEY=pnu_XXXXXXXX" >&2
    exit 1
fi

command -v python3 >/dev/null || { echo "Python3 required"; exit 1; }
command -v pip3 >/dev/null || { echo "Installing pip"; sudo apt update && sudo apt install -y python3-pip python3-venv; }

VENV_DIR="$HOME/plate-resort-env"
if [[ $FORCE_REFRESH -eq 1 ]]; then
    echo "♻️  Force refresh requested: deleting existing venv (if any)";
    rm -rf "$VENV_DIR"
fi
if [[ ! -d "$VENV_DIR" ]]; then
    echo "🐍 Creating virtual environment at $VENV_DIR";
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo "📦 Installing plate-resort package (Git ref: $GIT_REF)"
# Bypass pip wheel cache if force refresh requested
if [[ $FORCE_REFRESH -eq 1 ]]; then
    PIP_NO_CACHE_DIR=1 pip install --no-cache-dir --upgrade \
        "git+https://github.com/AccelerationConsortium/plate-RESORT.git@${GIT_REF}#subdirectory=plate-resort-multiple"
else
    pip install --upgrade \
        "git+https://github.com/AccelerationConsortium/plate-RESORT.git@${GIT_REF}#subdirectory=plate-resort-multiple"
fi

if [[ $EDITABLE -eq 1 ]]; then
    echo "🔧 Editable mode requested: cloning repository"
    cd "$HOME"
    if [[ ! -d plate-RESORT ]]; then
        git clone https://github.com/AccelerationConsortium/plate-RESORT.git
    fi
    cd plate-RESORT/plate-resort-multiple
    if [[ $FORCE_REFRESH -eq 1 ]]; then
        PIP_NO_CACHE_DIR=1 pip install --no-cache-dir -e .
    else
        pip install -e .
    fi
fi

if [[ $AUTO_ACTIVATE -eq 1 ]]; then
    if ! grep -Fq "source $VENV_DIR/bin/activate" "$HOME/.bashrc"; then
        echo "# Auto-activate plate-resort venv" >> "$HOME/.bashrc"
        echo "source $VENV_DIR/bin/activate" >> "$HOME/.bashrc"
        echo "✅ Added auto-activation to .bashrc"
    else
        echo "✅ Auto-activation already present"
    fi
fi

echo "✅ Base installation complete"

# Auto deploy & start worker if environment variables present
if [[ -n "${PREFECT_API_URL:-}" && -n "${PREFECT_API_KEY:-}" ]]; then
    echo "🔐 Prefect Cloud environment detected"
    echo "🌐 API URL: $PREFECT_API_URL"
    echo "🚀 Ensuring work pool '$POOL' exists"
    prefect work-pool create --type process "$POOL" 2>/dev/null || true
    echo "📦 Deploying flows"
    plate-resort-deploy || { echo "Deployment failed"; exit 3; }
    echo "🛠 Starting worker (process pool: $POOL)"
    # Start worker in background using nohup; user can manage later.
    nohup prefect worker start --pool "$POOL" >/dev/null 2>&1 &
    echo "✅ Worker started in background (nohup)"
else
    echo "ℹ️ PREFECT_API_URL / PREFECT_API_KEY not set; skipping deploy & worker."
    echo "   Export them and run: prefect work-pool create --type process $POOL; plate-resort-deploy; plate-resort-worker"
fi

echo "ℹ️  Next steps:" 
echo "   plate-resort-interactive            # local device control"
echo "   plate-resort-interactive --remote   # submit to Prefect Cloud deployments"
echo "   plate-resort-deploy                 # (manual redeploy flows)"
echo "   plate-resort-worker                 # start a worker manually (foreground)"
echo "   prefect work-pool ls                # confirm pool exists"
echo "   prefect deployment ls               # view registered deployments"

echo "Done."