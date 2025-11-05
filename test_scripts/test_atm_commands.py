#!/usr/bin/env python3
"""Test ATM commands to find session management"""

import json
import socket

MINER_IP = "192.168.1.210"

def send_command(command, parameter=""):
    """Send command to CGMiner API"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((MINER_IP, 4028))

        if parameter:
            cmd = {"command": command, "parameter": parameter}
        else:
            cmd = {"command": command}

        sock.sendall(json.dumps(cmd).encode())

        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if b'\x00' in chunk:
                break

        sock.close()
        return json.loads(response.decode('utf-8', errors='ignore').rstrip('\x00'))

    except Exception as e:
        return {"error": str(e)}

print("Testing various ATM commands...\n")

# Test different ATM commands
commands_to_test = [
    ("help", ""),
    ("atmset", ""),
    ("atmset", "enabled"),
    ("atmset", "disabled"),
    ("enableboard", "0"),  # Try without session
    ("disableboard", "2"),  # Try without session
]

for cmd, param in commands_to_test:
    print(f"\n{'='*60}")
    print(f"Command: {cmd} {param}")
    print('='*60)

    result = send_command(cmd, param)

    if "STATUS" in result:
        status = result["STATUS"][0]
        print(f"Status: {status.get('STATUS')} - {status.get('Msg')}")

        # Print any additional data
        for key in result:
            if key != "STATUS" and key != "id":
                print(f"\n{key}:")
                print(json.dumps(result[key], indent=2)[:500])
    else:
        print(json.dumps(result, indent=2)[:500])
