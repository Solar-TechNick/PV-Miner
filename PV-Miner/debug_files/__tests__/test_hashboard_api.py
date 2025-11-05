#!/usr/bin/env python3
"""Test the updated hashboard API methods."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_hashboard_api():
    """Test hashboard enable/disable methods."""
    host = "192.168.1.212"
    username = "root"
    password = "root"
    
    print(f"Testing updated hashboard API methods on {host}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Testing connection and session setup...")
        connected = await api.test_connection()
        print(f"Connection result: {connected}")
        
        if not connected:
            print("Connection failed, exiting...")
            return
        
        print(f"Session ID: {api._luxos_session_id}")
        
        print("\n2. Testing enable_hashboard method...")
        try:
            result = await api.enable_hashboard(0)
            print(f"Enable hashboard 0: SUCCESS")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Enable hashboard 0: ERROR - {e}")
        
        print("\n3. Testing disable_hashboard method...")
        try:
            result = await api.disable_hashboard(0)
            print(f"Disable hashboard 0: SUCCESS")
            print(f"Result: {result}")
            
            # Re-enable immediately
            print("Re-enabling hashboard 0...")
            result = await api.enable_hashboard(0)
            print(f"Re-enable hashboard 0: SUCCESS")
            
        except Exception as e:
            print(f"Disable hashboard 0: ERROR - {e}")
        
        print("\n4. Testing all hashboards...")
        for board_id in [0, 1, 2]:
            try:
                print(f"\nTesting hashboard {board_id}...")
                result = await api.enable_hashboard(board_id)
                print(f"  Enable: SUCCESS")
            except Exception as e:
                print(f"  Enable: ERROR - {e}")
        
        print("\nHashboard API tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_hashboard_api())