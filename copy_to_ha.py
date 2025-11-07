#!/usr/bin/env python3
"""Copy automation files to Home Assistant via SFTP"""

import os
import sys

try:
    import paramiko
except ImportError:
    print("Error: paramiko not installed. Trying alternative method...")
    print("\nPlease manually copy the files:")
    print("  automations/solar_power_control_full.yaml")
    print("  automations/README.md")
    print("\nTo: hassio@192.168.1.147:/config/automations/")
    print("\nOr install paramiko: pip3 install paramiko")
    sys.exit(1)

# Configuration
HOST = "192.168.1.147"
PORT = 22
USERNAME = "hassio"
PASSWORD = "hassio"
REMOTE_DIR = "/config/automations"

LOCAL_FILES = [
    ("automations/solar_power_control_full.yaml", "solar_power_control_full.yaml"),
    ("automations/README.md", "README.md"),
]

def copy_files():
    """Copy files to Home Assistant via SFTP"""
    print(f"Connecting to {HOST}...")

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect
        ssh.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD)
        print(f"✓ Connected to {HOST}")

        # Create SFTP client
        sftp = ssh.open_sftp()

        # Create remote directory if it doesn't exist
        try:
            sftp.stat(REMOTE_DIR)
        except FileNotFoundError:
            print(f"Creating directory {REMOTE_DIR}...")
            sftp.mkdir(REMOTE_DIR)

        # Copy files
        for local_file, remote_file in LOCAL_FILES:
            if not os.path.exists(local_file):
                print(f"✗ Local file not found: {local_file}")
                continue

            remote_path = f"{REMOTE_DIR}/{remote_file}"
            print(f"Copying {local_file} → {remote_path}...")
            sftp.put(local_file, remote_path)
            print(f"✓ Copied {remote_file}")

        sftp.close()
        ssh.close()

        print("\n=== Files copied successfully! ===")
        print(f"Files are now in {REMOTE_DIR}/ on Home Assistant")
        print("\nNext steps:")
        print("1. In Home Assistant, go to Settings → Automations & Scenes")
        print("2. Click 'Create Automation' → 'Create new automation' → 'Edit in YAML'")
        print(f"3. Copy the contents from {REMOTE_DIR}/solar_power_control_full.yaml")
        print("4. Or add 'automation: !include_dir_merge_list automations/' to configuration.yaml")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    copy_files()
