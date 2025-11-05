#!/usr/bin/env python3
"""Test stopping ATM and controlling hashboards"""

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
print("Testing ATM Stop and Hashboard Control")
print("="*60)

# Step 1: Login
result = send_command("logon", f"{USERNAME},{PASSWORD}")
session_id = None
if "SESSION" in result and result["SESSION"]:
    session_id = result["SESSION"][0].get("SessionID", "")
    print(f"✓ Login successful! Session ID: {session_id}\n")

if not session_id:
    print("✗ Login failed")
    exit(1)

# Step 2: Check initial status
check_board_status()

# Step 3: Try to stop ATM
print("\n" + "="*60)
print("Step 1: Stopping ATM")
print("="*60)

# Try atmset with session_id,disabled
parameter = f"{session_id},disabled"
result = send_command("atmset", parameter)

if "STATUS" in result:
    status = result["STATUS"][0]
    print(f"ATM Stop - Status: {status.get('STATUS')} - {status.get('Msg')}")

    if status.get("STATUS") == "S":
        print("✓ ATM stopped successfully!")
        print("Waiting 5 seconds...")
        time.sleep(5)
    else:
        print(f"✗ ATM stop failed: {status.get('Msg')}")
        print("\nTrying alternative commands...")

        # Try other possible commands
        for cmd in ["atmpause", "atmstop", "atmdisable"]:
            print(f"\nTrying: {cmd}")
            result2 = send_command(cmd, session_id)
            if "STATUS" in result2:
                status2 = result2["STATUS"][0]
                print(f"  Status: {status2.get('STATUS')} - {status2.get('Msg')}")

# Step 4: Now try to enable board 0
print("\n" + "="*60)
print("Step 2: Enable Board 0 (with ATM stopped)")
print("="*60)

parameter = f"{session_id},{0}"
result = send_command("enableboard", parameter)

if "STATUS" in result:
    status = result["STATUS"][0]
    print(f"Status: {status.get('STATUS')} - {status.get('Msg')}")

    if status.get("STATUS") == "S":
        print("✓ Board 0 enable successful!")
        time.sleep(10)
        check_board_status()
    else:
        print(f"✗ Board 0 enable failed: {status.get('Msg')}")

# Step 5: Re-enable ATM
print("\n" + "="*60)
print("Step 3: Re-enabling ATM")
print("="*60)

parameter = f"{session_id},enabled"
result = send_command("atmset", parameter)

if "STATUS" in result:
    status = result["STATUS"][0]
    print(f"Status: {status.get('STATUS')} - {status.get('Msg')}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
check_board_status()
