#!/usr/bin/env python3
"""Test profile commands to understand the correct format."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_profiles():
    """Test profile commands."""
    host = "192.168.1.212"
    
    api = LuxOSAPI(host)
    
    try:
        # Get session
        await api.test_connection()
        await api.login()
        session_id = api._luxos_session_id
        
        print(f"Session ID: {session_id}")
        
        print("\n1. Try to find out what profiles exist...")
        
        # Try different approaches to get profiles
        profile_attempts = [
            ("profileget", "all"),
            ("profileget", "*"),
            ("profileget", "list"),
            ("profileget", "0"),
            ("profileget", "1"),
            ("profileget", "default"),
            ("profileget", "eco"),
            ("profileget", "balanced"),
            ("profileget", "max"),
        ]
        
        working_profiles = []
        
        for cmd, param in profile_attempts:
            try:
                print(f"\nTrying {cmd} with '{param}'...")
                result = await api._execute_command(cmd, param)
                print(f"SUCCESS: {result}")
                working_profiles.append(param)
            except Exception as e:
                print(f"FAILED: {e}")
        
        print(f"\nWorking profiles found: {working_profiles}")
        
        print("\n2. Try profilenew to see what parameters it expects...")
        try:
            result = await api._execute_command("profilenew", "")
            print(f"Profilenew empty result: {result}")
        except Exception as e:
            print(f"Profilenew empty failed: {e}")
        
        print("\n3. Check what the 'devs' command shows for profiles...")
        try:
            devs_result = await api._execute_command("devs", "")
            if "DEVS" in devs_result:
                for dev in devs_result["DEVS"]:
                    if "Profile" in dev:
                        print(f"Device {dev['ASC']} profile: {dev['Profile']}")
        except Exception as e:
            print(f"Devs check failed: {e}")
        
        print("\n4. Check stats for profile info...")
        try:
            stats_result = await api._execute_command("stats", "")
            print("Looking for profile info in stats...")
            if "STATS" in stats_result:
                for stat in stats_result["STATS"]:
                    for key, value in stat.items():
                        if "profile" in str(key).lower() or "mode" in str(key).lower():
                            print(f"  {key}: {value}")
        except Exception as e:
            print(f"Stats check failed: {e}")
            
        print("\n5. Try limits command to see available profiles...")
        try:
            limits_result = await api._execute_command("limits", "")
            print(f"Limits result: {limits_result}")
        except Exception as e:
            print(f"Limits failed: {e}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_profiles())