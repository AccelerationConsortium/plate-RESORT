# Raspberry Pi: venv + Prefect setup (interactive convenience)

This document records the steps we used in the repo to prepare a Raspberry Pi to run the Plate-RESORT worker and to interact with Prefect from the Pi.

It focuses on two related goals:
- create and use a Python virtualenv that contains Prefect and the `plate-resort` package
- make it easy to run Prefect CLI commands interactively on the Pi (convenience auto-activation)

These steps assume a clone of the repository at `/home/ac/plate-RESORT` and that the service will use a venv at `/home/ac/plate-RESORT/plate-resort-env`. Adjust paths if your setup differs.

## 1 — System packages (minimal)
Install system packages on a fresh Pi:

```bash
sudo apt update
sudo apt install -y git python3-venv python3-pip build-essential
```

## 2 — Clone the repository

```bash
cd /home/ac
git clone https://github.com/AccelerationConsortium/plate-RESORT.git
cd plate-RESORT
git fetch origin
git checkout copilot/replace-rest-api-with-prefect
```

## 3 — Create the venv and install the package

We recommend creating a dedicated venv for the project. This keeps dependencies isolated and makes it easy for systemd to run the correct interpreter.

```bash
cd /home/ac/plate-RESORT
python3 -m venv plate-resort-env
source plate-resort-env/bin/activate
pip install --upgrade pip
# editable install so console scripts are available
pip install -e .
```

After this, the venv contains Prefect (pinned to `3.4.23` via `pyproject.toml`) and the `plate-resort` entry points.

## 4 — Secrets & environment variables

Store Prefect credentials and other env vars in a single file that both interactive shells and systemd can use. Create `/home/ac/plate-RESORT/secrets.local.env` with:

```bash
cat > /home/ac/plate-RESORT/secrets.local.env <<EOF
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/<ACCOUNT>/workspaces/<WORKSPACE>
PREFECT_API_KEY=<YOUR_API_KEY>
PREFECT_CLI_PROMPT=false
EOF

chown ac:ac /home/ac/plate-RESORT/secrets.local.env
chmod 600 /home/ac/plate-RESORT/secrets.local.env
```

Notes:
- `PREFECT_CLI_PROMPT=false` prevents any interactive CLI prompts (important for non-interactive systemd usage).
- Keep this file untracked (do not add to git); treat it as a local secret store.

## 5 — Convenience: auto-activate the venv in your interactive shells

If you frequently SSH into the Pi and want your interactive shell to have the venv active automatically, add the following to `~/.bashrc` (for user `ac`):

```bash
# Auto-activate plate-resort venv for interactive shells
if [ -n "$PS1" ] && [ -d "/home/ac/plate-RESORT/plate-resort-env" ]; then
  # export vars from secrets.local.env without printing
  if [ -f /home/ac/plate-RESORT/secrets.local.env ]; then
    set -a
    source /home/ac/plate-RESORT/secrets.local.env
    set +a
  fi
  source /home/ac/plate-RESORT/plate-resort-env/bin/activate
fi
```

This makes interactive sessions convenient: `prefect` and project console scripts are immediately available. Note this is strictly for interactive convenience only — systemd will not rely on `~/.bashrc`.

## 6 — Systemd / service note (non-interactive)

For services, do NOT rely on shell activation. Instead, use the venv python directly in the unit file. Example ExecStart:

```ini
ExecStart=/home/ac/plate-RESORT/plate-resort-env/bin/python -m plate_resort.workflows.worker_service
EnvironmentFile=/home/ac/plate-RESORT/secrets.local.env
Environment=PREFECT_CLI_PROMPT=false
```

This is robust and ensures the service uses the same environment as your interactive venv.

## 7 — Using Prefect on the Pi (examples)

Run from an activated shell (convenient):

```bash
source /home/ac/plate-RESORT/plate-resort-env/bin/activate
# optionally source secrets so envs are present
set -a; source /home/ac/plate-RESORT/secrets.local.env; set +a

# list available deployments
prefect deployment ls

# run a deployment by name and watch logs
prefect deployment run my-flow/my-deployment --watch

# run by id
prefect deployment run --id <DEPLOYMENT-ID> --watch
```

Run without activation (explicit venv python — reproducible):

```bash
/home/ac/plate-RESORT/plate-resort-env/bin/python -m prefect deployment run my-flow/my-deployment --watch
```

Run the local package CLI scripts (installed by `pip install -e .`) without activation:

```bash
/home/ac/plate-RESORT/plate-resort-env/bin/plate-resort-worker
# or via python -m
/home/ac/plate-RESORT/plate-resort-env/bin/python -m plate_resort.workflows.worker_service
```

## 8 — Quick health checks

Use `systemctl` and `journalctl` when diagnosing service behavior:

```bash
sudo systemctl status plate-resort.service
sudo journalctl -u plate-resort.service -f
```

## 9 — Reboot behavior

If the systemd unit is enabled, the worker will start automatically on reboot. After reboot, confirm with `systemctl status` and `journalctl`.

## 10 — Troubleshooting

- If `prefect` is not found in an interactive shell, either activate the venv or call the venv python as shown above.
- If the service prompts or aborts, ensure `PREFECT_CLI_PROMPT=false` is set in the env file and that the unit uses the venv python directly.
- If a flow run fails with hardware errors, run the same code manually from an activated venv to get full tracebacks and hardware logs.

---

This document mirrors the steps we used in our working session and can be copied to other Pi targets. If you want, I can add a single `provision_pi.sh` script that automates everything (clone, venv, install, unit copy, enable). Want that next?
