#!/usr/bin/env python3
"""Test hashboard control with proper LuxOS session management"""

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

        request = json.dumps(cmd)
        sock.sendall(request.encode())

        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if b'\x00' in chunk:
                break

        sock.close()
        response_str = response.decode('utf-8', errors='ignore').rstrip('\x00')

        try:
            return json.loads(response_str)
        except:
            return {"error": response_str}

    except Exception as e:
        return {"error": str(e)}

def get_session_id():
    """Get or create a LuxOS session"""
    # Try to check existing session
    result = send_command("session")

    if "SESSION" in result and result["SESSION"]:
        session_info = result["SESSION"][0]
        session_id = session_info.get("SessionID", "")
        if session_id:
            print(f"✓ Found existing session: {session_id}")
            return session_id

    # Need to login
    print("No active session, logging in...")
    result = send_command("login", f"{USERNAME},{PASSWORD}")

    if "SESSION" in result and result["SESSION"]:
        session_info = result["SESSION"][0]
        session_id = session_info.get("SessionID", "")
        if session_id:
            print(f"✓ Created new session: {session_id}")
            return session_id

    print(f"✗ Failed to get session: {result}")
    return None

def check_board_status():
    """Check current hashboard status"""
    print("\n" + "="*60)
    print("CURRENT HASHBOARD STATUS")
    print("="*60)

    result = send_command("devs")

    if "DEVS" in result:
        for dev in result["DEVS"]:
            board_id = dev.get("ASC")
            status = dev.get("Status")
            is_shutdown = dev.get("IsUserShutdown", False)
            hashrate = dev.get("MHS 5s", 0) / 1000000  # Convert to TH/s
            temp = dev.get("Temperature", 0)
            connector = dev.get("Connector", "?")

            shutdown_str = " [USER SHUTDOWN]" if is_shutdown else ""
            print(f"Board {board_id} ({connector}): {status}{shutdown_str} - {hashrate:.2f} TH/s @ {temp}°C")

    return result

def disable_board(session_id, board_id):
    """Disable a specific hashboard"""
    print(f"\nAttempting to disable board {board_id}...")

    # The parameter format is: session_id,board_id
    parameter = f"{session_id},{board_id}"
    result = send_command("disableboard", parameter)

    if "STATUS" in result:
        status = result["STATUS"][0]
        if status.get("STATUS") == "S":
            print(f"✓ Board {board_id} disable command successful!")
            print(f"   Message: {status.get('Msg', 'OK')}")
            return True
        else:
            print(f"✗ Board {board_id} disable failed: {status.get('Msg', 'Unknown error')}")
            return False

    print(f"✗ Unexpected response: {result}")
    return False

def enable_board(session_id, board_id):
    """Enable a specific hashboard"""
    print(f"\nAttempting to enable board {board_id}...")

    parameter = f"{session_id},{board_id}"
    result = send_command("enableboard", parameter)

    if "STATUS" in result:
        status = result["STATUS"][0]
        if status.get("STATUS") == "S":
            print(f"✓ Board {board_id} enable command successful!")
            print(f"   Message: {status.get('Msg', 'OK')}")
            return True
        else:
            print(f"✗ Board {board_id} enable failed: {status.get('Msg', 'Unknown error')}")
            return False

    print(f"✗ Unexpected response: {result}")
    return False

if __name__ == "__main__":
    print("="*60)
    print("LUXOS HASHBOARD CONTROL TEST")
    print(f"Miner: {MINER_IP}")
    print("="*60)

    # Step 1: Check initial status
    check_board_status()

    # Step 2: Get session
    session_id = get_session_id()

    if not session_id:
        print("\n✗ Cannot proceed without valid session ID")
        exit(1)

    # Step 3: Test enabling board 0 (currently disabled)
    print("\n" + "="*60)
    print("TEST: Enable Board 0")
    print("="*60)

    if enable_board(session_id, 0):
        print("\nWaiting 10 seconds for board to start...")
        time.sleep(10)
        check_board_status()

    # Step 4: Test disabling board 2
    print("\n" + "="*60)
    print("TEST: Disable Board 2")
    print("="*60)

    if disable_board(session_id, 2):
        print("\nWaiting 5 seconds for board to stop...")
        time.sleep(5)
        check_board_status()

    # Step 5: Re-enable board 2
    print("\n" + "="*60)
    print("TEST: Re-enable Board 2")
    print("="*60)

    if enable_board(session_id, 2):
        print("\nWaiting 10 seconds for board to restart...")
        time.sleep(10)
        check_board_status()

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
