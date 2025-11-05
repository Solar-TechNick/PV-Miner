#!/usr/bin/env python3
"""Debug what sensor data we're actually getting."""
import asyncio
import sys
import os
import json

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def debug_sensor_data():
    """Debug the actual sensor data structure."""
    host = "192.168.1.212"
    
    api = LuxOSAPI(host)
    
    try:
        # Get session
        await api.test_connection()
        
        print("=== DEBUGGING SENSOR DATA STRUCTURE ===\n")
        
        # Get all the data that the coordinator would get
        print("1. STATS DATA:")
        stats = await api.get_stats()
        print(json.dumps(stats, indent=2))
        
        print("\n" + "="*50 + "\n")
        
        print("2. DEVS DATA:")
        devs = await api.get_devs()
        print(json.dumps(devs, indent=2))
        
        print("\n" + "="*50 + "\n")
        
        print("3. POOLS DATA:")
        pools = await api.get_pools()
        print(json.dumps(pools, indent=2))
        
        print("\n" + "="*50 + "\n")
        
        print("4. CHECKING FOR POWER COMMAND:")
        try:
            power = await api._execute_command("power", "")
            print("POWER DATA:")
            print(json.dumps(power, indent=2))
        except Exception as e:
            print(f"Power command failed: {e}")
        
        print("\n" + "="*50 + "\n")
        
        print("5. CHECKING FOR TEMPS COMMAND:")
        try:
            temps = await api._execute_command("temps", "")
            print("TEMPS DATA:")
            print(json.dumps(temps, indent=2))
        except Exception as e:
            print(f"Temps command failed: {e}")
        
        print("\n" + "="*50 + "\n")
        
        print("6. CHECKING FOR FANS COMMAND:")
        try:
            fans = await api._execute_command("fans", "")
            print("FANS DATA:")
            print(json.dumps(fans, indent=2))
        except Exception as e:
            print(f"Fans command failed: {e}")
        
        print("\n" + "="*50 + "\n")
        
        print("7. EXTRACTING SPECIFIC SENSOR VALUES:")
        print(f"From STATS:")
        if "STATS" in stats and len(stats["STATS"]) > 1:
            miner_stats = stats["STATS"][1]
            print(f"  - GHS 5s (hashrate): {miner_stats.get('GHS 5s', 'NOT FOUND')}")
            print(f"  - temp_max: {miner_stats.get('temp_max', 'NOT FOUND')}")
            print(f"  - fan1: {miner_stats.get('fan1', 'NOT FOUND')}")
            print(f"  - total rate: {miner_stats.get('total rate', 'NOT FOUND')}")
            print(f"  - Elapsed: {miner_stats.get('Elapsed', 'NOT FOUND')}")
            print(f"  - Power (looking for power field): {miner_stats.get('Power', 'NOT FOUND')}")
            
            print(f"\n  All available fields in miner stats:")
            for key in sorted(miner_stats.keys()):
                print(f"    {key}: {miner_stats[key]}")
        
        print(f"\nFrom DEVS (for temperatures):")
        if "DEVS" in devs:
            for i, dev in enumerate(devs["DEVS"]):
                print(f"  Device {i} (ASC {dev.get('ASC')}):")
                print(f"    - Temperature: {dev.get('Temperature', 'NOT FOUND')}")
                print(f"    - MHS av: {dev.get('MHS av', 'NOT FOUND')}")
        
    except Exception as e:
        print(f"Debug failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(debug_sensor_data())