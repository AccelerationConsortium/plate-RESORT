#!/usr/bin/env python3
"""
Key generation utilities for Plate Resort system.
Generates secure configuration keys and manages settings.
"""

import secrets
import string
import os
import yaml
import argparse


def generate_api_key(length=32):
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits + "-_"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def load_config():
    """Load current configuration"""
    config_file = "config/defaults.yaml"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    return {}


def save_key_to_secrets_file(api_key):
    """Save API key to secrets file"""
    secrets_dir = "config"
    os.makedirs(secrets_dir, exist_ok=True)
    
    with open(os.path.join(secrets_dir, "secrets.ini"), 'w') as f:
        f.write(f"[prefect]\n")
        f.write(f"server_api_url = http://YOUR_PI_IP:4200/api\n\n")
        f.write(f"[hardware]\n")
        f.write(f"device = /dev/ttyUSB0\n")
        f.write(f"baudrate = 57600\n")
        f.write(f"motor_id = 1\n\n")
        f.write(f"[client]\n")
        f.write(f"default_host = YOUR_PI_IP\n")
        f.write(f"default_port = 4200\n")


def main():
    parser = argparse.ArgumentParser(description="Generate keys for Plate Resort")
    parser.add_argument("--length", type=int, default=32, 
                        help="Length of API key (default: 32)")
    parser.add_argument("--generate", action="store_true", 
                        help="Generate new configuration")
    
    args = parser.parse_args()
    
    if args.generate:
        # Generate new key (for future use if needed)
        new_key = generate_api_key(args.length)
        print(f"Generated key: {new_key}")
        
        save_key_to_secrets_file(new_key)
        print("✅ Created config/secrets.ini")
            
        print("\n📋 Usage:")
        print("1. Update config/secrets.ini with your Pi's IP address")
        print("2. Copy to your Pi for hardware access")
        
    else:
        # Default: just generate and show
        new_key = generate_api_key(args.length)
        print(f"Generated key: {new_key}")
        print("\nTo create config: python utils/keygen.py --generate")


if __name__ == "__main__":
    main()