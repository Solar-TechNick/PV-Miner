#!/usr/bin/env python3
"""
Simple synchronous hashboard control test using only standard library.
This bypasses Home Assistant to help diagnose hashboard switching issues.
"""
import socket
import json
import time

def send_luxos_command(host, command, parameter=""):
    """Send a command to LuxOS miner via TCP port 4028."""
    try:
        # Create the command JSON
        cmd = {"command": command}
        if parameter:
            cmd["parameter"] = parameter

        message = json.dumps(cmd)

        # Connect to miner
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, 4028))

        # Send command
        sock.sendall(message.encode('utf-8'))

        # Receive response
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            # LuxOS responses end with \x00
            if b'\x00' in response:
                break

        sock.close()

        # Parse response (remove null byte and parse JSON)
        response_str = response.decode('utf-8').rstrip('\x00')
        return json.loads(response_str)

    except Exception as e:
        return {"error": str(e)}

def get_session_id(host, username, password):
    """Get LuxOS session ID for authenticated commands."""
    # Try newer 'session' command first
    result = send_luxos_command(host, "session", f"{username},{password}")

    if "SESSION" in result and result["SESSION"]:
        session_info = result["SESSION"][0]
        # Try both "SessionID" and "Session ID" for compatibility
        session_id = session_info.get("SessionID") or session_info.get("Session ID")
        if session_id:
            print(f"✓ Login successful (session command), session ID: {session_id}")
            return session_id

    # Try older 'logon' command
    result = send_luxos_command(host, "logon", f"{username},{password}")

    if "SESSION" in result and result["SESSION"]:
        session_info = result["SESSION"][0]
        session_id = session_info.get("SessionID") or session_info.get("Session ID")
        if session_id:
            print(f"✓ Login successful (logon command), session ID: {session_id}")
            return session_id

    print(f"✗ Login failed: {result}")
    print(f"   Trying to continue without session ID (some commands may work)")
    return "0"  # Return dummy session ID to allow testing

def display_devs(devs_result):
    """Display device (hashboard) information."""
    if "DEVS" in devs_result:
        print(f"\nFound {len(devs_result['DEVS'])} hashboards:")
        for i, board in enumerate(devs_result['DEVS']):
            status = board.get('Status', 'Unknown')
            enabled = board.get('Enabled', 'Unknown')
            temp = board.get('Temperature', 'Unknown')
            hashrate = board.get('MHS 5s', 0) / 1000000  # Convert to TH/s
            print(f"  Board {i}: Status={status}, Enabled={enabled}, Temp={temp}°C, Hashrate={hashrate:.2f} TH/s")
    else:
        print(f"No device info: {devs_result}")

def main():
    """Main diagnostic function."""
    print("=== LuxOS Hashboard Control Diagnostic Tool (Simple) ===\n")

    MINER_HOST = "192.168.1.210"
    MINER_USERNAME = "root"
    MINER_PASSWORD = "root"

    print(f"Testing hashboard control on {MINER_HOST}")
    print(f"{'='*60}\n")

    # Test 1: Basic connection
    print("1. Testing basic connection...")
    version = send_luxos_command(MINER_HOST, "version")
    if "error" in version:
        print(f"   ✗ Connection failed: {version['error']}\n")
        return
    else:
        print(f"   ✓ Connection successful")
        if "VERSION" in version and version["VERSION"]:
            ver_info = version["VERSION"][0]
            print(f"   Miner: {ver_info.get('Type', 'Unknown')}")
            print(f"   LuxOS: {ver_info.get('LUXminer', 'Unknown')}\n")

    # Test 2: Get session ID
    print("2. Getting session ID...")
    session_id = get_session_id(MINER_HOST, MINER_USERNAME, MINER_PASSWORD)
    if not session_id:
        print("   ✗ Failed to get session ID\n")
        return
    print()

    # Test 3: Get current status
    print("3. Getting miner status...")
    devs = send_luxos_command(MINER_HOST, "devs")
    display_devs(devs)
    print()

    # Test 4: Check miner state
    print("4. Checking miner state...")
    stats = send_luxos_command(MINER_HOST, "stats")
    if "STATS" in stats and len(stats["STATS"]) > 1:
        hashrate = stats["STATS"][1].get("GHS 5s", 0)
        print(f"   Current total hashrate: {hashrate/1000:.2f} TH/s")
        if hashrate < 1000:
            print("   ⚠ Miner appears to be in sleep/idle mode")
        else:
            print("   ✓ Miner is active")
    print()

    # Test 5: Check ATM status
    print("5. Checking ATM (Automatic Tuning Mode) status...")
    atm_status = send_luxos_command(MINER_HOST, "atm")
    if "ATM" in atm_status and atm_status["ATM"]:
        atm_info = atm_status["ATM"][0]
        enabled = atm_info.get("Enabled", "Unknown")
        print(f"   ATM Enabled: {enabled}")
        if enabled:
            print("   ℹ ATM must be disabled temporarily to control hashboards")
    print()

    # Test 6: Interactive hashboard control
    print("6. Hashboard Control Test")
    print(f"{'='*60}")

    while True:
        print("\nOptions:")
        print("  1 - Enable hashboard 0")
        print("  2 - Disable hashboard 0")
        print("  3 - Enable hashboard 1")
        print("  4 - Disable hashboard 1")
        print("  5 - Enable hashboard 2")
        print("  6 - Disable hashboard 2")
        print("  7 - Get current status")
        print("  8 - Test resume/wakeup")
        print("  q - Quit")

        choice = input("\nEnter choice: ").strip().lower()

        if choice == 'q':
            break
        elif choice == '7':
            devs = send_luxos_command(MINER_HOST, "devs")
            display_devs(devs)
        elif choice == '8':
            print("\nTesting curtail wakeup command...")
            result = send_luxos_command(MINER_HOST, "curtail", f"{session_id},wakeup")
            print(f"Response: {result}")
        elif choice in ['1', '2', '3', '4', '5', '6']:
            # Parse board number and action
            if choice in ['1', '3', '5']:
                board_num = (int(choice) - 1) // 2
                action = 'enable'
                command = 'enableboard'
            else:
                board_num = (int(choice) - 2) // 2
                action = 'disable'
                command = 'disableboard'

            print(f"\n{'='*60}")
            print(f"Attempting to {action} hashboard {board_num}...")
            print(f"{'='*60}")

            # Step 1: Disable ATM
            print("\nStep 1: Disabling ATM...")
            atm_disable = send_luxos_command(MINER_HOST, "atmset", f"{session_id},enabled=false")
            print(f"Response: {atm_disable}")

            if "STATUS" in atm_disable and atm_disable["STATUS"]:
                status = atm_disable["STATUS"][0]
                if status.get("STATUS") == "S":
                    print("✓ ATM disabled successfully")
                else:
                    print(f"⚠ ATM disable warning: {status.get('Msg')}")

            time.sleep(0.5)

            # Step 2: Execute hashboard command
            print(f"\nStep 2: Executing {command} for board {board_num}...")
            board_result = send_luxos_command(MINER_HOST, command, f"{session_id},{board_num}")
            print(f"Response: {board_result}")

            if "STATUS" in board_result and board_result["STATUS"]:
                status = board_result["STATUS"][0]
                if status.get("STATUS") == "S":
                    print(f"✓ {command} successful!")
                else:
                    print(f"✗ {command} failed: {status.get('Msg')}")

            time.sleep(0.5)

            # Step 3: Re-enable ATM
            print("\nStep 3: Re-enabling ATM...")
            atm_enable = send_luxos_command(MINER_HOST, "atmset", f"{session_id},enabled=true")
            print(f"Response: {atm_enable}")

            if "STATUS" in atm_enable and atm_enable["STATUS"]:
                status = atm_enable["STATUS"][0]
                if status.get("STATUS") == "S":
                    print("✓ ATM re-enabled successfully")
                else:
                    print(f"⚠ ATM re-enable warning: {status.get('Msg')}")

            # Step 4: Check new status
            print("\nStep 4: Checking new status...")
            time.sleep(1)
            devs = send_luxos_command(MINER_HOST, "devs")
            display_devs(devs)

        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
