#!/usr/bin/env python3
"""
Update command for plate-resort package
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, 
                              text=True)
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
    print("🚀 Updating Plate Resort Server...")
    
    # GitHub repository URL
    repo_url = ("git+https://github.com/AccelerationConsortium/"
                "plate-RESORT.git#subdirectory=plate-resort-multiple")
    
    # Update from GitHub
    update_cmd = f"pip install --upgrade {repo_url}"
    
    if not run_command(update_cmd, "Installing latest version from GitHub"):
        return False
    
    # Restart systemd service if it exists
    service_path = "/etc/systemd/system/plate-resort-server.service"
    if os.path.exists(service_path):
        print("\n🔄 Restarting server service...")
        restart_cmd = "sudo systemctl restart plate-resort-server"
        status_cmd = "sudo systemctl status plate-resort-server --no-pager"
        
        if run_command(restart_cmd, "Restarting service"):
            run_command(status_cmd, "Checking service status")
        else:
            print("⚠️  Could not restart service automatically.")
            print("   Please run: sudo systemctl restart plate-resort-server")
    else:
        print("\n💡 No systemd service found.")
        print("   If you're running the server manually, please restart it.")
    
    print("\n✅ Update complete!")
    print("🔍 You can test the new features:")
    print("   plate-resort-client position")
    print("   plate-resort-client move 90")
    
    return True


if __name__ == "__main__":
    if not main():
        sys.exit(1)