#!/usr/bin/env python3
"""
Update script for plate-resort server
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

def update_plate_resort():
    """Update plate-resort to latest version"""
    print("🚀 Updating Plate Resort Server...")
    
    # Update from GitHub
    update_cmd = "pip install --upgrade git+https://github.com/AccelerationConsortium/plate-RESORT.git#subdirectory=plate-resort-multiple"
    
    if not run_command(update_cmd, "Installing latest version from GitHub"):
        return False
    
    # Restart systemd service if it exists
    if os.path.exists("/etc/systemd/system/plate-resort-server.service"):
        print("\n🔄 Restarting server service...")
        if run_command("sudo systemctl restart plate-resort-server", "Restarting service"):
            run_command("sudo systemctl status plate-resort-server --no-pager", "Checking service status")
        else:
            print("⚠️  Could not restart service automatically. Please run:")
            print("   sudo systemctl restart plate-resort-server")
    else:
        print("\n💡 No systemd service found. If you're running the server manually, please restart it.")
    
    print("\n✅ Update complete!")
    print("🔍 You can test the new features:")
    print("   plate-resort-client position")
    print("   plate-resort-client move 90")
    
    return True

if __name__ == "__main__":
    if not update_plate_resort():
        sys.exit(1)