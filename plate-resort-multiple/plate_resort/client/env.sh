#!/usr/bin/env bash
# Export required Prefect Cloud environment variables for client usage.
# Usage: source env.sh

export PREFECT_API_URL="https://api.prefect.cloud/api/accounts/<ACCOUNT_ID>/workspaces/<WORKSPACE_ID>"
export PREFECT_API_KEY="pnu_XXXXXXXXXXXXXXXX"
# Optional work pool override
export PLATE_RESORT_POOL="plate-resort-pool"

echo "Prefect environment variables exported."
