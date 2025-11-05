#!/usr/bin/env python3
"""Test dynamic profile detection from miner."""
import asyncio
import sys
import os
import json

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_profile_discovery():
    """Test different methods to discover profiles dynamically."""
    host = "192.168.99.202"
    username = "root"
    password = "root"
    
    print(f"🔍 Testing dynamic profile discovery on {host}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Establishing connection...")
        connected = await api.test_connection()
        if not connected:
            print("❌ Cannot connect to miner!")
            return
        print(f"✅ Connected with session: {api._luxos_session_id}")
        
        print("\n2. Testing 'profilelist' command...")
        try:
            result = await api._execute_command("profilelist", "")
            print(f"✅ profilelist result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ profilelist failed: {e}")
            
        print("\n3. Testing 'profiles' command...")
        try:
            result = await api._execute_command("profiles", "")
            print(f"✅ profiles result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ profiles failed: {e}")
        
        print("\n4. Testing known profiles with 'profileget'...")
        known_profiles = ["default", "310MHz", "400MHz", "500MHz", "600MHz", "700MHz", "balanced", "eco", "max"]
        working_profiles = []
        
        for profile in known_profiles:
            try:
                result = await api._execute_command("profileget", profile)
                if "PROFILE" in result and result["PROFILE"]:
                    working_profiles.append(profile)
                    profile_data = result["PROFILE"][0]
                    print(f"✅ {profile}: {profile_data}")
                else:
                    print(f"❌ {profile}: No data")
            except Exception as e:
                print(f"❌ {profile}: Error - {e}")
        
        print(f"\n📋 Working profiles found: {working_profiles}")
        
        print("\n5. Testing current profile detection...")
        try:
            result = await api._execute_command("profilecurrent", "")
            print(f"✅ profilecurrent result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ profilecurrent failed: {e}")
        
        print("\n6. Testing stats for profile information...")
        try:
            result = await api.get_stats()
            if "STATS" in result:
                stats = result["STATS"]
                if len(stats) > 1:
                    miner_stats = stats[1]
                    print("📊 Current miner stats (might contain profile info):")
                    for key, value in miner_stats.items():
                        if any(keyword in key.lower() for keyword in ['profile', 'freq', 'volt', 'power']):
                            print(f"  {key}: {value}")
        except Exception as e:
            print(f"❌ stats check failed: {e}")
            
        print("\n✅ Profile discovery test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_profile_discovery())