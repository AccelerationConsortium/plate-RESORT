# Deployment: persistent worker systemd unit

This folder contains a sample systemd unit to run the repository's persistent Prefect worker (the custom Python worker implemented at `plate_resort.workflows.worker_service`) on a Raspberry Pi.

Key points
- The unit expects an EnvironmentFile at `/home/ac/plate-RESORT/secrets.local.env` containing at least:
  - PREFECT_API_URL=...
  - PREFECT_API_KEY=...
  - PREFECT_CLI_PROMPT=false
- A Python virtualenv is expected at `/home/ac/plate-RESORT/plate-resort-env`. Adjust paths if your venv lives elsewhere.

Install steps (run on the Pi as a user with sudo):

1) Copy the unit file to systemd

```bash
sudo cp /home/ac/plate-RESORT/deployment/plate-resort.service /etc/systemd/system/plate-resort.service
sudo chown root:root /etc/systemd/system/plate-resort.service
sudo chmod 644 /etc/systemd/system/plate-resort.service
```

2) Ensure your secrets file exists and is correct (example)

```bash
cat > /home/ac/plate-RESORT/secrets.local.env <<EOF
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/<ACCOUNT>/workspaces/<WORKSPACE>
PREFECT_API_KEY=<YOUR_API_KEY>
PREFECT_CLI_PROMPT=false
EOF
sudo chown ac:ac /home/ac/plate-RESORT/secrets.local.env
chmod 600 /home/ac/plate-RESORT/secrets.local.env
```

3) Reload systemd and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now plate-resort.service
```

4) Watch logs

```bash
sudo journalctl -u plate-resort.service -f
```

5) If it still exits with prompts or errors, run the ExecStart command manually while the venv is activated to reproduce

```bash
su - ac
source /home/ac/plate-RESORT/plate-resort-env/bin/activate
python -m plate_resort.workflows.worker_service
```

If you want the unit to run the Prefect CLI worker instead, edit `ExecStart` to include your desired pool name or use the environment variable `PLATE_RESORT_POOL` in your EnvironmentFile. Example using an explicit pool name:

```text
ExecStart=/bin/bash -lc 'source /home/ac/plate-RESORT/plate-resort-env/bin/activate && exec prefect worker start --pool "plate-resort-pool" --type process --install-policy if-not-present'
```

Or set `PLATE_RESORT_POOL` in `/home/ac/plate-RESORT/secrets.local.env` and use the custom Python worker (recommended) which will pick it up automatically.

Note: the custom Python worker is recommended for hardware persistence because it maintains a single PlateResort instance across runs.
