#!/usr/bin/env python3
"""Test stopping ATM to enable hashboard control"""

import json
import socket
import time

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
print("Testing board control without ATM")
print("="*60)

# Check initial status
check_board_status()

# Try ascdisable/ascenable commands (standard CGMiner commands)
print("\n" + "="*60)
print("Trying standard CGMiner commands (ascdisable/ascenable)")
print("="*60)

print("\nTest 1: ascdisable 2")
result = send_command("ascdisable", "2")
print(f"Result: {result.get('STATUS', [{}])[0].get('Msg', 'No message')}")
time.sleep(2)
check_board_status()

print("\nTest 2: ascenable 0")
result = send_command("ascenable", "0")
print(f"Result: {result.get('STATUS', [{}])[0].get('Msg', 'No message')}")
time.sleep(2)
check_board_status()

# Try ascset commands
print("\n" + "="*60)
print("Trying ascset command")
print("="*60)

print("\nTest 3: ascset 0,enable")
result = send_command("ascset", "0,enable")
print(f"Result: {result.get('STATUS', [{}])[0].get('Msg', 'No message')}")
time.sleep(2)
check_board_status()

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
