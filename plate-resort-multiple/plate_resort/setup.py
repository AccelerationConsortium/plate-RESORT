#!/usr/bin/env python3
"""
Automated setup system for Plate Resort
Handles system dependencies, permissions, and configuration
"""

import os
import sys
import subprocess
import platform
import secrets
import string
import configparser
from pathlib import Path
import pkg_resources


def is_raspberry_pi():
    """Check if running on Raspberry Pi"""
    try:
        with open("/proc/cpuinfo", "r") as f:
            return "Raspberry Pi" in f.read()
    except FileNotFoundError:
        return False


def run_command(cmd, check=True, shell=False):
    """Run system command with error handling"""
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        result = subprocess.run(
            cmd, check=check, capture_output=True, text=True, shell=shell
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except Exception as e:
        return False, "", str(e)


def install_system_dependencies():
    """Install required system packages on Raspberry Pi"""
    if not is_raspberry_pi():
        print("ℹ️  Not on Raspberry Pi - skipping system package installation")
        return True

    print("📦 Installing system dependencies...")

    # Update package list
    success, _, _ = run_command("sudo apt update")
    if not success:
        print("❌ Failed to update package list")
        return False

    # Install required packages
    packages = [
        "python3-dev",
        "build-essential",
        "udev",
        "git",
        "python3-pip",
        "python3-venv",
    ]

    cmd = ["sudo", "apt", "install", "-y"] + packages
    success, _, stderr = run_command(cmd)
    if not success:
        print(f"❌ Failed to install packages: {stderr}")
        return False

    print("✅ System dependencies installed")
    return True


def setup_usb_permissions():
    """Configure USB permissions for Dynamixel devices"""
    if not is_raspberry_pi():
        print("ℹ️  Not on Raspberry Pi - skipping USB permissions setup")
        return True

    print("🔌 Setting up USB permissions...")

    # Add user to dialout group
    username = os.getenv("USER", "pi")
    success, _, _ = run_command(f"sudo usermod -aG dialout {username}")
    if not success:
        print("❌ Failed to add user to dialout group")
        return False

    # Create udev rules
    udev_rules = """# Dynamixel USB devices
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout"
# Generic USB-to-serial adapters
SUBSYSTEM=="tty", KERNEL=="ttyUSB*", MODE="0666", GROUP="dialout"
"""

    rules_file = "/etc/udev/rules.d/99-dynamixel.rules"
    try:
        # Write rules file
        success, _, _ = run_command(f"sudo tee {rules_file}", shell=True, check=False)
        if success:
            with subprocess.Popen(
                ["sudo", "tee", rules_file], stdin=subprocess.PIPE, text=True
            ) as proc:
                proc.communicate(input=udev_rules)

        # Reload udev rules
        run_command("sudo udevadm control --reload-rules")
        run_command("sudo udevadm trigger")

        print("✅ USB permissions configured")
        return True
    except Exception as e:
        print(f"❌ Failed to configure USB permissions: {e}")
        return False


def generate_api_key(length=32):
    """Generate a secure API key"""
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def setup_configuration():
    """Set up configuration files"""
    print("⚙️  Setting up configuration...")

    # Get package data directory
    try:
        # Try to get from installed package
        package_dir = Path(pkg_resources.resource_filename("plate_resort", ""))
    except:
        # Fall back to current directory
        package_dir = Path(__file__).parent.parent

    config_file = package_dir / "resort_config.yaml"
    secrets_file = Path("secrets.ini")

    # Copy default config if it doesn't exist
    if not Path("resort_config.yaml").exists() and config_file.exists():
        import shutil

        shutil.copy(config_file, "resort_config.yaml")
        print("✅ Configuration file copied")

    # Create secrets.ini if it doesn't exist
    if not secrets_file.exists():
        api_key = generate_api_key()

        config = configparser.ConfigParser()
        config["server"] = {"api_key": api_key}
        config["client"] = {"default_host": "localhost", "default_port": "8000"}

        with open(secrets_file, "w") as f:
            config.write(f)

        # Set restrictive permissions
        try:
            os.chmod(secrets_file, 0o600)
        except:
            pass  # Windows doesn't support chmod the same way

        print(f"✅ Secrets file created with API key: {api_key}")
        return api_key
    else:
        # Read existing API key
        config = configparser.ConfigParser()
        config.read(secrets_file)
        api_key = config.get("server", "api_key", fallback="changeme")
        print(f"✅ Using existing API key: {api_key}")
        return api_key


def create_service_files():
    """Create systemd service files for auto-start"""
    if not is_raspberry_pi():
        print("ℹ️  Not on Raspberry Pi - skipping service creation")
        return True

    print("🔄 Creating systemd service...")

    service_content = f"""[Unit]
Description=Plate Resort Server
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'pi')}
WorkingDirectory={os.getcwd()}
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/local/bin/plate-resort-server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    service_file = "/etc/systemd/system/plate-resort.service"
    try:
        with subprocess.Popen(
            ["sudo", "tee", service_file], stdin=subprocess.PIPE, text=True
        ) as proc:
            proc.communicate(input=service_content)

        # Enable service but don't start it yet
        run_command("sudo systemctl daemon-reload")
        run_command("sudo systemctl enable plate-resort")

        print("✅ Systemd service created and enabled")
        return True
    except Exception as e:
        print(f"❌ Failed to create service: {e}")
        return False


def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")

    try:
        # Test import
        from plate_resort import PlateResort

        print("✅ Package import successful")

        # Test client import
        from plate_resort.client import PlateResortClient

        print("✅ Client import successful")

        # Test server import
        from plate_resort.server.main import app

        print("✅ Server import successful")

        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


def setup_system():
    """Main setup function"""
    print("🚀 Plate Resort System Setup")
    print("=" * 40)

    success = True

    # Install system dependencies
    if not install_system_dependencies():
        success = False

    # Setup USB permissions (usually not needed on modern systems)
    # if not setup_usb_permissions():
    #     success = False

    # Setup configuration
    api_key = setup_configuration()

    # Create service files
    if not create_service_files():
        success = False

    # Test installation
    if not test_installation():
        success = False

    print("\n" + "=" * 40)
    if success:
        print("✅ Setup completed successfully!")
        print(f"\n� Your API key: {api_key}")
        
        if is_raspberry_pi():
            # USB permissions usually work by default on modern Pi OS
            print("\n📋 Note: USB permissions typically work automatically")
            print("- User is likely already in 'dialout' group")
            print("- Modern systems set USB devices as world-writable")
            
        # Start server immediately
        print("\n🚀 Starting Plate Resort Server...")
        start_server_now()

        print("\n📖 Documentation: http://localhost:8000/docs")
        print("🔧 Test connection: plate-resort-client --help")

    else:
        print("❌ Setup completed with errors")
        print("Please check the error messages above")
        return 1

    return 0


def start_server_now():
    """Start the server immediately"""
    print("\n🚀 Starting Plate Resort Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        # Import and run the server
        from plate_resort.server.main import run_server
        run_server()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")
        print("💡 Try manually: plate-resort-server")


if __name__ == "__main__":
    sys.exit(setup_system())
