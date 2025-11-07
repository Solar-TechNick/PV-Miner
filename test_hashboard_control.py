#!/usr/bin/env python3
"""
Direct hashboard control test script for LuxOS API.
This bypasses Home Assistant to help diagnose hashboard switching issues.
"""
import asyncio
import sys
import logging

# Set up logging to see everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the custom_components path to sys.path
sys.path.insert(0, '/home/nick/ai/Sol-Miner/custom_components/pv_miner')

from luxos_api import LuxOSAPI, LuxOSAPIError

async def test_hashboard_control():
    """Test hashboard control directly."""
    # Replace these with your miner's actual credentials
    MINER_HOST = input("Enter miner IP address: ").strip()
    MINER_USERNAME = input("Enter miner username (default: admin): ").strip() or "admin"
    MINER_PASSWORD = input("Enter miner password: ").strip()

    print(f"\n{'='*60}")
    print(f"Testing hashboard control on {MINER_HOST}")
    print(f"{'='*60}\n")

    # Create API instance
    api = LuxOSAPI(MINER_HOST, MINER_USERNAME, MINER_PASSWORD)

    try:
        # Test 1: Basic connection
        print("1. Testing basic connection...")
        connected = await api.test_connection()
        if connected:
            print("   ✓ Connection successful\n")
        else:
            print("   ✗ Connection failed\n")
            return

        # Test 2: Get current status
        print("2. Getting miner status...")
        try:
            devs = await api.get_devs()
            if "DEVS" in devs:
                print(f"   Found {len(devs['DEVS'])} hashboards:")
                for i, board in enumerate(devs['DEVS']):
                    status = board.get('Status', 'Unknown')
                    enabled = board.get('Enabled', 'Unknown')
                    temp = board.get('Temperature', 'Unknown')
                    print(f"   - Board {i}: Status={status}, Enabled={enabled}, Temp={temp}°C")
            print()
        except Exception as e:
            print(f"   ✗ Failed to get device status: {e}\n")

        # Test 3: Check if miner is awake
        print("3. Checking miner state...")
        try:
            stats = await api.get_stats()
            if "STATS" in stats and len(stats["STATS"]) > 1:
                hashrate = stats["STATS"][1].get("GHS 5s", 0)
                print(f"   Current hashrate: {hashrate/1000:.2f} TH/s")
                if hashrate < 1000:
                    print("   ⚠ Miner appears to be in sleep/idle mode\n")
                else:
                    print("   ✓ Miner is active\n")
        except Exception as e:
            print(f"   ⚠ Could not check miner state: {e}\n")

        # Test 4: Wake up miner
        print("4. Ensuring miner is awake...")
        try:
            await api.resume_mining()
            print("   ✓ Miner wakeup command sent\n")
            await asyncio.sleep(2)  # Wait for miner to wake up
        except LuxOSAPIError as e:
            if "already active" in str(e).lower():
                print("   ✓ Miner is already active\n")
            else:
                print(f"   ⚠ Wakeup error (continuing anyway): {e}\n")

        # Test 5: Interactive hashboard control
        print("5. Hashboard control test")
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
            print("  q - Quit")

            choice = input("\nEnter choice: ").strip().lower()

            if choice == 'q':
                break
            elif choice == '7':
                devs = await api.get_devs()
                if "DEVS" in devs:
                    for i, board in enumerate(devs['DEVS']):
                        status = board.get('Status', 'Unknown')
                        enabled = board.get('Enabled', 'Unknown')
                        hashrate = board.get('MHS 5s', 0) / 1000000  # Convert to TH/s
                        print(f"Board {i}: Status={status}, Enabled={enabled}, Hashrate={hashrate:.2f} TH/s")
            elif choice in ['1', '2', '3', '4', '5', '6']:
                board_num = int(choice) - 1 if choice in ['1', '3', '5'] else int(choice) - 2
                action = 'enable' if choice in ['1', '3', '5'] else 'disable'

                print(f"\nAttempting to {action} hashboard {board_num}...")
                try:
                    if action == 'enable':
                        result = await api.enable_hashboard(board_num)
                    else:
                        result = await api.disable_hashboard(board_num)

                    print(f"✓ Command successful!")
                    print(f"Response: {result}")

                    # Wait a moment and check new status
                    await asyncio.sleep(1)
                    devs = await api.get_devs()
                    if "DEVS" in devs and len(devs['DEVS']) > board_num:
                        board = devs['DEVS'][board_num]
                        status = board.get('Status', 'Unknown')
                        enabled = board.get('Enabled', 'Unknown')
                        print(f"New state: Status={status}, Enabled={enabled}")

                except LuxOSAPIError as e:
                    print(f"✗ API Error: {e}")
                except Exception as e:
                    print(f"✗ Unexpected error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Invalid choice")

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await api.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    print("=== LuxOS Hashboard Control Diagnostic Tool ===\n")
    asyncio.run(test_hashboard_control())
