#!/usr/bin/env python3
"""Test the LuxOS API directly."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_api():
    """Test the LuxOS API."""
    host = "192.168.1.212"
    username = "root"
    password = "root"
    
    print(f"Testing LuxOS API connection to {host}")
    print(f"Credentials: {username}:{password}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Testing connection...")
        connected = await api.test_connection()
        print(f"Connection result: {connected}")
        
        if connected:
            print("\n2. Testing stats...")
            try:
                stats = await api.get_stats()
                print(f"Stats result: {stats}")
            except Exception as e:
                print(f"Stats error: {e}")
            
            print("\n3. Testing devices...")  
            try:
                devs = await api.get_devs()
                print(f"Devices result: {devs}")
            except Exception as e:
                print(f"Devices error: {e}")
                
            print("\n4. Testing pools...")
            try:
                pools = await api.get_pools()
                print(f"Pools result: {pools}")
            except Exception as e:
                print(f"Pools error: {e}")
        
    except Exception as e:
        print(f"API test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_api())