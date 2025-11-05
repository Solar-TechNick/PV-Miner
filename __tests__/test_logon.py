#!/usr/bin/env python3
"""Test LuxOS logon and hashboard control"""

import json
import socket
import time

MINER_IP = "192.168.1.210"
USERNAME = "admin"
PASSWORD = "admin"

def send_command(command, parameter=""):
    """Send command to CGMiner API"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
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

def check_board_status():
    """Check current hashboard status"""
    result = send_command("devs")

    if "DEVS" in result:
        print("\nCurrent boards:")
        for dev in result["DEVS"]:
            board_id = dev.get("ASC")
            status = dev.get("Status")
            is_shutdown = dev.get("IsUserShutdown", False)
            hashrate = dev.get("MHS 5s", 0) / 1000000

            shutdown_str = " [SHUTDOWN]" if is_shutdown else ""
            print(f"  Board {board_id}: {status}{shutdown_str} - {hashrate:.2f} TH/s")

print("="*60)
print("Testing LuxOS Logon and Hashboard Control")
print("="*60)

# Step 1: Check initial status
check_board_status()

# Step 2: Try logon (not login)
print("\n" + "="*60)
print("Step 1: Logging in with 'logon' command")
print("="*60)

result = send_command("logon", f"{USERNAME},{PASSWORD}")
print(f"Logon result: {json.dumps(result, indent=2)[:500]}")

session_id = None
if "SESSION" in result and result["SESSION"]:
    session_info = result["SESSION"][0]
    session_id = session_info.get("SessionID", "")
    if session_id:
        print(f"\n✓ Login successful! Session ID: {session_id}")
    else:
        print("\n✗ Login succeeded but no session ID")
        exit(1)
else:
    print("\n✗ Login failed")
    exit(1)

# Step 3: Try to enable board 0 with session
print("\n" + "="*60)
print("Step 2: Enable Board 0")
print("="*60)

parameter = f"{session_id},{0}"
result = send_command("enableboard", parameter)

if "STATUS" in result:
    status = result["STATUS"][0]
    print(f"Status: {status.get('STATUS')} - {status.get('Msg')}")

    if status.get("STATUS") == "S":
        print("✓ Board 0 enable command successful!")
        time.sleep(10)
        check_board_status()
    else:
        print(f"✗ Board 0 enable failed: {status.get('Msg')}")
else:
    print(f"✗ Unexpected response: {result}")

# Step 4: Try to disable board 2 with session
print("\n" + "="*60)
print("Step 3: Disable Board 2")
print("="*60)

parameter = f"{session_id},{2}"
result = send_command("disableboard", parameter)

if "STATUS" in result:
    status = result["STATUS"][0]
    print(f"Status: {status.get('STATUS')} - {status.get('Msg')}")

    if status.get("STATUS") == "S":
        print("✓ Board 2 disable command successful!")
        time.sleep(5)
        check_board_status()
    else:
        print(f"✗ Board 2 disable failed: {status.get('Msg')}")
else:
    print(f"✗ Unexpected response: {result}")

# Step 5: Re-enable board 2
print("\n" + "="*60)
print("Step 4: Re-enable Board 2")
print("="*60)

parameter = f"{session_id},{2}"
result = send_command("enableboard", parameter)

if "STATUS" in result:
    status = result["STATUS"][0]
    print(f"Status: {status.get('STATUS')} - {status.get('Msg')}")

    if status.get("STATUS") == "S":
        print("✓ Board 2 enable command successful!")
        time.sleep(10)
        check_board_status()
    else:
        print(f"✗ Board 2 enable failed: {status.get('Msg')}")
else:
    print(f"✗ Unexpected response: {result}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
