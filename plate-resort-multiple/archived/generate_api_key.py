#!/usr/bin/env python3
"""
API Key Generator for Plate Resort Server
Generates secure random API keys and manages configuration
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
    config_file = "resort_config.yaml"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    return {}


def update_config_api_key(new_key):
    """Update the API key in the config file"""
    config = load_config()
    
    # Ensure server section exists
    if 'server' not in config:
        config['server'] = {}
    
    config['server']['api_key'] = new_key
    
    # Write back to file
    with open("resort_config.yaml", 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def save_key_to_env_file(api_key):
    """Save API key to .env file for easy sourcing"""
    with open(".env", 'w') as f:
        f.write(f"PLATE_API_KEY={api_key}\n")
        f.write("# Source this file: source .env\n")
        f.write("# Or export manually: export PLATE_API_KEY=<key>\n")


def main():
    parser = argparse.ArgumentParser(description="Generate and manage API keys for Plate Resort")
    parser.add_argument("--length", type=int, default=32, help="Length of API key (default: 32)")
    parser.add_argument("--show", action="store_true", help="Show current API key")
    parser.add_argument("--generate", action="store_true", help="Generate new API key")
    parser.add_argument("--update-config", action="store_true", help="Update config file with new key")
    parser.add_argument("--create-env", action="store_true", help="Create .env file with API key")
    
    args = parser.parse_args()
    
    if args.show:
        config = load_config()
        current_key = config.get('server', {}).get('api_key', 'Not set')
        print(f"Current API key: {current_key}")
        return
    
    if args.generate or args.update_config:
        # Generate new key
        new_key = generate_api_key(args.length)
        print(f"Generated API key: {new_key}")
        
        if args.update_config:
            update_config_api_key(new_key)
            print("✅ Updated resort_config.yaml")
        
        if args.create_env:
            save_key_to_env_file(new_key)
            print("✅ Created .env file")
            
        print("\n📋 Usage:")
        print("1. Set as environment variable:")
        print(f"   export PLATE_API_KEY={new_key}")
        print("\n2. Or source the .env file:")
        print("   source .env")
        print("\n3. Use with client:")
        print(f"   python client/client.py --api-key {new_key} status")
        
    else:
        # Default: just generate and show
        new_key = generate_api_key(args.length)
        print(f"Generated API key: {new_key}")
        print("\nTo update config: python generate_api_key.py --generate --update-config")


if __name__ == "__main__":
    main()