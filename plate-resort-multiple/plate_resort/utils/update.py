#!/usr/bin/env python3
"""
Update utilities for plate-resort package
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        if result.stdout.strip():
            print(f"   {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Update plate-resort to latest version"""
    print("🚀 Updating Plate Resort...")

    # GitHub repository URL for Prefect branch
    repo_url = (
        "git+https://github.com/AccelerationConsortium/"
        "plate-RESORT.git@copilot/replace-rest-api-with-prefect"
        "#subdirectory=plate-resort-multiple"
    )

    # Update from GitHub
    update_cmd = f"pip install --upgrade {repo_url}"

    if not run_command(update_cmd, "Installing latest version from GitHub"):
        return False

    print("\n✅ Update complete!")
    print("🔍 Test the Prefect workflows:")
    print("   python -m plate_resort.workflows.deploy")
    print("   python -m plate_resort.workflows.worker_service")

    return True


if __name__ == "__main__":
    if not main():
        sys.exit(1)
